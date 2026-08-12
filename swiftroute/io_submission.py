"""Đọc và ghi file JSON nộp bài.

Trình đọc khoan dung với các biến thể định dạng hay gặp — order_id viết dạng chuỗi,
lồng thêm một tầng ``routes``, thiếu khoá ``team`` — nhưng không tha lỗi cú pháp JSON.
Chi tiết ở DATA_FORMAT.md.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .model import Routes, SolutionSet

_TEAM_KEYS = ("team", "team_name", "teamName", "name", "author", "group")
_SOLUTION_KEYS = ("solutions", "solution", "results", "answers", "instances")
_ROUTE_KEYS = ("routes", "route", "tours", "plan")


class SubmissionError(ValueError):
    """File nộp hỏng tới mức không đọc nổi."""


@dataclass
class Submission:
    team: str
    solutions: SolutionSet
    source: str = ""
    warnings: list[str] = field(default_factory=list)


def _coerce_route(value: object, where: str) -> list[int]:
    if not isinstance(value, (list, tuple)):
        raise SubmissionError(f"{where}: tuyến phải là mảng, nhận được {type(value).__name__}")
    out: list[int] = []
    for item in value:
        if isinstance(item, bool):
            raise SubmissionError(f"{where}: order_id không hợp lệ: {item!r}")
        if isinstance(item, int):
            out.append(item)
        elif isinstance(item, float) and item.is_integer():
            out.append(int(item))
        elif isinstance(item, str) and re.fullmatch(r"\s*-?\d+\s*", item):
            out.append(int(item.strip()))
        else:
            raise SubmissionError(f"{where}: order_id không hợp lệ: {item!r}")
    return out


def _coerce_routes(value: object, where: str, warnings: list[str]) -> Routes:
    # Biến thể hay gặp: {"routes": [[...]]} lồng thêm một tầng.
    if isinstance(value, dict):
        for key in _ROUTE_KEYS:
            if key in value:
                warnings.append(f"{where}: đã bóc tầng lồng {key!r}")
                return _coerce_routes(value[key], where, warnings)
        raise SubmissionError(f"{where}: object không có khoá tuyến nào trong {_ROUTE_KEYS}")

    if not isinstance(value, (list, tuple)):
        raise SubmissionError(f"{where}: phải là mảng các tuyến")

    if value and all(isinstance(x, (int, float, str)) for x in value):
        # Nộp một tuyến phẳng duy nhất thay vì mảng-của-mảng.
        warnings.append(f"{where}: nhận được một tuyến phẳng, đã bọc thành 1 tuyến")
        return [_coerce_route(value, where)]

    return [_coerce_route(r, f"{where}[{i}]") for i, r in enumerate(value)]


def parse_submission(payload: object, source: str = "") -> Submission:
    if not isinstance(payload, dict):
        raise SubmissionError("file nộp phải là một JSON object ở cấp cao nhất")

    warnings: list[str] = []

    team = ""
    for key in _TEAM_KEYS:
        if isinstance(payload.get(key), str) and payload[key].strip():
            team = payload[key].strip()
            break
    if not team:
        team = Path(source).stem if source else "UNKNOWN"
        warnings.append(f"thiếu khoá 'team', dùng tên file: {team!r}")

    raw: object | None = None
    for key in _SOLUTION_KEYS:
        if key in payload:
            raw = payload[key]
            break
    if raw is None:
        # Biến thể: instance_id nằm thẳng ở cấp cao nhất.
        raw = {k: v for k, v in payload.items() if k not in _TEAM_KEYS}
        if not raw:
            raise SubmissionError("không tìm thấy lời giải nào trong file")
        warnings.append("không có khoá 'solutions', đọc instance từ cấp cao nhất")

    if isinstance(raw, list):
        # Biến thể: [{"instance_id": ..., "routes": [...]}, ...]
        converted: dict[str, object] = {}
        for i, item in enumerate(raw):
            if not isinstance(item, dict):
                raise SubmissionError(f"solutions[{i}] phải là object có instance_id")
            iid = item.get("instance_id") or item.get("id")
            if not isinstance(iid, str):
                raise SubmissionError(f"solutions[{i}] thiếu instance_id dạng chuỗi")
            converted[iid] = item
        raw = converted
        warnings.append("solutions ở dạng mảng, đã chuyển sang map theo instance_id")

    if not isinstance(raw, dict):
        raise SubmissionError("solutions phải là object map instance_id -> tuyến")

    solutions: SolutionSet = {}
    for iid, value in raw.items():
        solutions[str(iid).strip()] = _coerce_routes(value, f"solutions[{iid!r}]", warnings)

    return Submission(team=team, solutions=solutions, source=source, warnings=warnings)


def load_submission(path: str | Path) -> Submission:
    path = Path(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SubmissionError(f"{path.name}: JSON không hợp lệ ({exc})") from exc
    return parse_submission(payload, source=str(path))


def write_submission(path: str | Path, team: str, solutions: SolutionSet) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"team": team, "solutions": {k: v for k, v in solutions.items()}}
    path.write_text(json.dumps(payload, indent=1), encoding="utf-8")
