<!--
SPDX-FileCopyrightText: 2020 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Required software

The following software are needed to use flict:

- Python (version 3.6+)
- pip

## Install from pypi

- run `pip3 install flict` _(might require sudo/root/admin rights)_

## Install from git clone

- run `git clone https://github.com/vinland-technology/flict`
- *optional*: checkout the revision you like to install
- run `cd flict`
- run `pip3 install -r requirements.txt`
- run `pip3 install .` _(might require sudo/root/admin rights)_

## Install development version

- run `git clone https://github.com/vinland-technology/flict`
- *optional*: checkout the revision you like to install
- run `cd flict`
- run `pip3 install -r requirements-dev.txt`
- run `pip3 install -e .[dev]` _(might require sudo/root/admin rights)_

### Non-root installation

In case you don't have root access on your machine you need add `--user` to all the `pip3` calls - e.g. `pip3 install --user -e .[dev]`.

**NOTE: On __Debian-based__ systems that is the default behavior**

# Docker image

Flict is included in the docker image [Compliance Tools](https://hub.docker.com/repository/docker/sandklef/compliance-tools) which is easily managed by [Compliance Tool Collection](https://github.com/vinland-technology/compliance-tool-collection)

# Using flict

Check out our [EXAMPLES](EXAMPLES.md)
