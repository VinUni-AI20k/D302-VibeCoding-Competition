"""Chạy thử trọn vẹn trên bộ sample: đọc đề -> giải -> ghi file -> tự kiểm tra.

Bộ test này đi kèm gói phát cho sinh viên. Nó trả lời đúng một câu hỏi: "môi trường của
mình đã chạy được chưa?" Nếu nó xanh thì bạn nộp bài được.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from swiftroute.io_csv import read_instances
from swiftroute.io_submission import load_submission, write_submission
from swiftroute.metrics import evaluate

ROOT = Path(__file__).resolve().parent.parent


def _sample_csv() -> Path:
    for candidate in (
        ROOT / "data" / "sample_orders.csv",
        ROOT / "data" / "sample" / "sample_orders.csv",
    ):
        if candidate.exists():
            return candidate
    pytest.skip("chưa có bộ sample")


@pytest.fixture(scope="module")
def instances():
    return read_instances(_sample_csv())


def _starter_solve(instance):
    import sys

    for candidate in (ROOT, ROOT / "starter"):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
    from starter.solver_starter import solve

    return solve(instance)


def test_sample_file_parses(instances):
    assert len(instances) >= 2
    for inst in instances:
        assert inst.n > 0
        assert inst.num_vehicles >= 1
        assert inst.vehicle_capacity >= 1
        assert inst.shift_start < inst.shift_end
        assert inst.speed > 0


def test_every_order_can_at_least_be_reached(instances):
    """Kiểm tra tỉnh táo: không đơn nào nằm ngoài tầm với ngay cả khi đi thẳng từ kho."""
    for inst in instances:
        for order in inst.orders:
            arrival = inst.shift_start + inst.travel_time(inst.dist_depot(order.id))
            assert arrival < inst.shift_end, f"{inst.instance_id}: đơn {order.id} bất khả thi"


def test_the_empty_solution_is_valid(instances):
    """Không giao gì cũng hợp lệ — chỉ là bị phạt. Đây là lối thoát khi bí."""
    for inst in instances:
        stats = evaluate(inst, [])
        assert stats.feasible
        assert stats.orders_unserved == inst.n


def test_starter_solver_gives_a_valid_solution(instances):
    for inst in instances:
        stats = evaluate(inst, _starter_solve(inst))
        assert stats.feasible, f"{inst.instance_id}: {stats.violations}"
        assert stats.vehicles_used <= inst.num_vehicles


def test_write_then_read_a_submission(tmp_path, instances):
    solutions = {inst.instance_id: _starter_solve(inst) for inst in instances}
    path = tmp_path / "TEN_DOI.json"
    write_submission(path, "TEN_DOI", solutions)

    back = load_submission(path)
    assert back.team == "TEN_DOI"
    assert set(back.solutions) == {inst.instance_id for inst in instances}
    for inst in instances:
        assert back.solutions[inst.instance_id] == solutions[inst.instance_id]


def test_a_solution_that_breaks_the_rules_is_caught(instances):
    inst = instances[0]
    first = inst.orders[0].id

    duplicated = evaluate(inst, [[first], [first]])
    assert not duplicated.feasible

    unknown = evaluate(inst, [[999999]])
    assert not unknown.feasible

    too_many = evaluate(inst, [[o.id] for o in inst.orders[: inst.num_vehicles + 1]])
    assert not too_many.feasible
