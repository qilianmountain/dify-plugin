## Local DIFYPKG Validation Summary

- Report directory: C:\Users\Administrator\Documents\Codex\2026-10-27\work\report7
- Blocking failures: 0
- Warning categories: 6
- Environment/check execution failures: 0

| Check | Type | Status | Findings |
|---|---|---|---|
| `package_contents` | blocking | PASS | No findings. |
| `package_secrets` | blocking | PASS | requirements.txt:95 review possible secret field `tiktoken` |
| `package_binaries` | blocking | PASS | .difyignore: has executable permission |
| `manifest_metadata` | blocking | PASS | missing recommended field: meta.minimum_dify_version |
| `readme_metadata` | blocking | PASS | No findings. |
| `package_dependencies` | blocking | PASS | No findings. |
| `python_compile` | blocking | PASS | No findings. |
| `python_safety` | warning | PASS | browseract/client.py:26: return value may expose credential-like values: return message.replace(self._api_key, "[REDACTED]") |
| `prohibited_financial_activity` | warning | PASS | No findings. |
| `access_domains` | warning | PASS | detected 1 outbound domain(s) by static scan: |
| `dependency_vulnerabilities` | warning | PASS | dependency source: uv.lock (49 pinned, 0 unpinned) |
| `sensitive_capabilities` | blocking | PASS | No findings. |

### Skipped checks
- PR title/body language and template checks require GitHub PR metadata
- Marketplace duplicate-version check requires Marketplace/PR workflow context
- plugin install and upload-package tests are not run by this local validator

### Warnings for review
- package_secrets:
  - requirements.txt:95 review possible secret field `tiktoken`
- package_binaries:
  - .difyignore: has executable permission
  - .python-version: has executable permission
  - LICENSE: has executable permission
  - main.py: has executable permission
  - manifest.yaml: has executable permission
  - PRIVACY.md: has executable permission
  - pyproject.toml: has executable permission
  - README.md: has executable permission
  - requirements.txt: has executable permission
  - uv.lock: has executable permission
  - ... 16 more
- manifest_metadata:
  - missing recommended field: meta.minimum_dify_version
- python_safety:
  - browseract/client.py:26: return value may expose credential-like values: return message.replace(self._api_key, "[REDACTED]")
  - tools/run_my_bot.py:20: return value may expose credential-like values: return option_cache.get( self.runtime.credentials["api_key"], self.runtime.user_id, "my_bot:bot_id", lambda: parameter_options(client.list_bots(), "bot_id"), )
  - tools/run_official_template.py:20: return value may expose credential-like values: return option_cache.get( self.runtime.credentials["api_key"], self.runtime.user_id, "official_template:" + parameter, lambda: parameter_options(client.list_templates(), "template_i
- access_domains:
  - detected 1 outbound domain(s) by static scan:
  -   api.browseract.com [domain] (browseract/client.py:32)
- dependency_vulnerabilities:
  - dependency source: uv.lock (49 pinned, 0 unpinned)
  - no known vulnerabilities in the pinned dependency set
