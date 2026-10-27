"""Build a fixed-host Test03 package without changing production source files."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

import yaml


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    output = args.output.resolve()
    if output.exists():
        parser.error("Output already exists; use a new package filename.")
    cli = root / ".tools" / "dify.exe"
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ba-test03-") as temporary:
        temporary = Path(temporary)
        source = temporary / "source.difypkg"
        subprocess.run([str(cli), "plugin", "package", str(root), "-o", str(source)], check=True)
        staging = temporary / "plugin"
        with zipfile.ZipFile(source) as archive:
            source_names = set(archive.namelist())
            archive.extractall(staging)
        client_path = staging / "browseract" / "client.py"
        client = client_path.read_text(encoding="utf-8")
        production = '"https://api.browseract.com"'
        assert client.count(production) == 1, "Review the API host before packaging"
        client_path.write_text(client.replace(production, '"https://api-test03.browseract.com"'), encoding="utf-8")
        manifest_path = staging / "manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        # PyYAML parses timestamps as datetime; the CLI requires RFC3339 text.
        if hasattr(manifest["created_at"], "isoformat"):
            manifest["created_at"] = manifest["created_at"].isoformat().replace("+00:00", "Z")
        # Dify's dynamic selectors can cache credentials by provider identity.
        # Keep test and production identities separate as well as their hosts.
        manifest["name"] = "browseract_test03"
        manifest["label"] = {"en_US": "BrowserAct (Test03)", "zh_Hans": "BrowserAct (Test03)"}
        manifest["description"] = {locale: "Test03 only: run published BrowserAct Bots and official templates."
                                   for locale in ("en_US", "zh_Hans")}
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        provider_path = staging / "provider" / "browseract.yaml"
        provider = yaml.safe_load(provider_path.read_text(encoding="utf-8"))
        provider["identity"]["name"] = manifest["name"]
        provider["identity"]["label"] = dict(manifest["label"])
        provider_path.write_text(yaml.safe_dump(provider, sort_keys=False), encoding="utf-8")
        privacy_path = staging / "PRIVACY.md"
        privacy_path.write_text(privacy_path.read_text(encoding="utf-8").replace(
            "host api.browseract.com.", "host api-test03.browseract.com (this Test03 build)."
        ), encoding="utf-8")
        readme = staging / "README.md"
        readme.write_text("# Test03 build\n\nThis package sends all API calls to https://api-test03.browseract.com. "
                          "Use a Test03 API Key. It is labeled BrowserAct (Test03). "
                          "Its plugin ID is " + manifest["author"] + "/" + manifest["name"] + ". Add new tool nodes from this provider; "
                          "existing browseract nodes retain their old provider.\n\n" +
                          readme.read_text(encoding="utf-8"), encoding="utf-8")
        subprocess.run([str(cli), "plugin", "package", str(staging), "-o", str(output)], check=True)
        with zipfile.ZipFile(output) as archive:
            assert archive.testzip() is None
            entries = {name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()}
            assert set(entries) == source_names
            for name in entries:
                assert archive.read(name) == (staging / name).read_bytes(), name
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(digest + "  " + output.name + "\n", encoding="utf-8")
    receipt = {"source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
               "source_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True)),
               "version": manifest["version"], "api_host": "https://api-test03.browseract.com",
               "plugin_id": manifest["author"] + "/" + manifest["name"],
               "provider_name": provider["identity"]["name"],
               "channel_header": "api-channel-ak: difyak", "package": str(output),
               "sha256": digest, "bytes": output.stat().st_size, "entries": entries,
               "build_overrides": ["browseract/client.py", "manifest.yaml", "provider/browseract.yaml", "README.md", "PRIVACY.md"]}
    output.with_suffix(output.suffix + ".build.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in receipt.items() if key != "entries"}))


if __name__ == "__main__":
    main()
