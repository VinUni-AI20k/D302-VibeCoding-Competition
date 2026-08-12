"""SwiftRoute — Last-Mile Delivery Challenge.

Ranh giới quan trọng nhất của package này:

    ship được cho thí sinh   : model, metrics, io_csv, io_submission
    chỉ ban tổ chức          : weights, cost, scoring, generator, solvers

Đừng import nhóm thứ hai từ nhóm thứ nhất. tests/test_no_leak.py canh điều đó.
"""

from .metrics import Stats, evaluate
from .model import Instance, Order

__all__ = ["Instance", "Order", "Stats", "evaluate"]
__version__ = "1.0.0"
