"""Unit tests for patchtest2 results module."""

import pytest

from patchtest2.results import patchtest_result


class TestPatchtestResultDecorator:
    """Tests for the patchtest_result decorator."""

    def test_pass_result_formatting(self):
        """Test that PASS results are formatted correctly."""

        @patchtest_result
        def dummy_test(patch):
            return "[PATCH] test", "PASS", None

        result = dummy_test(None)
        assert result == "PASS: dummy_test on [PATCH] test"
        assert "(" not in result, "PASS should not include reason in parentheses"

    def test_fail_result_formatting(self):
        """Test that FAIL results include reason."""

        @patchtest_result
        def dummy_test(patch):
            return "[PATCH] test", "FAIL", "missing something"

        result = dummy_test(None)
        assert result == "FAIL: dummy_test on [PATCH] test (missing something)"
        assert "missing something" in result

    def test_skip_result_formatting(self):
        """Test that SKIP results include reason."""

        @patchtest_result
        def dummy_test(patch):
            return "[PATCH] test", "SKIP", "not applicable"

        result = dummy_test(None)
        assert result == "SKIP: dummy_test on [PATCH] test (not applicable)"
        assert "not applicable" in result

    def test_invalid_return_type_raises_error(self):
        """Test that non-tuple return raises ValueError."""

        @patchtest_result
        def dummy_test(patch):
            return "not a tuple"

        with pytest.raises(ValueError, match="must return a tuple"):
            dummy_test(None)

    def test_wrong_tuple_length_raises_error(self):
        """Test that wrong-length tuple raises ValueError."""

        @patchtest_result
        def dummy_test(patch):
            return "[PATCH] test", "PASS"  # Only 2 elements

        with pytest.raises(ValueError, match="must return.*3 values"):
            dummy_test(None)

    def test_invalid_result_value_raises_error(self):
        """Test that invalid result value raises ValueError."""

        @patchtest_result
        def dummy_test(patch):
            return "[PATCH] test", "INVALID", "reason"

        with pytest.raises(ValueError, match="invalid result.*INVALID"):
            dummy_test(None)

    def test_function_name_preserved(self):
        """Test that decorator preserves function name."""

        @patchtest_result
        def my_custom_test(patch):
            return "[PATCH] test", "PASS", None

        assert my_custom_test.__name__ == "my_custom_test"

    def test_docstring_preserved(self):
        """Test that decorator preserves function docstring."""

        @patchtest_result
        def documented_test(patch):
            """This is a test docstring."""
            return "[PATCH] test", "PASS", None

        assert documented_test.__doc__ == "This is a test docstring."

    def test_pass_with_none_reason(self):
        """Test that PASS works correctly with None reason."""

        @patchtest_result
        def dummy_test(patch):
            return "[PATCH] test", "PASS", None

        result = dummy_test(None)
        assert "None" not in result, "None should not appear in output"

    def test_fail_with_multiline_reason(self):
        """Test that FAIL handles multiline reasons."""

        @patchtest_result
        def dummy_test(patch):
            return "[PATCH] test", "FAIL", "line1\nline2"

        result = dummy_test(None)
        assert "line1\nline2" in result
