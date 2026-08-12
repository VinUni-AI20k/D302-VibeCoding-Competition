#!/usr/bin/env python3
"""Kiểm tra file nộp. CÔNG CỤ NÀY ĐƯỢC GIAO CHO THÍ SINH.

Nó cho biết lời giải của bạn có HỢP LỆ không, và các đại lượng thô mà ban tổ chức đo.
Nó KHÔNG cho biết điểm, và cũng không cho biết mỗi đại lượng đáng giá bao nhiêu — phần
đó là bài toán của bạn.

Chạy:
    python validate.py --orders data/sample_orders.csv --submission TEN_DOI.json
    python validate.py --orders data/sample_orders.csv --submission TEN_DOI.json --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _candidate in (_HERE, _HERE.parent / "src"):
    if (_candidate / "swiftroute").is_dir():
        sys.path.insert(0, str(_candidate))
        break

from swiftroute.io_csv import read_instances  # noqa: E402
from swiftroute.io_submission import SubmissionError, load_submission  # noqa: E402
from swiftroute.metrics import evaluate  # noqa: E402

_FIELDS = [
    ("total_distance_km", "tổng quãng đường (km)"),
    ("vehicles_used", "số xe sử dụng"),
    ("orders_served", "số đơn đã giao"),
    ("orders_unserved", "số đơn bỏ"),
    ("num_late_orders", "số đơn giao trễ"),
    ("total_lateness_min", "tổng phút trễ"),
    ("max_lateness_min", "phút trễ lớn nhất"),
    ("num_overtime_routes", "số tuyến về muộn"),
    ("total_overtime_min", "tổng phút ngoài ca"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", required=True, type=Path, help="file CSV đề bài")
    parser.add_argument("--submission", required=True, type=Path, help="file JSON bạn nộp")
    parser.add_argument("--json", action="store_true", help="in ra JSON thay vì bảng")
    args = parser.parse_args()

    instances = read_instances(args.orders)

    try:
        submission = load_submission(args.submission)
    except SubmissionError as exc:
        print(f"KHÔNG ĐỌC ĐƯỢC FILE NỘP: {exc}", file=sys.stderr)
        return 2

    report: dict[str, object] = {"team": submission.team, "instances": {}}
    problems = 0

    for instance in instances:
        routes = submission.solutions.get(instance.instance_id)
        if routes is None:
            report["instances"][instance.instance_id] = {
                "feasible": False,
                "error": "thiếu instance này trong file nộp",
            }
            problems += 1
            continue

        stats = evaluate(instance, routes)
        entry = stats.public_summary()
        if not stats.feasible:
            entry["violations"] = stats.violations
            problems += 1
        report["instances"][instance.instance_id] = entry

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1 if problems else 0

    for warning in submission.warnings:
        print(f"  cảnh báo: {warning}")
    print(f"\nĐội: {submission.team}\n")

    for iid, entry in report["instances"].items():
        if entry.get("error"):
            print(f"{iid}: THIẾU — {entry['error']}")
            continue
        mark = "hợp lệ" if entry["feasible"] else "KHÔNG HỢP LỆ"
        print(f"{iid}: {mark}")
        for key, label in _FIELDS:
            print(f"    {label:24s} {entry[key]}")
        for violation in entry.get("violations", []):
            print(f"    vi phạm: {violation}")
        print()

    if problems:
        print(f"{problems} instance có vấn đề — sửa trước khi nộp.")
    else:
        print("Tất cả instance đều hợp lệ.")
    print("\nCông cụ này không tính điểm. Điểm chỉ có trên bảng xếp hạng.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
