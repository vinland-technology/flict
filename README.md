<!--
SPDX-FileCopyrightText: 2020 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

![flict graphics](./logos/flict-logo-256-256.png)
&nbsp;

[![REUSE status][1]][2]

[1]: https://api.reuse.software/badge/github.com/vinland-technology/flict
[2]: https://api.reuse.software/info/github.com/vinland-technology/flict

# flict / FOSS License Compatibility Tool

# Introduction

***FOSS License Compatibility Tool*** (***flict***) is a Free and Open
Source Software tool to verify license compatibility for a package and
its dependencies. You can use the tool to automate license
compatibility verification in your compliance work flow.

flict can:

* verify licenses compatibilty for license expression and a packages and its dependencies

* suggest candidate outbound licenses

* simplify license expressions 

* display, in misc format, compatibilies between licenses 

* ~~check outbound licenses against a policy (policy as supplied by the user)~~ (automatic now)

flict supports:

* 71 licenses (```flict -of text list```) 

* 'or-later' relicensing  (e.g GPL-2.0-or-later -> GPL-2.0-only or GPL-3.0-only)

* explicit relicensing (LGPL -> GPL)

* common non SPDX ways to write licenses (e.g GPLv2 -> GPL-2.0-only)

* policy framework where you can specify which licenses you want to: allow, avoid or deny

# Examples

Check out our [EXAMPLES](EXAMPLES.md)

# Extensible and tweakable

flict does not come with any knowledge about certain policies,
licenses and their compatibilities. These things are specified outside
the tool, using JSON and CSV files. By default flict has files
defining licenses and compatibilities which probably gets most of our
users going. Having licenses and compatibilities (and even more stuff)
defined outside the tool makes it easy to extend the tool with new
licenses etc without modifying the code.

Read more in [SETTINGS](SETTINGS.md)

# Supported licenses

## License matrix

To check compatibility between two licenses flict is using [OSADL](https://www.osadl.org/)'s
[matrix](https://www.osadl.org/fileadmin/checklists/matrix.html).

# Installing

Look at our [INSTALLATION](INSTALLATION.md) page.

## Docker image

Flict is included in the docker image [Compliance Tools](https://hub.docker.com/repository/docker/sandklef/compliance-tools) which is easily managed by [Compliance Tool Collection](https://github.com/vinland-technology/compliance-tool-collection)

# Exit code and reports

flict outputs a report as well as an exit code.

## Exit code

**0** - success

**5** - missing arguments

**10** - invalid project file

**11** - invalid expression

**12** - file not found

## Compatibility verification report

A report of the component's compatibility with suggested outbound
licenses is created. By default a short text report is created, but
flict can provide a report in a couple of formats.

## Report formats

### JSON

Default. Available for all commands.

### Markdown

With markdown output you can use pandoc to create output in other
formats (e.g. html, pdf). Partially supported.

### Text

Partially supported. 

## User specific configuration

You can create a user specific configuration for the tool that defines a few default parameters to your choices.
Either create a json file at `~/.flict.cfg` or at a path defined by environment variable `FLICT_USERCONFIG`.

| key                   | sets CLI option              |
| --------------------- | ---------------------------- |
| license_matrix-file   | -lmf --license-matrix-file   |
| licenses_denied_file  | -ldf --licenses-denied-file  |
| licenses_denied_file  | -ldf --licenses-denied-file  |
| alias-file            | -af  --alias-file            |
| output-format         | -of  --output-format         |

### Example user configuration

```json
{
    "license_matrix-file": "/my/very/own/osadl-matrix.csv",
    "output-format": "text",
}
```

# Reporting bugs

File a ticket at [github.com/vinland-technology/flict/issues](https://github.com/vinland-technology/flict/issues).

# Contribute to the project

See [CONTRIBUTING](CONTRIBUTING.md)

# License of flict

flict is released under GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)

