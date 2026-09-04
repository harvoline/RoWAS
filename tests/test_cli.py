"""Smoke tests for the CLI entry point.

These tests exist to prove the project scaffolding (packaging, imports,
test runner wiring) works end-to-end. They intentionally know nothing
about robot allocation business rules, which have not been specified yet.
"""

from robot_allocation.cli import main


def test_main_runs_and_exits_successfully(capsys):
    exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "EverBot" in captured.out
