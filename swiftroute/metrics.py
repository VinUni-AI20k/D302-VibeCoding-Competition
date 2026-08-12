"""Đo lường thuần tuý một lời giải: khả thi hay không, và các đại lượng thô.

QUAN TRỌNG — module này được ship cho thí sinh.
Nó KHÔNG được chứa bất kỳ trọng số chi phí nào. Việc quy đổi các đại lượng thô sang
tiền nằm ở ``swiftroute.cost``, module đó không bao giờ rời khỏi máy ban tổ chức.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .model import Instance, Routes


@dataclass
class RouteTrace:
    """Kết quả mô phỏng một tuyến."""

    vehicle_index: int
    order_ids: list[int]
    load: int
    distance: float
    return_time: float
    overtime: float
    arrivals: list[float] = field(default_factory=list)
    lateness: list[float] = field(default_factory=list)


@dataclass
class Stats:
    """Các đại lượng thô của một lời giải. Không có tiền, không có điểm."""

    instance_id: str
    feasible: bool
    violations: list[str]

    total_distance: float = 0.0
    vehicles_used: int = 0
    served_ids: list[int] = field(default_factory=list)
    unserved_ids: list[int] = field(default_factory=list)

    lateness_per_order: list[float] = field(default_factory=list)
    overtime_per_route: list[float] = field(default_factory=list)
    routes: list[RouteTrace] = field(default_factory=list)

    @property
    def orders_served(self) -> int:
        return len(self.served_ids)

    @property
    def orders_unserved(self) -> int:
        return len(self.unserved_ids)

    @property
    def total_lateness(self) -> float:
        return sum(self.lateness_per_order)

    @property
    def max_lateness(self) -> float:
        return max(self.lateness_per_order, default=0.0)

    @property
    def num_late_orders(self) -> int:
        return sum(1 for v in self.lateness_per_order if v > 1e-9)

    @property
    def total_overtime(self) -> float:
        return sum(self.overtime_per_route)

    @property
    def num_overtime_routes(self) -> int:
        return sum(1 for v in self.overtime_per_route if v > 1e-9)

    def public_summary(self) -> dict[str, float | int | bool]:
        """Đúng những gì thí sinh được phép nhìn thấy."""
        return {
            "feasible": self.feasible,
            "total_distance_km": round(self.total_distance, 3),
            "vehicles_used": self.vehicles_used,
            "orders_served": self.orders_served,
            "orders_unserved": self.orders_unserved,
            "num_late_orders": self.num_late_orders,
            "total_lateness_min": round(self.total_lateness, 2),
            "max_lateness_min": round(self.max_lateness, 2),
            "total_overtime_min": round(self.total_overtime, 2),
            "num_overtime_routes": self.num_overtime_routes,
        }


def check_hard_constraints(instance: Instance, routes: Routes) -> list[str]:
    """Trả về danh sách vi phạm ràng buộc cứng. Rỗng nghĩa là hợp lệ."""
    violations: list[str] = []
    non_empty = [r for r in routes if r]

    if len(non_empty) > instance.num_vehicles:
        violations.append(
            f"dùng {len(non_empty)} xe, vượt quá num_vehicles={instance.num_vehicles}"
        )

    seen: set[int] = set()
    duplicates: list[int] = []
    unknown: list[int] = []
    for route in routes:
        for oid in route:
            if not instance.has_order(oid):
                unknown.append(oid)
                continue
            if oid in seen:
                duplicates.append(oid)
            seen.add(oid)

    if unknown:
        violations.append(f"order_id không tồn tại: {sorted(set(unknown))[:10]}")
    if duplicates:
        violations.append(f"order_id bị lặp: {sorted(set(duplicates))[:10]}")

    # Đánh số theo vị trí trong file thí sinh nộp, không theo danh sách đã lọc tuyến rỗng
    # — người đọc thông báo lỗi đang nhìn vào file của chính họ.
    for i, route in enumerate(routes):
        if not route:
            continue
        load = sum(instance.order(o).demand for o in route if instance.has_order(o))
        if load > instance.vehicle_capacity:
            violations.append(
                f"tuyến #{i} chở {load} > vehicle_capacity={instance.vehicle_capacity}"
            )

    return violations


def simulate_route(instance: Instance, route: list[int], vehicle_index: int) -> RouteTrace:
    """Mô phỏng một tuyến theo đúng luật đã công bố trong đề."""
    t = float(instance.shift_start)
    prev_x, prev_y = instance.depot_x, instance.depot_y
    distance = 0.0
    load = 0
    arrivals: list[float] = []
    lateness: list[float] = []

    for oid in route:
        o = instance.order(oid)
        step = ((o.x - prev_x) ** 2 + (o.y - prev_y) ** 2) ** 0.5
        distance += step
        t += instance.travel_time(step)
        if t < o.ready_time:
            t = float(o.ready_time)  # đến sớm thì chờ
        arrivals.append(t)
        lateness.append(max(0.0, t - o.due_time))
        t += o.service_time
        load += o.demand
        prev_x, prev_y = o.x, o.y

    back = ((instance.depot_x - prev_x) ** 2 + (instance.depot_y - prev_y) ** 2) ** 0.5
    distance += back
    t += instance.travel_time(back)

    return RouteTrace(
        vehicle_index=vehicle_index,
        order_ids=list(route),
        load=load,
        distance=distance,
        return_time=t,
        overtime=max(0.0, t - instance.shift_end),
        arrivals=arrivals,
        lateness=lateness,
    )


def evaluate(instance: Instance, routes: Routes) -> Stats:
    """Đo một lời giải. Luôn trả về Stats, kể cả khi không khả thi."""
    violations = check_hard_constraints(instance, routes)
    stats = Stats(
        instance_id=instance.instance_id,
        feasible=not violations,
        violations=violations,
    )

    if violations:
        # Vẫn cố mô phỏng để báo lỗi hữu ích, nhưng chỉ với các id hợp lệ.
        routes = [[o for o in r if instance.has_order(o)] for r in routes]

    served: set[int] = set()
    non_empty = [r for r in routes if r]
    for i, route in enumerate(non_empty):
        trace = simulate_route(instance, route, i)
        stats.routes.append(trace)
        stats.total_distance += trace.distance
        stats.overtime_per_route.append(trace.overtime)
        stats.lateness_per_order.extend(trace.lateness)
        served.update(route)

    stats.vehicles_used = len(non_empty)
    stats.served_ids = sorted(served)
    stats.unserved_ids = [o.id for o in instance.orders if o.id not in served]
    return stats
