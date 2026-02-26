"""Tests for fubon-cli main CLI"""
import pytest
from click.testing import CliRunner
from fubon_cli.main import cli


class TestMainCLI:
    """Test main CLI commands"""

    def test_cli_help(self):
        """Test CLI help command"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_cli_version(self):
        """Test CLI version command"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower() or "0." in result.output

    @pytest.mark.cli
    def test_cli_no_args(self):
        """Test CLI without arguments shows help"""
        runner = CliRunner()
        result = runner.invoke(cli, [])
        # Should show help or require arguments
        assert result.exit_code in [0, 2]
