"""SwiftRoute — thư viện đọc đề bài và đo lời giải.

    from swiftroute.io_csv import read_instances
    from swiftroute.metrics import evaluate

    for inst in read_instances("data/sample_orders.csv"):
        stats = evaluate(inst, [[3, 9, 4], [7, 1]])

Xem GUIDE.md để có ví dụ đầy đủ.
"""

from .metrics import Stats, evaluate
from .model import Instance, Order

__all__ = ["Instance", "Order", "Stats", "evaluate"]
__version__ = "1.0.0"
