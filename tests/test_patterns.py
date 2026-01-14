"""Unit tests for patchtest2 patterns module."""

import pytest
import pyparsing
from patchtest2 import patterns


class TestSignedOffByPattern:
    """Tests for signed-off-by pattern matching."""

    def test_valid_signed_off_by_matches(self):
        """Test that valid signed-off-by lines are matched."""
        text = "Signed-off-by: John Doe <john@example.com>"
        result = patterns.signed_off_by.search_string(text)
        assert result, "Valid signed-off-by should match"

    def test_invalid_email_does_not_match(self):
        """Test that invalid email format doesn't match."""
        text = "Signed-off-by: Invalid"
        result = patterns.signed_off_by.search_string(text)
        assert not result, "Invalid signed-off-by should not match"

    def test_missing_angle_brackets_does_not_match(self):
        """Test that missing angle brackets doesn't match."""
        text = "Signed-off-by: John Doe john@example.com"
        result = patterns.signed_off_by.search_string(text)
        assert not result, "Signed-off-by without angle brackets should not match"

    def test_name_with_spaces(self):
        """Test that names with multiple spaces work."""
        text = "Signed-off-by: John Q. Public <john.q.public@example.com>"
        result = patterns.signed_off_by.search_string(text)
        assert result, "Name with spaces should match"


class TestShortlogPattern:
    """Tests for shortlog format pattern."""

    def test_valid_shortlog_matches(self):
        """Test that valid shortlog format matches."""
        text = "module: Add new feature"
        try:
            patterns.shortlog.parse_string(text, parse_all=True)
            assert True
        except pyparsing.ParseException:
            pytest.fail("Valid shortlog should parse")

    def test_shortlog_without_colon_fails(self):
        """Test that shortlog without colon fails."""
        text = "module Add new feature"
        with pytest.raises(pyparsing.ParseException):
            patterns.shortlog.parse_string(text, parse_all=True)

    def test_shortlog_with_multi_part_target(self):
        """Test that multi-part targets work."""
        text = "layer/module: Fix bug"
        try:
            patterns.shortlog.parse_string(text, parse_all=True)
            assert True
        except pyparsing.ParseException:
            pytest.fail("Multi-part target should parse")


class TestCVEPattern:
    """Tests for CVE pattern matching."""

    def test_valid_cve_matches(self):
        """Test that valid CVE identifiers match."""
        text = "CVE-2024-1234"
        result = patterns.cve.search_string(text)
        assert result, "Valid CVE should match"

    def test_invalid_cve_year_format(self):
        """Test that invalid year format doesn't match."""
        text = "CVE-24-1234"
        result = patterns.cve.search_string(text)
        assert not result, "Invalid CVE year should not match"

    def test_cve_in_text(self):
        """Test that CVE is found within text."""
        text = "This patch fixes CVE-2024-5678 and improves security"
        result = patterns.cve.search_string(text)
        assert result, "CVE should be found in text"


class TestUpstreamStatus:
    """Tests for upstream status patterns."""

    def test_valid_upstream_status_pending(self):
        """Test that 'Pending' status matches."""
        text = "Upstream-Status: Pending"
        try:
            patterns.upstream_status.parse_string(text, parse_all=True)
            assert True
        except pyparsing.ParseException:
            pytest.fail("Valid Pending status should parse")

    def test_valid_upstream_status_backport(self):
        """Test that 'Backport' status matches."""
        text = "Upstream-Status: Backport"
        try:
            patterns.upstream_status.parse_string(text, parse_all=True)
            assert True
        except pyparsing.ParseException:
            pytest.fail("Valid Backport status should parse")

    def test_invalid_upstream_status(self):
        """Test that invalid status doesn't match."""
        text = "Upstream-Status: Unknown"
        with pytest.raises(pyparsing.ParseException):
            patterns.upstream_status.parse_string(text, parse_all=True)


class TestEmailPattern:
    """Tests for email address pattern."""

    def test_valid_email_matches(self):
        """Test that valid email addresses match."""
        text = "test@example.com"
        result = patterns.email_pattern.search_string(text)
        assert result, "Valid email should match"

    def test_email_with_subdomain(self):
        """Test that emails with subdomains work."""
        text = "user@mail.example.com"
        result = patterns.email_pattern.search_string(text)
        assert result, "Email with subdomain should match"

    def test_email_with_plus(self):
        """Test that emails with plus addressing work."""
        text = "user+tag@example.com"
        result = patterns.email_pattern.search_string(text)
        assert result, "Email with plus should match"


class TestRevertShortlog:
    """Tests for revert commit shortlog pattern."""

    def test_valid_revert_matches(self):
        """Test that valid revert format matches."""
        text = 'Revert "original commit message"'
        result = patterns.mbox_revert_shortlog_regex.search_string(text)
        assert result, "Valid revert should match"

    def test_non_revert_does_not_match(self):
        """Test that non-revert commits don't match."""
        text = "module: Fix issue"
        result = patterns.mbox_revert_shortlog_regex.search_string(text)
        assert not result, "Non-revert should not match"


class TestBugzillaPattern:
    """Tests for Bugzilla reference patterns."""

    def test_valid_bugzilla_format_matches(self):
        """Test that properly formatted Bugzilla refs match."""
        text = "[YOCTO #12345]"
        result = patterns.mbox_bugzilla_validation.search_string(text)
        assert result, "Valid Bugzilla format should match"

    def test_multiple_bugzilla_refs(self):
        """Test that multiple refs in one tag work."""
        text = "[YOCTO #12345, YOCTO #67890]"
        result = patterns.mbox_bugzilla_validation.search_string(text)
        assert result, "Multiple Bugzilla refs should match"

    def test_invalid_bugzilla_format(self):
        """Test that invalid format doesn't match validation."""
        text = "[YOCTO 12345]"  # Missing '#'
        result = patterns.mbox_bugzilla_validation.search_string(text)
        assert not result, "Invalid Bugzilla format should not match validation"
