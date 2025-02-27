# Patchtest Architecture

## Roadmap

- Configuration file to parse (e.g. for setting how long a shortlog should be)
- Pluggable testsuites (pass as e.g. `--testsuite` flag)

## FAQ

**Why do you run tests even if some others that should gate them (e.g. unidiff
parsing) fail?**

A key part of patchtest's design is providing a complete assessment of the
target patches with one invocation, so it prefers spitting out a complete list
of PASS/FAIL/SKIP results for users to make adjustments from, instead of
stopping if one test doesn't work. This is functionally similar to other test
frameworks that have an option to test everything even if some tests fail.

**Why not use pytest or unittest?**

The [original](https://git.yoctoproject.org/poky/tree/meta/lib/patchtest/tests)
already sort of uses unittest, but it's convoluted and hard to maintain,
particularly because of the need to pass a patch file to the tests (which is not
something most test frameworks are really designed to do out-of-the-box).

You could probably write a pytest plugin to do what patchtest is doing, using
something like
[this](https://docs.pytest.org/en/7.1.x/example/simple.html#pass-different-values-to-a-test-function-depending-on-command-line-options). It still has the same issues though.

The way patchtest2 is written right now is similar in spirit to the original
patchtest code, while abstracting/simplifying things quite a bit.
