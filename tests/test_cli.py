"""Tests for the interactive CLI flow (Level 2 + L1/L2 comparison)."""

from everbot import allocate
from everbot.cli import format_allocation, format_comparison, format_cost_allocation, run
from everbot.comparison import compare_levels


def make_io(inputs):
    """Return (input_fn, output_fn, output_lines) driving `run` with queued inputs."""
    queue = list(inputs)
    output = []

    def input_fn(_prompt=""):
        return queue.pop(0)

    def output_fn(line=""):
        output.append(line)

    return input_fn, output_fn, output


def test_cli_owner_example_1():
    input_fn, output_fn, output = make_io(["2", "3", "2", "20"])
    code = run(input_fn, output_fn)
    text = "\n".join(output)

    assert code == 0
    assert "Cost Optimized Allocation" in text
    assert "Charlie: 1" in text
    assert "Delta: 2" in text
    assert "Total Hours Provided: 21" in text
    assert "Total Charging Cost: $11" in text
    assert "Level 1 Cost: $12" in text
    assert "Level 2 Cost: $11" in text
    assert "Cost Difference: $1" in text
    assert "mandatory usage of multiple robot categories" in text


def test_cli_owner_example_2():
    input_fn, output_fn, output = make_io(["2", "2", "3", "6"])
    code = run(input_fn, output_fn)
    text = "\n".join(output)

    assert code == 0
    assert "Cost Optimized Allocation" in text
    assert "Bravo: 2" in text
    assert "Total Hours Provided: 6" in text
    assert "Total Charging Cost: $4" in text


def test_cli_reports_level1_infeasible_gracefully():
    # No Bravo — Level 2 still works; comparison notes Level 1 infeasible.
    input_fn, output_fn, output = make_io(["0", "3", "2", "20"])
    code = run(input_fn, output_fn)
    text = "\n".join(output)

    assert code == 0
    assert "Cost Optimized Allocation" in text
    assert "Total Charging Cost: $11" in text
    assert "Level 1: infeasible" in text
    assert "each category" in text


def test_cli_reports_insufficient_capacity():
    input_fn, output_fn, output = make_io(["1", "0", "0", "10"])
    code = run(input_fn, output_fn)
    assert code == 1
    assert "Insufficient robot capacity" in "\n".join(output)


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


def test_format_cost_allocation_omits_zero_counts():
    from everbot.allocation import Allocation

    alloc = Allocation({"Bravo": 0, "Charlie": 1, "Delta": 2}, 20)
    text = format_cost_allocation(alloc)
    assert "Cost Optimized Allocation" in text
    assert "Charlie: 1" in text
    assert "Delta: 2" in text
    assert "Bravo:" not in text
    assert "Total Hours Provided: 21" in text
    assert "Total Charging Cost: $11" in text



def test_format_allocation_level1_block_still_available():
    alloc = allocate({"Bravo": 2, "Charlie": 3, "Delta": 2}, 16)
    text = format_allocation(alloc)
    assert "Robot Assignment" in text
    assert "Bravo: 1" in text
    assert "Charlie: 1" in text
    assert "Delta: 1" in text
    assert "Total Work Hours Provided: 16" in text
    assert "Client Work Hours Requested: 16" in text


def test_format_comparison_insight():
    comparison = compare_levels({"Bravo": 2, "Charlie": 3, "Delta": 2}, 20)
    text = format_comparison(comparison)
    assert "Level 1 Cost: $12" in text
    assert "Level 2 Cost: $11" in text
    assert "Cost Difference: $1" in text
