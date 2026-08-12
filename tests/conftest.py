from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Chạy được ở cả hai bố cục: repo ban tổ chức (package nằm trong src/) và repo phát cho
# sinh viên (package nằm ngay ở gốc). Nhờ vậy đúng bộ test đó chạy được ở cả hai nơi.
for _candidate in (ROOT, ROOT / "src", ROOT / "tools"):
    if _candidate.is_dir():
        sys.path.insert(0, str(_candidate))

from swiftroute.model import Instance, Order  # noqa: E402


@pytest.fixture
def root() -> Path:
    return ROOT


@pytest.fixture
def tiny() -> Instance:
    """Instance nhỏ với số liệu tròn, tính tay được.

    kho ở (0,0), tốc độ 1 km/phút nên km và phút trùng nhau.
        đơn 1 tại (3,4)  -> cách kho 5
        đơn 2 tại (3,0)  -> cách kho 3, cách đơn 1 là 4
    Tuyến [1, 2] chạy: đến đơn 1 lúc t=5, xong lúc 15, đến đơn 2 lúc 19, xong lúc 24,
    về kho lúc 27, tổng quãng đường 5 + 4 + 3 = 12.
    """
    return Instance(
        instance_id="tiny",
        num_vehicles=2,
        vehicle_capacity=10,
        depot_x=0.0,
        depot_y=0.0,
        shift_start=0,
        shift_end=100,
        speed=1.0,
        orders=(
            Order(id=1, x=3.0, y=4.0, demand=2, ready_time=0, due_time=100, service_time=10),
            Order(id=2, x=3.0, y=0.0, demand=3, ready_time=0, due_time=100, service_time=5),
        ),
    )


def rebuild(instance: Instance, **changes) -> Instance:
    """Sao chép instance với vài trường bị thay đổi."""
    fields = {
        "instance_id": instance.instance_id,
        "num_vehicles": instance.num_vehicles,
        "vehicle_capacity": instance.vehicle_capacity,
        "depot_x": instance.depot_x,
        "depot_y": instance.depot_y,
        "shift_start": instance.shift_start,
        "shift_end": instance.shift_end,
        "speed": instance.speed,
        "orders": instance.orders,
    }
    fields.update(changes)
    return Instance(**fields)


def with_order(instance: Instance, order_id: int, **changes) -> Instance:
    orders = []
    for o in instance.orders:
        if o.id == order_id:
            fields = {
                "id": o.id,
                "x": o.x,
                "y": o.y,
                "demand": o.demand,
                "ready_time": o.ready_time,
                "due_time": o.due_time,
                "service_time": o.service_time,
            }
            fields.update(changes)
            orders.append(Order(**fields))
        else:
            orders.append(o)
    return rebuild(instance, orders=tuple(orders))
