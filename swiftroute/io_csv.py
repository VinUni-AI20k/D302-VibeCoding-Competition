"""Đọc/ghi bộ đề dưới dạng một file CSV phi chuẩn hoá.

Mỗi dòng là một đơn hàng; các cột tham số của instance lặp lại trên mọi dòng thuộc
instance đó. Dư thừa nhưng đọc bằng pandas là xong một dòng lệnh.

Module này được ship cho thí sinh.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .model import Instance, Order

COLUMNS = [
    "instance_id",
    "num_vehicles",
    "vehicle_capacity",
    "depot_x",
    "depot_y",
    "shift_start",
    "shift_end",
    "speed",
    "order_id",
    "x",
    "y",
    "demand",
    "ready_time",
    "due_time",
    "service_time",
]

_INSTANCE_COLS = (
    "num_vehicles",
    "vehicle_capacity",
    "depot_x",
    "depot_y",
    "shift_start",
    "shift_end",
    "speed",
)


def write_instances(path: str | Path, instances: list[Instance]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        for inst in instances:
            head = {
                "instance_id": inst.instance_id,
                "num_vehicles": inst.num_vehicles,
                "vehicle_capacity": inst.vehicle_capacity,
                "depot_x": f"{inst.depot_x:.4f}",
                "depot_y": f"{inst.depot_y:.4f}",
                "shift_start": inst.shift_start,
                "shift_end": inst.shift_end,
                "speed": f"{inst.speed:.4f}",
            }
            for o in inst.orders:
                writer.writerow(
                    {
                        **head,
                        "order_id": o.id,
                        "x": f"{o.x:.4f}",
                        "y": f"{o.y:.4f}",
                        "demand": o.demand,
                        "ready_time": o.ready_time,
                        "due_time": o.due_time,
                        "service_time": o.service_time,
                    }
                )


def read_instances(path: str | Path) -> list[Instance]:
    """Đọc CSV, giữ nguyên thứ tự instance xuất hiện lần đầu."""
    path = Path(path)
    with path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    if not rows:
        raise ValueError(f"{path} rỗng")

    missing = [c for c in COLUMNS if c not in rows[0]]
    if missing:
        raise ValueError(f"{path} thiếu cột: {missing}")

    order_map: dict[str, list[Order]] = {}
    params: dict[str, dict[str, float]] = {}
    sequence: list[str] = []

    for line_no, row in enumerate(rows, start=2):
        iid = row["instance_id"].strip()
        if iid not in order_map:
            order_map[iid] = []
            sequence.append(iid)
            params[iid] = {c: float(row[c]) for c in _INSTANCE_COLS}
        else:
            current = {c: float(row[c]) for c in _INSTANCE_COLS}
            if current != params[iid]:
                raise ValueError(
                    f"{path}:{line_no} tham số của instance {iid!r} không nhất quán"
                )
        order_map[iid].append(
            Order(
                id=int(row["order_id"]),
                x=float(row["x"]),
                y=float(row["y"]),
                demand=int(row["demand"]),
                ready_time=int(row["ready_time"]),
                due_time=int(row["due_time"]),
                service_time=int(row["service_time"]),
            )
        )

    instances: list[Instance] = []
    for iid in sequence:
        p = params[iid]
        ids = [o.id for o in order_map[iid]]
        if len(set(ids)) != len(ids):
            raise ValueError(f"instance {iid!r} có order_id trùng trong CSV")
        instances.append(
            Instance(
                instance_id=iid,
                num_vehicles=int(p["num_vehicles"]),
                vehicle_capacity=int(p["vehicle_capacity"]),
                depot_x=p["depot_x"],
                depot_y=p["depot_y"],
                shift_start=int(p["shift_start"]),
                shift_end=int(p["shift_end"]),
                speed=p["speed"],
                orders=tuple(order_map[iid]),
            )
        )
    return instances


def read_instance_map(path: str | Path) -> dict[str, Instance]:
    return {inst.instance_id: inst for inst in read_instances(path)}
