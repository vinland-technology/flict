<!--
SPDX-FileCopyrightText: 2021 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->


# Display Simplify license expression

To simplify the expression `MIT and BSD-3-Clause and MIT`, type:

```shell
$ flict simplify MIT and BSD-3-Clause and MIT
{"original": "MIT and BSD-3-Clause and MIT", "simplified": "BSD-3-Clause AND MIT"}
```

and if you want the result in `text` format:

```shell
$ flict -of text simplify MIT and BSD-3-Clause and MIT
BSD-3-Clause AND MIT
```

# Check compatibility between licenses

To check how the licenses `BSD-3-Clause MIT GPL-2.0-only` are compatible with each other you can type:

```shell
$ flict display-compatibility BSD-3-Clause MIT GPL-2.0-only
{"compatibilities": [{"license": "MIT", "licenses": [{"license": "BSD-3-Clause", "compatible_right": "true", "compatible_left": "true"}, {"license": "GPL-2.0-only", "compatible_right": "true", "compatible_left": "false"}]}, {"license": "BSD-3-Clause", "licenses": [{"license": "MIT", "compatible_right": "true", "compatible_left": "true"}, {"license": "GPL-2.0-only", "compatible_right": "true", "compatible_left": "false"}]}, {"license": "GPL-2.0-only", "licenses": [{"license": "MIT", "compatible_right": "false", "compatible_left": "true"}, {"license": "BSD-3-Clause", "compatible_right": "false", "compatible_left": "true"}]}]}
```

As a result, you can see a list of compatibilities in form: which license is analysed, and if it is compatible with all others specified.
Given that, one can see that MIT and GPL-2.0-only are compatible only one-way.

## Create graph over compatibility

Instead of a text based representation (as above) you can instead create a graphical representation using `dot` format.

```shell
$ flict -of dot display-compatibility BSD-3-Clause MIT GPL-2.0-only > compat.dot
$ dot -Tpdf compat.dot -O
```

## Output formats

You can use the `-of` option (e.g. `-of JSON`)  to specify wanted output format:

* JSON - default

* markdown - from which you can generate HTML, PDF, latex, odt, docx and many more

* text - we're trying to be human friendly here

* dot - for use with graphviz (`dot`) so you can create graphical representation of the compatibility

# Calculate outbound license

To get a list of suggested outbound licenses for the expression `MIT and BSD & GPL-2.0-or-later`, type:

```shell
$ flict outbound-candidate MIT and BSD and GPL-2.0-or-later
["GPL-2.0-only", "GPL-3.0-only"]
```
***Note:** the `GPL-2.0-or-later` has been relicensed to `GPL-2.0-only OR GPL-3.0-only`*

## Suggesting licenses (as outbound) from all known licenses

Instead of calculating the outbound license suggestions from the list
of licenses in the project (with its dependencies) you can instruct
flict to check every its known licenses as outbound:

```shell
$ flict outbound-candidate Apache-2.0 AND LGPL-2.1-only
[]
$ flict -el outbound-candidate Apache-2.0 AND LGPL-2.1-only
["GPL-3.0-only", "GPL-3.0-or-later"]
```

# Create compatibility report of the Europe project

## JSON

To get a compatibility report for the project (flict format) as specified in [example-data/europe.json](example-data/europe.json) and store the result in `europe-report.json`, type:

```shell
$ flict -o europe-report.json verify -f example-data/europe.json 
```

This creates a report in JSON

*Tip: . If you want to pretty print this file you can use tools such as `jq`: `jq . europe-report.json`*

To get the suggested outbound licenses from the report (using `jq`), type:

```shell
$ jq '.licensing.outbound_candidates' europe-report.json
[
  "Apache-2.0",
  "BSD-3-Clause",
  "GPL-2.0-only",
  "GPL-3.0-only",
  "MIT",
  "MPL-1.1"
]
```

## Markdown

To get a compatibility report for the project (flict format) as specified in [example-data/europe.json](example-data/europe.json) and store the result in `europe-report.md`, type:

```shell
$ flict -o europe-report.md -of markdown verify -f example-data/europe.json 
```

This creates a report in markdown. Using `pandoc` you can convert this markdown report in to many others format, e.g. pdf like this `pandoc europe-report.md -o europe-report.pdf`.

# List supported licenses

```shell
$ flict list
["Artistic-1.0-Perl", "MPL-2.0", "EPL-2.0", "UPL-1.0", "Unicode-DFS-2015", "MIT", "MirOS", "FTL", "bzip2-1.0.6", "WTFPL", "Apache-1.1", "GPL-3.0-or-later", "AGPL-3.0-only", "CPL-1.0", "Compatibility", "IPL-1.0", "curl", "GPL-2.0-only", "libtiff", "XFree86-1.1", "OpenSSL", "EUPL-1.1", "SunPro", "EFL-2.0", "OSL-3.0", "BSD-4-Clause-UC", "Qhull", "bzip2-1.0.5", "LGPL-3.0-only", "LGPL-2.1-only", "IJG", "AFL-2.0", "Public Domain", "BSD-2-Clause", "AGPL-3.0-or-later", "BSD-3-Clause", "GPL-2.0-only WITH Classpath-exception-2.0", "MS-PL", "GPL-3.0-only", "Libpng", "Python-2.0", "CDDL-1.0", "EPL-1.0", "LGPL-2.1-or-later", "BSD-4-Clause", "Zlib", "Apache-1.0", "BSL-1.0", "MS-RL", "X11", "Proprietary-linked", "ISC", "zlib-acknowledgement", "NTP", "CC0-1.0", "BSD-2-Clause-Patent", "HPND", "IBM-pibs", "Proprietary", "MIT-CMU", "RPL-1.5", "Unicode-DFS-2016", "MPL-1.1", "NBPL-1.0", "Permissive", "ICU", "MPL-2.0-no-copyleft-exception", "GPL-2.0-or-later", "Apache-2.0", "AFL-2.1", "LGPL-3.0-or-later"]
```

