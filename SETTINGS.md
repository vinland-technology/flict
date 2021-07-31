
You can tweak flict by providing:

* [_Relicense_](#relicense) - change the interpretation of a license with "or-later" (e g `GPL-2.0-or-later`) or relicensing by some other means

* [_Policy_](#policy) - specify which licenses you would like to avoid and which should be denied

* [_Translate_](#translate) - translations for "non standard" spelled licenes (e.g. 'BSD3 -> BSD-3-Clause')

* [_Group_](#group) - undocumented and experimental feature

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
