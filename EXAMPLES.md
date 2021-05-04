<!--
SPDX-FileCopyrightText: 2021 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->


# Display and/or Simplify license expression

To simplify the expression `MIT and BSD-3-Clause & MIT`, type:

```
$ flict -le "MIT and BSD-3-Clause & MIT"
BSD-3-Clause AND MIT
```

# Check compatibility between licenses

To check how the licenses `BSD-3-Clause MIT GPL-2.0-only` are compatible with each other you can type:

```
$ flict -v -cc BSD-3-Clause MIT GPL-2.0-only
{"compatibilities": [{"license": "MIT", "licenses": [{"license": "GPL-2.0-only", "compatible_right": "true", "compatible_left": "false"}, {"license": "BSD-3-Clause", "compatible_right": "true", "compatible_left": "true"}]}, {"license": "GPL-2.0-only", "licenses": [{"license": "MIT", "compatible_right": "false", "compatible_left": "true"}, {"license": "BSD-3-Clause", "compatible_right": "false", "compatible_left": "true"}]}, {"license": "BSD-3-Clause", "licenses": [{"license": "MIT", "compatible_right": "true", "compatible_left": "true"}, {"license": "GPL-2.0-only", "compatible_right": "true", "compatible_left": "false"}]}]}
```

## Create graph over compatibility

Instead of a text based representation (as above) you can instead create a graphical representation using `dot` format. 

```
$ flict -v -cc BSD-3-Clause MIT GPL-2.0-only -of dot > compat.dot
$ dot -Tpdf compat.dot -O
```

## Output formats

You can use the `-of` option (e.g. `-of JSON`)  to specify wanted output format:

* JSON - default

* markdown - from which you can generate HTML, PDF, latex, odt, docx and many more

* dot - for use with graphviz (`dot`) so you can create graphical representation of the compatibility


# Calculate outbound license

To get a list of suggested outbound licenses for the expression `MIT and BSD & GPL-2.0-or-later`, type:

```
$ flict -ol "MIT and BSD & GPL-2.0-or-later"
["GPL-2.0-only", "GPL-3.0-only"]
```

***Note:** the `GPL-2.0-or-later` has been relicensed to `GPL-2.0-only OR GPL-3.0-only`*

## Suggesting licenses (as outbound) from all known licenses

Instead of calculating the outbound license suggestions from the list
of licenses in the project (with its dependencies) you can instruct
flict to check every its known licenses as outbound:

```
$ flict -el -ol  "BSD-3-Clause and MIT"
["AFL-2.0", "EFL-2.0", "OSL-3.0", "FTL", "IBM-pibs", "AGPL-3.0-only", "Zlib", "CDDL-1.0", "Artistic-1.0-Perl", "CC0-1.0", "libtiff", "GPL-3.0-or-later", "zlib-acknowledgement", "SunPro", "MPL-1.1", "Apache-1.0", "MS-RL", "Python-2.0", "BSL-1.0", "GPL-3.0-only", "MIT", "LGPL-3.0-or-later", "MPL-2.0-no-copyleft-exception", "ICU", "Apache-1.1", "bzip2-1.0.6", "BSD-3-Clause", "EUPL-1.1", "MIT-CMU", "MPL-2.0", "LGPL-2.1-or-later", "BSD-2-Clause-Patent", "HPND", "Libpng", "RPL-1.5", "MirOS", "Apache-2.0", "EPL-2.0", "X11", "IPL-1.0", "Unicode-DFS-2015", "CPL-1.0", "ISC", "curl", "LGPL-3.0-only", "EPL-1.0", "OpenSSL", "XFree86-1.1", "BSD-4-Clause", "BSD-4-Clause-UC", "BSD-2-Clause", "GPL-2.0-or-later", "MS-PL", "bzip2-1.0.5", "WTFPL", "AGPL-3.0-or-later", "Permissive", "LGPL-2.1-only", "NBPL-1.0", "GPL-2.0-only", "IJG", "NTP", "Unicode-DFS-2016", "UPL-1.0", "GPL-2.0-only WITH Classpath-exception-2.0", "Public Domain", "AFL-2.1", "Qhull"]
```

# Create compatibility report of the Europe project

## JSON

To get a compatibility report for the project as specified in [example-data/europe.json](example-data/europe.json) and store the result in `europe-report.json`, type:

```
$ flict -pf example-data/europe.json > europe-report.json
```

This creates a report in JSON

*Tip: . If you want to pretty print this file you can use tools such as `jq`: `jq . europe-report.json`*

To get the suggested outbound licenses from the report (using `jq`), type:

```
$ jq '.licensing.outbound_suggestions' europe-report.json 
[
  "GPL-2.0-only",
  "GPL-3.0-only"
]
```

## Markdown

Coming soon


# Create a policy report of the Europe project

## JSON

To get a policy, as specified in [example-data/europe-policy.json](example-data/europe-policy.json),
report for the compatibility report of the project as specified in
[example-data/europe.json](example-data/europe.json) and store the result in
`europe-policy-report.json` type:

```
$ flict -lpf example-data/europe-policy.json -crf europe-report.json > europe-policy-report.json 
```

This creates a policy report in JSON

*Tip: . If you want to pretty print this file you can use tools such as `jq`: `jq . europe-policy-report.json`*

To get the list of suggested outbound licenses with the policy applied (using `jq`), type:

```
$ jq .policy_outbounds europe-policy-report.json 
{
  "allowed": [
    "GPL-2.0-only"
  ],
  "avoid": [],
  "denied": [
    "GPL-3.0-only"
  ],
  "policy_result": 0
}
```

Here we can see that we have one suggested outbound which is denied
`GPL-3.0-only` and one which is OK to use `GPL-2.0-only`.
