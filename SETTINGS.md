<!--
SPDX-FileCopyrightText: 2021 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

You can tweak flict by providing:

* [_Alias__](#alias) - alias for "non standard" spelled licenes (e.g. 'BSD3 -> BSD-3-Clause')

# Configuration and runtime files 

<a name="alias"></a>
## License alias defininitions

Sometimes licenses are not expressed in an SPDX compliant way. This
files is intended to translate from "non SPDX" to SPDX. You can
provide a list of definitions for this tool to decide how these
"incorrectly spelled" licenses should be interpreted.

By default flict uses the following alias file: [var/alias.json](var/alias.json)

Example:

```
{
    "aliases": [
        {
            "alias": "GPLv2+",
            "license": "GPL-2.0-or-later",
            "comment": "As found in ...."
        }
}
```

As with previous example you can for now skip the meta section. A translation definition is specified using:

```alias``` - the expression we want to translate to a "proper" license, e.gg GPLv2+

```license``` - a licenses identifier e.g. GPL-2.0-or-later

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
$ flict -of text verify -il MIT AND BSD-3-Clause -ol X11
Yes
$ flict -of text -ldf example-data/denied-licenses.json verify  -il MIT AND BSD-3-Clause -ol X11
No
```

<a name="preference"></a>
## Preferred licenses

In cases where a choice between licenses can be made flict chose the
most preferred license. By default flict counts how many other
licenses each license is compatible with. The more licenses a license
is compatible with the more preferred it will be. If two licenses have
the same number of compaitbilities alpabetical order will be used to
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
 not only '0BSD' and 'AFL-2.0'.*

To apply the new license db and store the result in `merged-matrix.csv`:

```
flict merge -lf additional_matrix.json > merged-matrix.csv

```

To list the supported licenses, with the added licenses:

```
flict -lmf merged-matrix.csv list
```

To use this merged license database when for example veryfing a license:

```
flict -lmf merged-matrix.csv verify -il 0BSD -ol ABC
```


