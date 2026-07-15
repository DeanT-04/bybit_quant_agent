import pathlib
import runpy
import sys

import pytest

from quant_platform.main import main


def test_main_executes_successfully(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify that main runs and prints the startup message."""
    # Ensure .env exists in the current working directory for the test duration
    env_file = pathlib.Path(".env")
    existed = env_file.exists()
    if not existed:
        env_file.write_text("", encoding="utf-8")

    try:
        main()
        captured = capsys.readouterr()
        # The StreamHandler by default logs to stderr.
        # Let's check both stdout and stderr.
        combined = captured.out + captured.err
        assert "Application started successfully." in combined
    finally:
        if not existed and env_file.exists():
            env_file.unlink()


def test_main_as_script(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify that main executes successfully when run as a script."""
    # Ensure .env exists in the current working directory for the test duration
    env_file = pathlib.Path(".env")
    existed = env_file.exists()
    if not existed:
        env_file.write_text("", encoding="utf-8")

    try:
        # Temporarily remove from sys.modules to avoid RuntimeWarning about reloading
        main_module = sys.modules.pop("quant_platform.main", None)
        try:
            runpy.run_module("quant_platform.main", run_name="__main__")
        finally:
            if main_module is not None:
                sys.modules["quant_platform.main"] = main_module

        captured = capsys.readouterr()
        combined = captured.out + captured.err
        assert "Application started successfully." in combined
    finally:
        if not existed and env_file.exists():
            env_file.unlink()

