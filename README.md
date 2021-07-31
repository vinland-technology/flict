<!--
SPDX-FileCopyrightText: 2020 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

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

* check outbound licenses against a policy (policy as supplied by the user)

flict supports:

* 71 licenses (```flict -of text list```) 

* 925 licenses in experimental mode using scancode classification (```flict -es -of text list```) 

* 'or-later' relicensing  (e.g GPL-2.0-or-later -> GPL-2.0-only or GPL-3.0-only)

* explicit relicensing (LGPL -> GPL)

* common non SPDX ways to write licenses (e.g GPLv2 -> GPL-2.0-only)

* grouping of common licenses in to well known license classification 

* policy framework where you can specify which licenses you want to: allow, avoid or deny

# Examples

Check out our [EXAMPLES](EXAMPLES.md)

# Contribute to the project

See [CONTRIBUTING](CONTRIBUTING.md)

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

To check compatibility between two licenses flict is using [OSADL's
matrix](https://www.osadl.org/fileadmin/checklists/matrix.html).

## Scancode's db

Flict can also (*experimentally*) use Scancode's [database](https://scancode-licensedb.aboutcode.org/).

# Installing

Look at our [INSTALLATION](INSTALLATION.md) page.

## Docker image

Flict is included in the docker image: [Compliance Tools](https://hub.docker.com/repository/docker/sandklef/compliance-tools)

# Exit code and reports

flict outputs a report as well as an exit code.

## Exit code

**0** - success

**5** - missing arguments

**10** - invalid project file

**10** - invalid license expression

## Report

A report of the component's compatibility with suggested outbound
licenses is created. By default a short text report is created, but
flict can provide a report in a couple of formats.

## Report formats

### JSON

This is currently rewritten and not available.

### Markdown

Using this format you can create txt, html, pdf and what format pandoc can create from markdown.

## Policy report

To the above report you can apply your own policy (see [SETTINGS](SETTINGS.md)). Applying this will create a policy report with your policy applied to the suggested outbound license from the usual report and with some complementary information.

# License of flict

flict is released under GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)

