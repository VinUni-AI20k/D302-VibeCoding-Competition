"""Đọc/ghi CSV và đọc file nộp.

Trình đọc file nộp phải khoan dung: sinh viên sẽ nộp đủ kiểu biến thể, và loại một đội
vì dấu ngoặc chứ không phải vì thuật toán là cách chấm thi tệ.
"""

from __future__ import annotations

import json

import pytest
from conftest import rebuild

from swiftroute.io_csv import COLUMNS, read_instances, write_instances
from swiftroute.io_submission import (
    SubmissionError,
    load_submission,
    parse_submission,
    write_submission,
)


def test_csv_round_trip_preserves_everything(tmp_path, tiny):
    other = rebuild(tiny, instance_id="tiny2", num_vehicles=5, speed=0.4)
    path = tmp_path / "orders.csv"
    write_instances(path, [tiny, other])

    back = read_instances(path)
    assert [i.instance_id for i in back] == ["tiny", "tiny2"]
    for original, restored in zip([tiny, other], back):
        assert restored.num_vehicles == original.num_vehicles
        assert restored.vehicle_capacity == original.vehicle_capacity
        assert restored.shift_start == original.shift_start
        assert restored.shift_end == original.shift_end
        assert restored.speed == pytest.approx(original.speed)
        assert restored.depot_x == pytest.approx(original.depot_x)
        assert len(restored.orders) == len(original.orders)
        for a, b in zip(original.orders, restored.orders):
            assert (a.id, a.demand, a.ready_time, a.due_time, a.service_time) == (
                b.id,
                b.demand,
                b.ready_time,
                b.due_time,
                b.service_time,
            )
            assert a.x == pytest.approx(b.x)


def test_csv_header_is_the_documented_one(tmp_path, tiny):
    path = tmp_path / "orders.csv"
    write_instances(path, [tiny])
    assert path.read_text(encoding="utf-8").splitlines()[0] == ",".join(COLUMNS)


def test_csv_rejects_inconsistent_instance_parameters(tmp_path, tiny):
    path = tmp_path / "orders.csv"
    write_instances(path, [tiny])
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[2] = lines[2].replace(",2,10,", ",3,10,", 1)  # đổi num_vehicles ở dòng thứ hai
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="không nhất quán"):
        read_instances(path)


def test_csv_rejects_missing_columns(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("instance_id,order_id\nx,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="thiếu cột"):
        read_instances(path)


# ---------------------------------------------------------------- file nộp


def test_canonical_submission():
    sub = parse_submission({"team": "ALPHA", "solutions": {"a": [[1, 2], [3]]}})
    assert sub.team == "ALPHA"
    assert sub.solutions == {"a": [[1, 2], [3]]}
    assert sub.warnings == []


def test_string_order_ids_are_accepted():
    sub = parse_submission({"team": "A", "solutions": {"a": [["1", " 2 "]]}})
    assert sub.solutions == {"a": [[1, 2]]}


def test_nested_routes_key_is_unwrapped():
    sub = parse_submission({"team": "A", "solutions": {"a": {"routes": [[1, 2]]}}})
    assert sub.solutions == {"a": [[1, 2]]}
    assert any("bóc tầng" in w for w in sub.warnings)


def test_flat_single_route_is_wrapped():
    sub = parse_submission({"team": "A", "solutions": {"a": [1, 2, 3]}})
    assert sub.solutions == {"a": [[1, 2, 3]]}
    assert any("tuyến phẳng" in w for w in sub.warnings)


def test_solutions_as_a_list_is_converted():
    sub = parse_submission(
        {"team": "A", "solutions": [{"instance_id": "a", "routes": [[1]]}]}
    )
    assert sub.solutions == {"a": [[1]]}


def test_instances_at_top_level_are_found():
    sub = parse_submission({"team": "A", "a": [[1, 2]], "b": [[3]]})
    assert sub.solutions == {"a": [[1, 2]], "b": [[3]]}


def test_missing_team_falls_back_to_filename(tmp_path):
    path = tmp_path / "TEAM_BRAVO.json"
    path.write_text(json.dumps({"solutions": {"a": [[1]]}}), encoding="utf-8")
    sub = load_submission(path)
    assert sub.team == "TEAM_BRAVO"
    assert any("thiếu khoá 'team'" in w for w in sub.warnings)


def test_alternative_team_keys():
    assert parse_submission({"team_name": "X", "solutions": {"a": [[1]]}}).team == "X"
    assert parse_submission({"group": "Y", "solutions": {"a": [[1]]}}).team == "Y"


def test_float_ids_that_are_whole_numbers_are_accepted():
    assert parse_submission({"team": "A", "solutions": {"a": [[1.0, 2.0]]}}).solutions == {
        "a": [[1, 2]]
    }


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"team": "A", "solutions": {"a": [[1.5]]}},
        {"team": "A", "solutions": {"a": [[None]]}},
        {"team": "A", "solutions": {"a": [[True]]}},
        {"team": "A", "solutions": {"a": 5}},
        {"team": "A"},
    ],
)
def test_genuinely_broken_submissions_are_rejected(payload):
    with pytest.raises(SubmissionError):
        parse_submission(payload)


def test_invalid_json_names_the_file(tmp_path):
    path = tmp_path / "TEAM.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(SubmissionError, match="TEAM.json"):
        load_submission(path)


def test_write_then_read_submission(tmp_path):
    path = tmp_path / "T.json"
    write_submission(path, "T", {"a": [[1, 2]], "b": [[3]]})
    sub = load_submission(path)
    assert sub.team == "T"
    assert sub.solutions == {"a": [[1, 2]], "b": [[3]]}
