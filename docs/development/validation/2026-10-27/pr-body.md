## Plugin information

- **Author**: browser-act
- **Plugin name**: browseract
- **Version**: 1.0.0
- **Source repository**: https://github.com/browser-act/dify-browser-act-plugin
- **Contact**: service@browseract.com

## Submission type

- [x] New plugin
- [ ] Version update

## What changed

Initial release. Adds two tools, Run My Bot and Run Official Template, that
start a BrowserAct task and return its result inside the node.

## Risk level

- [ ] Low risk
- [ ] Medium risk
- [x] High risk

## Required checks

- [x] I have read and followed the Marketplace submission requirements.
- [x] I have read and comply with the Plugin Development Guidelines.
- [x] I tested this plugin on Dify Cloud; limitations are listed in Reviewer notes.
- [x] The package contains only files needed at runtime.
- [x] The package does not contain secrets or development artifacts.
- [x] The package does not contain executables or bundled binaries.
- [x] The README includes setup, usage, credentials, connection requirements and the source repository.
- [x] The plugin includes PRIVACY.md and manifest.yaml references it.
- [x] All user-facing text is in English.

## Security and privacy notes

Browser automation: the plugin sends the user's BrowserAct API Key to
api.browseract.com and starts a Bot that runs in BrowserAct's hosted service.
Task inputs and outputs pass through that service. The plugin does not accept a
custom host, does not follow redirects, and redacts the API Key from errors.

## Local validation

    python validator/validate-difypkg.py browseract-1.0.0.difypkg --output-dir report
    exit code 0, no blocking findings.

## Reviewer notes

Tested on Dify Cloud with both tools. The node wait timeout defaults to 600
seconds; on timeout the node fails and keeps task_id, and the remote task is not
cancelled by the plugin.
