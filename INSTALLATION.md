<!--
SPDX-FileCopyrightText: 2020 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->


# Required software

The following software are needed to use flict:

* Python (version 3)

    * pip

    * license-expression

## Install required software

### GNU/Linux

#### Debian based distributions

Install Python and pip
```
$ sudo apt-get install python3 python3-pip
```

Install license-expression
```
$ pip3 install license-expression
```

### Windows

Please [help](https://github.com/vinland-technology/flict/issues/26) us writing instructions for this

### MacOS

Please [help](https://github.com/vinland-technology/flict/issues/25) us writing instructions for this

# Install flict

For the time being we have no installation scripts. Please
[help](https://github.com/vinland-technology/flict/issues/27) us
writing code for this.

To install flict you need to clone our repository.

## Install from git 

Go to a directory where you want to put the flict source code. In the
example below we use ```opt``` in the user's home directory.

```
cd 
mkdir opt
cd opt
```


Clone flict:

```
git clone https://github.com/vinland-technology/flict.git
cd flict
```

Setup your PATH variable:
```
PATH=~/opt/flict:$PATH
```

*Note: setting up the PATH variable is something you need to do every time you want to use flict. If you want to add the flict path to the PATH variable permanently try `echo "PATH=~/opt/flict:$PATH" >> ~/.bashrc`*
`

# Using flict

Check out our [EXAMPLES](EXAMPLES.md)

