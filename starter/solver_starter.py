#!/usr/bin/env python3
"""Lời giải mẫu để bạn có cái chạy được ngay. HÃY THAY BẰNG CODE CỦA BẠN.

Nó làm đúng một việc ngây thơ: xếp đơn theo hạn giao, rồi nhét lần lượt vào tuyến rẻ
nhất mà không vượt tải trọng. Không xét cửa sổ thời gian, không tối ưu thứ tự ghé,
không cân nhắc bỏ đơn. Nó sẽ ra một lời giải hợp lệ và một số điểm rất tệ.

Chạy:
    python solver_starter.py --orders data/sample_orders.csv --out TEN_DOI.json --team TEN_DOI
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _candidate in (_HERE, _HERE.parent, _HERE.parent / "src"):
    if (_candidate / "swiftroute").is_dir():
        sys.path.insert(0, str(_candidate))
        break

from swiftroute.io_csv import read_instances  # noqa: E402
from swiftroute.io_submission import write_submission  # noqa: E402
from swiftroute.metrics import evaluate  # noqa: E402
from swiftroute.model import Instance  # noqa: E402


def solve(instance: Instance) -> list[list[int]]:
    """Trả về danh sách tuyến, mỗi tuyến là thứ tự ghé theo order_id."""
    routes: list[list[int]] = [[] for _ in range(instance.num_vehicles)]
    loads = [0] * instance.num_vehicles

    # Gấp trước, thong thả sau. Đơn giản đến mức thô thiển, nhưng đúng luật.
    pending = sorted(instance.orders, key=lambda o: (o.due_time, o.ready_time))

    for order in pending:
        best_route = -1
        best_extra = math.inf

        for i, route in enumerate(routes):
            if loads[i] + order.demand > instance.vehicle_capacity:
                continue
            if route:
                last = instance.order(route[-1])
                extra = math.hypot(order.x - last.x, order.y - last.y)
            else:
                extra = math.hypot(order.x - instance.depot_x, order.y - instance.depot_y)
            if extra < best_extra:
                best_extra = extra
                best_route = i

        if best_route < 0:
            continue  # không xe nào chở nổi -> bỏ đơn (được phép, nhưng bị phạt)

        routes[best_route].append(order.id)
        loads[best_route] += order.demand

    return [r for r in routes if r]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--team", required=True)
    args = parser.parse_args()

    solutions = {}
    for instance in read_instances(args.orders):
        routes = solve(instance)
        solutions[instance.instance_id] = routes

        stats = evaluate(instance, routes)
        summary = stats.public_summary()
        flag = "" if stats.feasible else "  KHÔNG HỢP LỆ: " + "; ".join(stats.violations)
        print(
            f"{instance.instance_id}: {summary['total_distance_km']:8.1f} km  "
            f"{summary['vehicles_used']:2d} xe  "
            f"bỏ {summary['orders_unserved']:3d} đơn  "
            f"trễ {summary['total_lateness_min']:8.1f} phút  "
            f"ngoài ca {summary['total_overtime_min']:6.1f} phút{flag}"
        )

    write_submission(args.out, args.team, solutions)
    print(f"\nĐã ghi {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
