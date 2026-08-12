"""Đo lường phải khớp từng con số với đề bài đã công bố."""

from __future__ import annotations

import pytest
from conftest import rebuild, with_order

from swiftroute.metrics import check_hard_constraints, evaluate, simulate_route


def test_route_distance_and_return_time(tiny):
    trace = simulate_route(tiny, [1, 2], 0)
    assert trace.distance == pytest.approx(12.0)
    assert trace.arrivals == pytest.approx([5.0, 19.0])
    assert trace.return_time == pytest.approx(27.0)
    assert trace.overtime == 0.0
    assert trace.load == 5


def test_arriving_early_means_waiting(tiny):
    # Đơn 2 chưa sẵn sàng cho tới phút 30; xe đến lúc 19 nên phải chờ 11 phút.
    inst = with_order(tiny, 2, ready_time=30)
    trace = simulate_route(inst, [1, 2], 0)
    assert trace.arrivals[1] == pytest.approx(30.0)
    assert trace.return_time == pytest.approx(38.0)
    assert trace.lateness == pytest.approx([0.0, 0.0])
    # Chờ không làm thay đổi quãng đường.
    assert trace.distance == pytest.approx(12.0)


def test_lateness_measured_at_arrival_not_at_completion(tiny):
    # Đến lúc 19, hẹn lúc 10 -> trễ 9. Nếu tính lúc giao xong (24) thì sẽ ra 14.
    inst = with_order(tiny, 2, due_time=10)
    trace = simulate_route(inst, [1, 2], 0)
    assert trace.lateness == pytest.approx([0.0, 9.0])


def test_overtime_counted_from_return_to_depot(tiny):
    inst = rebuild(tiny, shift_end=20)
    trace = simulate_route(inst, [1, 2], 0)
    assert trace.overtime == pytest.approx(7.0)


def test_shift_start_offsets_everything(tiny):
    inst = rebuild(tiny, shift_start=100, shift_end=200)
    trace = simulate_route(inst, [1, 2], 0)
    assert trace.arrivals == pytest.approx([105.0, 119.0])
    assert trace.return_time == pytest.approx(127.0)


def test_speed_scales_travel_but_not_service_or_distance(tiny):
    inst = rebuild(tiny, speed=2.0)
    trace = simulate_route(inst, [1, 2], 0)
    assert trace.distance == pytest.approx(12.0)
    # 12 km ở tốc độ 2 là 6 phút chạy, cộng 15 phút dừng vốn không phụ thuộc tốc độ.
    assert trace.return_time == pytest.approx(21.0)


def test_unserved_orders_are_allowed(tiny):
    stats = evaluate(tiny, [[1]])
    assert stats.feasible
    assert stats.served_ids == [1]
    assert stats.unserved_ids == [2]
    assert stats.vehicles_used == 1


def test_empty_routes_do_not_count_as_vehicles(tiny):
    stats = evaluate(tiny, [[], [1, 2], []])
    assert stats.feasible
    assert stats.vehicles_used == 1


def test_empty_solution_is_feasible_but_serves_nothing(tiny):
    stats = evaluate(tiny, [])
    assert stats.feasible
    assert stats.vehicles_used == 0
    assert stats.unserved_ids == [1, 2]
    assert stats.total_distance == 0.0


# ------------------------------------------------------------------- luật cứng


def test_duplicate_order_id_is_a_violation(tiny):
    violations = check_hard_constraints(tiny, [[1, 2], [1]])
    assert any("lặp" in v for v in violations)


def test_unknown_order_id_is_a_violation(tiny):
    violations = check_hard_constraints(tiny, [[1, 99]])
    assert any("không tồn tại" in v for v in violations)


def test_too_many_vehicles_is_a_violation(tiny):
    violations = check_hard_constraints(tiny, [[1], [2], []])
    assert violations == []  # tuyến rỗng không tính
    inst = rebuild(tiny, num_vehicles=1)
    violations = check_hard_constraints(inst, [[1], [2]])
    assert any("vượt quá num_vehicles" in v for v in violations)


def test_capacity_overload_is_a_violation(tiny):
    inst = rebuild(tiny, vehicle_capacity=4)
    violations = check_hard_constraints(inst, [[1, 2]])
    assert any("vehicle_capacity" in v for v in violations)
    # Tách thành hai xe thì lại hợp lệ.
    assert check_hard_constraints(inst, [[1], [2]]) == []


def test_infeasible_solution_still_reports_useful_numbers(tiny):
    stats = evaluate(tiny, [[1, 99]])
    assert not stats.feasible
    assert stats.violations
    # id lạ bị loại ra, phần còn lại vẫn được mô phỏng để báo lỗi cho hữu ích.
    assert stats.total_distance == pytest.approx(10.0)


# ------------------------------------------------------- những gì thí sinh thấy


def test_public_summary_never_exposes_cost(tiny):
    stats = evaluate(tiny, [[1, 2]])
    summary = stats.public_summary()
    assert set(summary) == {
        "feasible",
        "total_distance_km",
        "vehicles_used",
        "orders_served",
        "orders_unserved",
        "num_late_orders",
        "total_lateness_min",
        "max_lateness_min",
        "total_overtime_min",
        "num_overtime_routes",
    }
    assert not any("cost" in k or "score" in k for k in summary)


def test_aggregate_lateness_fields(tiny):
    inst = with_order(tiny, 1, due_time=1)
    inst = with_order(inst, 2, due_time=10)
    stats = evaluate(inst, [[1, 2]])
    assert stats.lateness_per_order == pytest.approx([4.0, 9.0])
    assert stats.total_lateness == pytest.approx(13.0)
    assert stats.max_lateness == pytest.approx(9.0)
    assert stats.num_late_orders == 2
