<!--
SPDX-FileCopyrightText: 2021 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

You can tweak flict by providing:

* <a name="#name">Denied licenses</a>

* <a name="#preference">Preferred licenses</a>

* <a name="#extending">Extending the license db</a>

In earlier versions of flict you could provide your own aliases. Now
flict relies on [foss-licenses](https://github.com/hesa/foss-licenses)
(available in [pypi.org](https://pypi.org) as
[foss-flame](https://pypi.org/project/foss-flame/)).

# Configuration and runtime files

<a name="denied"></a>
## Denied licenses

If you, for some reason, want to deny a license (e.g. 'MIT*) to be used as outbound or inbound license.

Example:

```
{
    "licenses_denied": ["MIT"]
}
```

If you store this in a file, `denied-list.json`, you can use it like this:

```
$ flict -of text verify -il 'MIT AND BSD-3-Clause' -ol X11
Yes
$ flict -of text -ldf example-data/denied-licenses.json verify  -il 'MIT AND BSD-3-Clause' -ol X11
No
```

<a name="preference"></a>
## Preferred licenses

In cases where a choice between licenses can be made flict chose the
most preferred license. By default flict counts how many other
licenses each license is compatible with. The more licenses a license
is compatible with the more preferred it will be. If two licenses have
the same number of compatibilities, alpabetical order will be used to
chose license.

If you want to provide your own ordered list of license preference, you do this like this:

Example:

```
{
    "license_preferences": [
        "curl", "MIT"
    ]

}
```

If you store this in a file, `license-preferences.json`, you can use it with the `-lpf` option.

<a name="extending"></a>
## Extending the license db

If you want to extend or override the license database with new
licenses you can do this with a custom database.

Let's say you want to add support for a new license, called 'ABC'. You need to add how this new license is compatible with all other in both ways.

Adding information how existing licenses ('0BSD', 'AFL-2.0' and so on), can use 'ABC':
```
    "0BSD": {
      "ABC": "Yes"
    },
    "AFL-2.0": {
      "ABC": "Yes"
    },
        .... and so on
```

Adding information how the new license, 'ABC', can use the existing licenses (`0BSD`, `AFL-2.0` and so on):
```
    "ABC": {
      "0BSD": "Yes",
      "AFL-2.0": "Yes"
    }
```

These should be placed inside `osadl_additional_licenses` like this:

```
{
  "osadl_additional_licenses": {
    "0BSD": {
      "ABC": "Yes"
    },
    "AFL-2.0": {
      "ABC": "Yes"
    },
    "ABC": {
      "0BSD": "Yes",
      "AFL-2.0": "Yes"
    }
```

*Note: the above is an incomplete example. All licenses supported by
 the OSADL matrix need to be defined in relation to the new license,
 not only '0BSD' and 'AFL-2.0'.*. If they are NOT defined - 'Unknown' compatibility will be assumed.
 This file is further called `additional_matrix.json`.

To apply the new license db and store the result in `merged-matrix.json`:

```
flict merge -lf additional_matrix.json > merged-matrix.json

```

To list the supported licenses, with the added licenses:

```
flict -lmf merged-matrix.json list
```

To use this merged license database when for example veryfing a license:

```
flict -lmf merged-matrix.json verify -il 0BSD -ol ABC
```

*Note: Previously flict created csv output when merging. If you still want csv output, use `-of csv`*
