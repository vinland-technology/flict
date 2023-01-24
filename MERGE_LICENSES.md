# Extending the license db

## Example with minimal matrix

If you want to extend or override the license database with new
licenses you can do this with a custom database.

Let's assume

1. there's only two licenses, _AFL-2.0_ and _BSD-3-Clause_, in the OSADL matrix. Such a matrix can be found in `example-data/osadl-matrix-mini.csv`.
2. you want to add support for a new license, called _WOW_.
3. _AFL-2.0_ is compatible as follows
    1. can use _BSD-3-Clause_ (specified in the OSADL matrix)
    2. can use NOT use _WOW_ (we're adding this)
4. _BSD-3-Clause_ is compatible as follows
    1. can use _AFL-2.0_ (specified in the OSADL matrix)
    2. can use use _WOW_ (we're adding this)
5. _WOW_ is compatible as follows
    1. can use _AFL-2.0_ (we're adding this)
    2. can use NOT use _BSD-3-Clause_

To extend the license database with your new license, you need to add
how this new license, _WOW_, is compatible with all the other licenses
(both ways).

First of all, you need to add information how the two existing
licenses (AFL-2.0, _BSD-3-Clause_), can use _WOW_:

```
    "AFL-2.0": {
      "WOW": "No"
    }
    "BSD-3-Clause": {
      "WOW": "Yes"
    }
```

and as a second step, add information how the new license, _WOW_, can use the existing licenses (`AFL-2.0` and `BSD-3-Clause`):

```
    "WOW": {
      "AFL-2.0": "Yes",
      "BSD-3.0": "No"
    }
```

All of the above should be placed inside `osadl_additional_licenses` like this:

```
{
    "osadl_additional_licenses": {
        "AFL-2.0": {
            "WOW": "No"
        },
        "BSD-3-Clause": {
            "WOW": "Yes"
        },
        "WOW": {
            "AFL-2.0": "Yes",
            "BSD-3.0": "No"
        }
    }
}
```

*Note: the above is an incomplete example. All licenses supported by
 the OSADL matrix need to be defined in relation to the new license,
 not only _BSD-3-Clause_ and _AFL-2.0_.*.

If the compatibility is NOT defined - _Unknown_ compatibility will be assumed.

Store the above JSON in a file called
`additional_matrix.json`. Actually there is a file in our repository
with this content: `example-data/additional_matrix.json`.

Flict does not support to merge an external, typically yours, license matrix with an additional. Flict only supports merging an additional matrix to the matrix form the `osadl-matrix` Python module.

## Extend the OSADL matrix with additional licenses

If you want to add two more licenses, _WOW_ and _ZOZ_, to the existing
OSADL matrix you follow the same procedure as in the example
above. Typically do this in two steps:

* Add compatibility from the existing to the new licenses

### Add compatibility from the existing to the new licenses

For each license supported in the OSADL matrix:

* add an entry for the compatibility between that license and the ones you want to add

* add compatibility from the new licenses to the existing ones

Example 

```
{
    "osadl_additional_licenses": {
        "AFL-2.0": {
            "WOW": "No",
            "ZOZ": "Yes"
        },
        "AFL-2.1": {
            "WOW": "No",
            "ZOZ": "Yes"
        },
        .... continue the above for every license in the OSADL matrix
```

### Add compatibility from the new licenses to the existing ones

For each new license:

* add an entry for the compatibility between that license and the ones in the OSADL matrix


```
        "WOW": {
            "AFL-2.0": "Yes",
            "AFL-2.1": "Yes",
            .... continue the above for every license in the OSADL matrix
        },
        "ZOZ": {
            "AFL-2.0": "Yes",
            "AFL-2.1": "Yes",
            .... continue the above for every license in the OSADL matrix
        }
```

### Putting the pieces together

If you've done the two steps above you should have a JSON file looking like this:

```
{
    "osadl_additional_licenses": {
        "AFL-2.0": {
            "WOW": "No",
            "ZOZ": "Yes"
        },
        "AFL-2.1": {
            "WOW": "No",
            "ZOZ": "Yes"
        },
        .... continue the above for every license in the OSADL matrix
        "zlib-acknowledgement": {
            "WOW": "Yes",
            "ZOZ": "No"
        }       
        "WOW": {
            "AFL-2.0": "Yes",
            "AFL-2.1": "Yes",
            .... continue the above for every license in the OSADL matrix
            "zlib-acknowledgement": "No"
        },
        "ZOZ": {
            "AFL-2.0": "Yes",
            "AFL-2.1": "Yes",
            .... continue the above for every license in the OSADL matrix
            "zlib-acknowledgement": "No"
        }
    }
}
```

## Merging

To merge the new licenses file, `additional_matrix.json`, with the
OSADL matrix and store the result in `merged-matrix.csv`:

```
flict merge -lf example-data/additional_matrix.json > merged-matrix.csv
```

Let's analyze the above command a bit:

* Input data

    * `example-data/additional_matrix.json` (added support of the license _WOW_)

* Result 

    * output to `stdout`, redirected to `merged-matrix.csv`. This file is now our new matrix, with support for the old licenses as well as _WOW_ and _ZOZ_, that we should use from now on.


## Using the merged database

To list the supported licenses, with the added licenses:

```
flict -lmf merged-matrix.csv list
```

To use this merged license database when veryfing an inbound against an outbound license:

```
flict -lmf merged-matrix.csv verify -il 0BSD -ol WOW
```
