<!--
SPDX-FileCopyrightText: 2020 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->


# Required software

The following software are needed to use flict:

- Python (version 3)
  - pip
  - license-expression

## Install required software

### GNU/Linux

#### Debian based distributions

Install Python and pip

```shell
sudo apt-get install python3 python3-pip
```

```shell
pip3 install flict
```

### Windows

Please help us writing instructions for this

### MacOS

Please help us writing instructions for this

# Install developing dependencies

```shell
pip3 install -e .[dev]
```

## Install from git

In case you want to install the tool for all user (requires sudo)

```shell
git clone https://github.com/vinland-technology/flict.git
cd flict
sudo python3 setup.py install
```

or alternatively for just the current user

```shell
git clone https://github.com/vinland-technology/flict.git
cd flict
python3 setup.py install --user
```

# Docker image

Flict is included in the docker image [Compliance Tools](https://hub.docker.com/repository/docker/sandklef/compliance-tools) which is easily managed by [Compliance Tool Collection](https://github.com/vinland-technology/compliance-tool-collection)

# Using flict

Check out our [EXAMPLES](EXAMPLES.md)
