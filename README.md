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

flict can assist you with:

* verify licenses compatibilty for a package and its dependencies

* suggest outbound license candidates

* check outbound licenses against a policy (supplied by the user)

* automatically relicense 

* simplify license expressions 

* verify a package with dependecies for license compatibility

flict supports:

* 71 licenses (```flict -of text list```) 

* 925 licenses in experimental mode using scancode classification (```flict -es -of text list```) 

* 'or-later' relicensing  (e.g GPL-2.0-or-later -> GPL-2.0-only or GPL-3.0-only)

* explcit relicensing 

* common non standard ways to write SPDX license (e.g GPLv2 -> GPL-2.0-only)

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

You can tweak the tool by providing:

* [_Relicense_](#relicense) - change the interpretation of a license with "or-later" (e g `GPL-2.0-or-later`) or relicensing by some other means

* [_Policy_](#policy) - specify which licenses you would like to avoid and which should be denied

* [_Translate_](#translate) - translations for "non standard" spelled licenes (e.g. 'BSD3 -> BSD-3-Clause')

* [_Group_](#group) - undocumented and experimental feature

# Supported licenses

## License matrix

To check compatibility between two licenses flict is using [OSADL's
matrix](https://www.osadl.org/fileadmin/checklists/matrix.html).

## Scancode's db

Flict can also (*experimentally*) use Scancode's [database](https://scancode-licensedb.aboutcode.org/).

# Installing

Look at our [INSTALLATION](INSTALLATION.md) page.

# Configuration and runtime files 

<a name="policy"></a>
## Policy (no built in, optional)

With a policy file you can tell this tool which licenses you disallow
and which you prefer not to avoid. Here's an example policy file:

```
{
    "meta" : {
        "software":"FOSS License Compatibility Tool",
        "version":"0.1"
    } ,
    "policy": {
        "allowlist": [],
        "avoidlist": [
            "BSD-3-Clause"
        ],
        "deniedlist": [
            "MIT",
            "Zlib"
        ]
    }
}
```

When applying a policy to a report you'll get notified whether the
suggested outbound licenses are in compliance with your policy.

<a name="relicense"></a>
## Relicense defininitions (built in or custom)

Some licenses can be specifed saying "or-later", e.g.
GPL-2.0-or-later. You can provide a list of definitions for this tool
to decide how these licenses should be interpreted.

By default flict uses the following relicense file: [var/relicense.json](var/relicense.json)

Let's start with an example:


```
{
    "meta": {
        "software":"FOSS License Compatibility Tool",
        "type": "later-definitions",
        "version":"0.1"
    },
    "relicense-definitions": [
        {
            "spdx": "GPL-2.0-or-later",
            "later": [
                "GPL-2.0-only"
                "GPL-3.0-only"
            ]
        }
    ]
}
```

As with previous example you can for now skip the meta section. A later definition is specified using:

```spdx``` - the license (SPDX short name) this later definition is valid for

```later``` - a list of licenses (SPDX short name) that the above license can be turned into

In the above example we state that GPL-2.0-or-later should be
translated to "GPL-2.0-only or GPL-2.0-only". If you want to use your
own later definition file or disable later definitions by providing an
empty file you can use the option ```--relicense-file```.

<a name="translate"></a>
## License translation defininitions (built in or custom)

Sometimes licenses are not expressed in an SPDX compliant way. This
files is intended to translate from "non SPDX" to SPDX. You can
provide a list of definitions for this tool to decide how these
"incorrectly spelled" licenses should be interpreted.

By default flict uses the following translation file: [var/translation.json](var/translation.json)

Let's start with an example:


```
{
    "meta": {
        "software":"FOSS License Compatibility Tool",
        "type": "later-definitions",
        "version":"0.1"
    },
    "translations": [
        {
            "value": "&",
            "translation": "and"
        },
        {
            "value": "Apache-2",
            "translation": "Apache-2.0"
        }
    ]
}
```

As with previous example you can for now skip the meta section. A translation definition is specified using:

```value``` - the expression we want to translate

```translation``` - tre translated value

In the above example we state that `&` should be
translated to `and` and `Apache-2` to `Apache-2.0`. If you want to use your
own later definition file or disable later definitions by providing an
empty file you can use the option ```--translations-file```.

# Exit code and reports

flict outputs a report as well as an exit code.

## Exit code

To be documented

## Report

A report of the component's compatibility with suggested outbound
licenses is created. By default a short text report is created. With
the tools also comes a couple of Report format that can be used.

## Report formats

### JSON

This is currently rewritten and not available.

### Markdown

Using this format you can create txt, html, pdf and what format pandoc can create from markdown.

## Policy report

To the above report you can apply your own [_Policy_](#policy). Applying this will create a policy report with your policy applied to the suggested outbound license from the usual report and with some complementary information.

# License of flict

flict is currently released under GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)

