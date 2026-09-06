"""Tests for the interactive CLI flow."""

from everbot import allocate
from everbot.cli import format_allocation, run


def make_io(inputs):
    """Return (input_fn, output_lines) driving `run` with queued inputs."""
    queue = list(inputs)
    output = []

    def input_fn(_prompt=""):
        return queue.pop(0)

    def output_fn(line=""):
        output.append(line)

    return input_fn, output_fn, output


def test_cli_happy_path_matches_spec():
    input_fn, output_fn, output = make_io(["2", "3", "2", "16"])
    code = run(input_fn, output_fn)
    text = "\n".join(output)

    assert code == 0
    assert "Robot Assignment" in text
    assert "Bravo: 1" in text
    assert "Charlie: 1" in text
    assert "Delta: 1" in text
    assert "Total Work Hours Provided: 16" in text
    assert "Client Work Hours Requested: 16" in text


def test_cli_reports_insufficient_capacity():
    input_fn, output_fn, output = make_io(["1", "1", "1", "17"])
    code = run(input_fn, output_fn)
    assert code == 1
    assert "Insufficient robot capacity" in "\n".join(output)


def test_cli_reports_missing_category():
    input_fn, output_fn, output = make_io(["0", "2", "2", "10"])
    code = run(input_fn, output_fn)
    assert code == 1
    assert "at least one robot from each category" in "\n".join(output)


def test_cli_rejects_non_integer_hours():
    input_fn, output_fn, output = make_io(["2", "2", "2", "abc"])
    code = run(input_fn, output_fn)
    assert code == 1
    assert "Work hours must be a positive integer" in "\n".join(output)


def test_cli_rejects_non_integer_robot_count():
    input_fn, output_fn, output = make_io(["x", "2", "2", "10"])
    code = run(input_fn, output_fn)
    assert code == 1
    assert "Robot counts must be non-negative integers" in "\n".join(output)


def test_format_allocation_exact_block():
    alloc = allocate({"Bravo": 2, "Charlie": 3, "Delta": 2}, 16)
    expected = (
        "Robot Assignment\n"
        "\n"
        "Bravo: 1\n"
        "Charlie: 1\n"
        "Delta: 1\n"
        "\n"
        "Total Work Hours Provided: 16\n"
        "Client Work Hours Requested: 16"
    )
    assert format_allocation(alloc) == expected
