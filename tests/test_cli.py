"""Tests for the interactive CLI flow (menu + Level 1/2/3 runners)."""

from everbot import allocate
from everbot.cli import (
    format_allocation,
    format_comparison,
    format_cost_allocation,
    format_multi_client_plan,
    format_standby_plan,
    run,
    run_level_1,
    run_level_2,
    run_level_3,
    run_level_4,
)
from everbot.comparison import compare_levels
from everbot.multiclient import plan_multi_client
from everbot.standby import plan_standby


def make_io(inputs):
    """Return (input_fn, output_fn, output_lines) driving runners with queued inputs."""
    queue = list(inputs)
    output = []

    def input_fn(_prompt=""):
        return queue.pop(0)

    def output_fn(line=""):
        output.append(line)

    return input_fn, output_fn, output


# --- menu -------------------------------------------------------------------


def test_menu_selects_level_1():
    # Choice 1, then inventory + hours for Level 1.
    input_fn, output_fn, output = make_io(["1", "2", "3", "2", "16"])
    code = run(input_fn, output_fn)
    text = "\n".join(output)
    assert code == 0
    assert "Select allocation level" in text
    assert "Robot Assignment" in text
    assert "Bravo: 1" in text
    assert "Cost Optimized Allocation" not in text
    assert "Additional Standby" not in text


def test_menu_selects_level_2():
    input_fn, output_fn, output = make_io(["2", "2", "3", "2", "20"])
    code = run(input_fn, output_fn)
    text = "\n".join(output)
    assert code == 0
    assert "Cost Optimized Allocation" in text
    assert "Level 1 Cost: $12" in text
    assert "Robot Assignment" not in text


def test_menu_selects_level_3():
    input_fn, output_fn, output = make_io(["3", "1", "1", "1", "21"])
    code = run(input_fn, output_fn)
    text = "\n".join(output)
    assert code == 0
    assert "Active Robot Capacity: 16 hours" in text
    assert "Client Work Requested: 21 hours" in text
    assert "Additional Standby Robots Required:" in text
    assert "Charlie: 1 - cost $3" in text
    assert "Cost Optimized Allocation" not in text


def test_menu_selects_level_4():
    input_fn, output_fn, output = make_io(["4", "2", "3", "2", "12,16,17,10,21"])
    code = run(input_fn, output_fn)
    text = "\n".join(output)
    assert code == 0
    assert "Multi-Client Allocation" in text
    assert "Active Robot Capacity: 37 hours" in text
    assert "Clients: 5" in text
    assert "Client 5: 21 hours requested" in text
    assert "Total Standby Cost: $23" in text
    assert "Robot Assignment" not in text


def test_menu_rejects_invalid_choice():
    input_fn, output_fn, output = make_io(["9"])
    code = run(input_fn, output_fn)
    assert code == 1
    assert "choose level 1, 2, 3, or 4" in "\n".join(output).lower()


# --- Level 2 runner (unchanged behaviour) -----------------------------------


def test_cli_owner_example_1():
    input_fn, output_fn, output = make_io(["2", "3", "2", "20"])
    code = run_level_2(input_fn, output_fn)
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
    code = run_level_2(input_fn, output_fn)
    text = "\n".join(output)

    assert code == 0
    assert "Cost Optimized Allocation" in text
    assert "Bravo: 2" in text
    assert "Total Hours Provided: 6" in text
    assert "Total Charging Cost: $4" in text


def test_cli_reports_level1_infeasible_gracefully():
    input_fn, output_fn, output = make_io(["0", "3", "2", "20"])
    code = run_level_2(input_fn, output_fn)
    text = "\n".join(output)

    assert code == 0
    assert "Cost Optimized Allocation" in text
    assert "Total Charging Cost: $11" in text
    assert "Level 1: infeasible" in text
    assert "each category" in text


def test_cli_reports_insufficient_capacity():
    input_fn, output_fn, output = make_io(["1", "0", "0", "10"])
    code = run_level_2(input_fn, output_fn)
    assert code == 1
    assert "Insufficient robot capacity" in "\n".join(output)


def test_cli_rejects_non_integer_hours():
    input_fn, output_fn, output = make_io(["2", "2", "2", "abc"])
    code = run_level_2(input_fn, output_fn)
    assert code == 1
    assert "Work hours must be a positive integer" in "\n".join(output)


def test_cli_rejects_non_integer_robot_count():
    input_fn, output_fn, output = make_io(["x", "2", "2", "10"])
    code = run_level_2(input_fn, output_fn)
    assert code == 1
    assert "Robot counts must be non-negative integers" in "\n".join(output)


# --- Level 1 runner ---------------------------------------------------------


def test_level_1_runner_owner_example():
    input_fn, output_fn, output = make_io(["2", "3", "2", "16"])
    code = run_level_1(input_fn, output_fn)
    text = "\n".join(output)
    assert code == 0
    assert "Robot Assignment" in text
    assert "Bravo: 1" in text
    assert "Charlie: 1" in text
    assert "Delta: 1" in text
    assert "Total Work Hours Provided: 16" in text
    assert "Client Work Hours Requested: 16" in text
    assert "Cost Optimized Allocation" not in text


