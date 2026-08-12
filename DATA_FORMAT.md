# Định dạng dữ liệu

## Đề bài — một file CSV

Một dòng là một đơn hàng. Các cột tham số của instance lặp lại trên mọi dòng thuộc cùng
instance. Dư thừa, nhưng nhờ vậy chỉ cần một dòng pandas là xong.

```
instance_id,num_vehicles,vehicle_capacity,depot_x,depot_y,shift_start,shift_end,speed,order_id,x,y,demand,ready_time,due_time,service_time
sample_01,2,175,14.0000,14.0000,480,1020,0.6000,1,11.482,17.903,7,612,913,9
sample_01,2,175,14.0000,14.0000,480,1020,0.6000,2,19.771,8.264,3,547,872,12
```

Đọc bằng pandas:

```python
import pandas as pd

df = pd.read_csv("data/sample_orders.csv")
for instance_id, group in df.groupby("instance_id", sort=False):
    head = group.iloc[0]
    num_vehicles = int(head.num_vehicles)
    capacity = int(head.vehicle_capacity)
    orders = group[["order_id", "x", "y", "demand",
                    "ready_time", "due_time", "service_time"]]
```

Hoặc dùng thư viện có sẵn trong gói:

```python
from swiftroute.io_csv import read_instances

for instance in read_instances("data/sample_orders.csv"):
    print(instance.instance_id, instance.num_vehicles, len(instance.orders))
    print(instance.dist(1, 2))          # khoảng cách giữa hai đơn
    print(instance.dist_depot(1))       # khoảng cách từ kho tới một đơn
```

Đơn vị: toạ độ tính bằng km, thời gian tính bằng phút kể từ 00:00 (nên `480` là 08:00),
`speed` tính bằng km mỗi phút.

## File nộp — một file JSON

**Một đội một file.** Đặt tên theo tên đội, ví dụ `TEAM_ALPHA.json`.

```json
{
  "team": "TEAM_ALPHA",
  "solutions": {
    "public_01": [[7, 3, 12], [5, 1, 9, 4]],
    "public_02": [[2, 8], [6, 11, 1]]
  }
}
```

- `solutions` là map từ `instance_id` sang **danh sách các tuyến**.
- Mỗi tuyến là danh sách `order_id` **theo đúng thứ tự ghé**.
- Xe luôn xuất phát và kết thúc ở kho; đừng đưa kho vào danh sách.
- Tuyến rỗng bị bỏ qua, không tính là một xe được dùng.
- Đơn không xuất hiện trong tuyến nào = bỏ đơn. Được phép, bị phạt.
- Phải có đủ **mọi** `instance_id` của bộ đề. Thiếu bài nào thì bài đó 0 điểm.

Ghi file bằng thư viện có sẵn:

```python
from swiftroute.io_submission import write_submission

write_submission("TEAM_ALPHA.json", "TEAM_ALPHA", solutions)
```

## Trình đọc khoan dung tới đâu

Trình chấm cố hiểu file của bạn thay vì bắt lỗi vặt. Những dạng sau đều được chấp nhận:

- `order_id` viết dưới dạng chuỗi: `["7", "3"]`
- lồng thêm một tầng: `"public_01": {"routes": [[7, 3]]}`
- `solutions` ở dạng mảng: `[{"instance_id": "public_01", "routes": [[7, 3]]}]`
- thiếu khoá `team` — khi đó tên file được dùng làm tên đội
- các khoá thay thế: `team_name`, `results`, `answers`

Những thứ **không** được tha:

- JSON sai cú pháp
- `order_id` không phải số nguyên
- tuyến không phải là mảng

Đừng dựa vào sự khoan dung này. Cứ chạy `validate.py` trước khi nộp.

## Tự kiểm tra trước khi nộp

```bash
python validate.py --orders data/sample_orders.csv --submission TEAM_ALPHA.json
```

Thay `data/sample_orders.csv` bằng file đề thật khi ban tổ chức phát ra.

Lệnh này in ra, cho từng instance: hợp lệ hay không, tổng km, số xe dùng, số đơn giao,
số đơn bỏ, số đơn trễ, tổng phút trễ, phút trễ lớn nhất, số tuyến về muộn, tổng phút
ngoài ca.

Nó **không** in điểm. Đó không phải lỗi.
