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

By default flict uses the following alias file: [var/alias.json](flict/var/alias.json)

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

You can for now skip the meta section, which is present in example. A translation definition is specified using:

```alias``` - the expression we want to translate to a "proper" license, e.gg GPLv2+

```license``` - a licenses identifier e.g. GPL-2.0-or-later

If you want to use the aliases as defined in a file called `alias.json` you add `--alias-file alias.json` to your command line.

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

This is described in a separate file: [MERGE_LICENSES](https://github.com/vinland-technology/flict/blob/main/MERGE_LICENSES.md)

