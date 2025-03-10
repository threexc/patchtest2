# patchtest2

patchtest2 is an effort to refactor the existing patchtest tool (part of
the Yocto Project) to use modern Python idioms and reduce complexity.
You can find out more about the tool here:

[Patchtest](https://wiki.yoctoproject.org/wiki/Patchtest)

[![PyPI - Version](https://img.shields.io/pypi/v/patchtest2.svg)](https://pypi.org/project/patchtest2)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/patchtest2.svg)](https://pypi.org/project/patchtest2)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

Right now, the tool is only installable manually. First, setup a
virtualenv:

```console
python3 -m venv venv
```

Start it:

```console
source venv/bin/activate
```

Then install with pip:

```console
pip install .
```

## Examples

Test a patch (the sample file is generated using `git format-patch` on commit `d7de60340ec9` in this repository):

```console
(venv) tgamblin@workbox:~/git/patchtest2$ patchtest --patch 0001-README.md-update-Installation-instructions.patch
PASS: test_mbox_signed_off_by_presence on [PATCH] README.md: update Installation instructions
PASS: test_mbox_shortlog_format on [PATCH] README.md: update Installation instructions
FAIL: test_mbox_commit_message_presence on [PATCH] README.md: update Installation instructions (Please include a commit message on your patch explaining the change)
```

## License

`patchtest2` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
