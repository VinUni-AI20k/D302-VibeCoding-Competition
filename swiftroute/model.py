"""Kiểu dữ liệu lõi của bài toán SwiftRoute.

Module này KHÔNG chứa bất kỳ hằng số nào của hàm chi phí. Nó được ship cho thí sinh.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Order:
    id: int
    x: float
    y: float
    demand: int
    ready_time: int
    due_time: int
    service_time: int


@dataclass(frozen=True)
class Instance:
    instance_id: str
    num_vehicles: int
    vehicle_capacity: int
    depot_x: float
    depot_y: float
    shift_start: int
    shift_end: int
    speed: float
    orders: tuple[Order, ...]

    _by_id: dict[int, Order] = field(default_factory=dict, compare=False, repr=False)

    def __post_init__(self) -> None:
        # dataclass frozen -> phải ghi qua object.__setattr__
        object.__setattr__(self, "_by_id", {o.id: o for o in self.orders})

    def order(self, order_id: int) -> Order:
        return self._by_id[order_id]

    def has_order(self, order_id: int) -> bool:
        return order_id in self._by_id

    @property
    def order_ids(self) -> list[int]:
        return [o.id for o in self.orders]

    @property
    def n(self) -> int:
        return len(self.orders)

    def total_demand(self) -> int:
        return sum(o.demand for o in self.orders)

    def dist_depot(self, order_id: int) -> float:
        o = self._by_id[order_id]
        return math.hypot(o.x - self.depot_x, o.y - self.depot_y)

    def dist(self, a: int, b: int) -> float:
        oa, ob = self._by_id[a], self._by_id[b]
        return math.hypot(oa.x - ob.x, oa.y - ob.y)

    def travel_time(self, distance: float) -> float:
        return distance / self.speed


# Một lời giải cho một instance: danh sách các tuyến, mỗi tuyến là thứ tự ghé order_id.
Routes = list[list[int]]

# Lời giải cho toàn bộ bộ đề.
SolutionSet = dict[str, Routes]
