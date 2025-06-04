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

Test a patch using only the default test suite (the example file is an internal
selftest):

```console
(venv) tgamblin@megalith ~/workspace/yocto/patchtest2 (main)$ patchtest --patch tests/selftests/files/test_mbox_has_signed_off_by.1.fail
PASS: test_mbox_has_commit_message on [PATCH] selftest-hello: fix CVE-1234-56789
FAIL: test_mbox_has_signed_off_by on [PATCH] selftest-hello: fix CVE-1234-56789 (mbox was missing a signed-off-by tag)
FAIL: test_mbox_revert_signed_off_by_exception on [PATCH] selftest-hello: fix CVE-1234-56789 (Mbox is missing Signed-off-by. Add it manually or with "git commit --amend -s")
PASS: test_mbox_shortlog_format on [PATCH] selftest-hello: fix CVE-1234-56789
PASS: test_mbox_shortlog_length on [PATCH] selftest-hello: fix CVE-1234-56789
SKIP: test_mbox_shortlog_revert_format on [PATCH] selftest-hello: fix CVE-1234-56789 (Not a revert commit)
PASS: test_mbox_unidiff_parse_error on [PATCH] selftest-hello: fix CVE-1234-56789
```

Test the same patch and include the "oe" testsuite (assuming it's included in
the default test path):

```console
(venv) tgamblin@megalith ~/workspace/yocto/patchtest2 (main)$ patchtest --patch tests/selftests/files/test_mbox_has_signed_off_by.1.fail --suites oe
PASS: test_mbox_has_commit_message on [PATCH] selftest-hello: fix CVE-1234-56789
FAIL: test_mbox_has_signed_off_by on [PATCH] selftest-hello: fix CVE-1234-56789 (mbox was missing a signed-off-by tag)
FAIL: test_mbox_revert_signed_off_by_exception on [PATCH] selftest-hello: fix CVE-1234-56789 (Mbox is missing Signed-off-by. Add it manually or with "git commit --amend -s")
PASS: test_mbox_shortlog_format on [PATCH] selftest-hello: fix CVE-1234-56789
PASS: test_mbox_shortlog_length on [PATCH] selftest-hello: fix CVE-1234-56789
SKIP: test_mbox_shortlog_revert_format on [PATCH] selftest-hello: fix CVE-1234-56789 (Not a revert commit)
PASS: test_mbox_unidiff_parse_error on [PATCH] selftest-hello: fix CVE-1234-56789
PASS: test_mbox_author_valid on [PATCH] selftest-hello: fix CVE-1234-56789
SKIP: test_mbox_bugzilla_entry_format on [PATCH] selftest-hello: fix CVE-1234-56789 (No bug ID found)
PASS: test_mbox_commit_message_user_tags on [PATCH] selftest-hello: fix CVE-1234-56789
PASS: test_mbox_non_auh_upgrade on [PATCH] selftest-hello: fix CVE-1234-56789
PASS: test_mbox_target_mailing_list_meta_project on [PATCH] selftest-hello: fix CVE-1234-56789
```

## License

`patchtest2` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
