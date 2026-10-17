# Security policy

## Reporting a vulnerability

Please **do not open a public issue** for a security problem. Report it privately in either way:

- GitHub: the **Security** tab of this repository, then **Report a vulnerability**
  (private vulnerability reporting).
- Email: [n.opal@unit42.fr](mailto:n.opal@unit42.fr?subject=Video%20Studio%20security%20report).

Include what you found, how to reproduce it, and which script is affected. I will acknowledge a
report within a few days and tell you what I plan to do about it. This is a one-person project,
so these are best-effort timelines, not guarantees.

## Scope

In scope: the Python scripts and `Restore.bat` in this repository, for example a file name that
makes a script run an unintended command or write outside the folders it works in.

Out of scope: the programs the scripts call (FFmpeg, realesrgan-ncnn-vulkan, MKVToolNix) and the
Real-ESRGAN models. Please report those to their own projects.

## Supported versions

Only the latest release and the current `main` branch are supported.

## What the repository contains

No secrets, and the tools make no network requests. If you ever find a credential in this
repository or its history, that is a vulnerability: please report it as above.
