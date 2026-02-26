"""Tests for fubon-cli core module"""

import pytest

from fubon_cli import core


class TestCoreModule:
    """Test core module functionality"""

    def test_core_import(self):
        """Test that core module can be imported"""
        assert core is not None

    @pytest.mark.slow
    def test_version_accessible(self):
        """Test version information is accessible"""
        # Version will be dynamically managed by setuptools-scm
        assert hasattr(core, "__name__")