# --- Level 3 runner ---------------------------------------------------------


def test_level_3_owner_example():
    input_fn, output_fn, output = make_io(["1", "1", "1", "21"])
    code = run_level_3(input_fn, output_fn)
    text = "\n".join(output)
    assert code == 0
    assert "Active Robot Capacity: 16 hours" in text
    assert "Client Work Requested: 21 hours" in text
    assert "Additional Standby Robots Required:" in text
    assert "Charlie: 1 - cost $3" in text
    # Only the winner — no Bravo/Delta lines.
    assert "Bravo:" not in text.split("Additional")[-1] if "Additional" in text else True
    assert "Delta:" not in text.split("Additional Standby Robots Required:")[-1]


def test_level_3_omits_additional_when_capacity_enough():
    input_fn, output_fn, output = make_io(["1", "1", "1", "16"])
    code = run_level_3(input_fn, output_fn)
    text = "\n".join(output)
    assert code == 0
    assert "Active Robot Capacity: 16 hours" in text
    assert "Client Work Requested: 16 hours" in text
    assert "Additional Standby" not in text


def test_format_standby_plan_colours_off_by_default():
    plan = plan_standby({"Bravo": 1, "Charlie": 1, "Delta": 1}, 21)
    text = format_standby_plan(plan)
    assert "\033[" not in text
    assert "Charlie: 1 - cost $3" in text


def test_format_standby_plan_colours_by_robot_type():
    plan = plan_standby({"Bravo": 1, "Charlie": 1, "Delta": 1}, 21)
    text = format_standby_plan(plan, color=True)
    assert "\033[35m" in text  # magenta for Charlie
    assert "Charlie: 1 - cost $3" in text


# --- formatters -------------------------------------------------------------


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


# --- Level 4 runner ---------------------------------------------------------


def test_level_4_owner_example_input():
    input_fn, output_fn, output = make_io(["2", "3", "2", "12,16,17,10,21"])
    code = run_level_4(input_fn, output_fn)
    text = "\n".join(output)
    assert code == 0
    # Served highest hours first, but labelled by input position.
    order = [line for line in text.splitlines() if line.strip().startswith("Client ")]
    assert [line.strip().split(":")[0] for line in order] == [
        "Client 5",
        "Client 3",
        "Client 2",
        "Client 1",
        "Client 4",
    ]
    assert "Active Robots Allocated: Charlie: 1, Delta: 2 (21 hours)" in text
    assert "Additional Standby Robots Required:" in text
    assert "Bravo: 1 - cost $2" in text
    assert "Delta: 2 - cost $8" in text
    assert "Total Standby Cost: $23" in text


def test_level_4_space_separated_matches_comma_separated():
    input_a, output_a, lines_a = make_io(["2", "3", "2", "12,16,17,10,21"])
    input_b, output_b, lines_b = make_io(["2", "3", "2", "12 16 17 10 21"])
    assert run_level_4(input_a, output_a) == 0
    assert run_level_4(input_b, output_b) == 0
    assert lines_a == lines_b


def test_level_4_single_value_needs_no_standby():
    input_fn, output_fn, output = make_io(["2", "3", "2", "20"])
    code = run_level_4(input_fn, output_fn)
    text = "\n".join(output)
    assert code == 0
    assert "Clients: 1" in text
    assert "Client 1: 20 hours requested" in text
    assert "Active Robots Allocated: Charlie: 1, Delta: 2 (21 hours)" in text
    assert "Additional Standby" not in text
    assert "Total Standby Cost: $0" in text


def test_level_4_rejects_invalid_hours_value():
    input_fn, output_fn, output = make_io(["2", "3", "2", "12,abc"])
    code = run_level_4(input_fn, output_fn)
    assert code == 1
    assert "Work hours must be a positive integer" in "\n".join(output)


def test_level_4_rejects_empty_hours_input():
    input_fn, output_fn, output = make_io(["2", "3", "2", "   "])
    code = run_level_4(input_fn, output_fn)
    assert code == 1
    assert "Work hours must be a positive integer" in "\n".join(output)


def test_level_4_zero_inventory_is_all_standby():
    input_fn, output_fn, output = make_io(["0", "0", "0", "8 6"])
    code = run_level_4(input_fn, output_fn)
    text = "\n".join(output)
    assert code == 0
    assert "Active Robot Capacity: 0 hours" in text
    assert "Active Robots Allocated" not in text
    assert "Total Standby Cost: $8" in text


def test_format_multi_client_plan_colours_standby_by_robot_type():
    plan = plan_multi_client({"Bravo": 1, "Charlie": 1, "Delta": 1}, [21])
    plain = format_multi_client_plan(plan)
    coloured = format_multi_client_plan(plan, color=True)
    assert "\033[" not in plain
    assert "Charlie: 1 - cost $3" in plain
    assert "\033[35m" in coloured  # magenta for Charlie
