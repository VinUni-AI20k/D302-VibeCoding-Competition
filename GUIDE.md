# Hướng dẫn từng bước

Tài liệu này dắt bạn từ con số không đến một lời giải nộp được, rồi chỉ đường để làm nó
tốt lên. Không cần biết trước gì về bài toán định tuyến.

---

## Bước 0 — Kiểm tra máy

Cần Python 3.10 trở lên:

```bash
python --version
```

Không cần cài thư viện nào. Nếu muốn chắc chắn mọi thứ ổn:

```bash
pip install pytest
pytest
```

Xanh hết là xong. (Nếu máy bạn gõ `python` không ra, thử `python3`.)

---

## Bước 1 — Chạy thử một vòng

```bash
python starter/solver_starter.py --orders data/sample_orders.csv --out TEN_DOI.json --team TEN_DOI
python validate.py --orders data/sample_orders.csv --submission TEN_DOI.json
```

Bạn sẽ thấy đại loại thế này:

```
sample_01: hợp lệ
    tổng quãng đường (km)    142.318
    số xe sử dụng            2
    số đơn đã giao           25
    số đơn bỏ                0
    số đơn giao trễ          6
    tổng phút trễ            221.4
    ...
```

Đó là toàn bộ những gì bạn được nhìn thấy. Không có điểm. Không có chi phí. **Cố ý đấy.**

---

## Bước 2 — Hiểu đề bài

### Bối cảnh

Một kho ở giữa bản đồ. Một đội xe **giống hệt nhau**. Mỗi xe rời kho lúc `shift_start`,
đi giao một loạt đơn, rồi quay về kho.

Mỗi đơn hàng có:

- **vị trí** `x, y` (đơn vị km)
- **khối lượng** `demand` — cộng dồn lại không được vượt tải trọng xe
- **cửa sổ thời gian** `[ready_time, due_time]` — đến sớm thì phải **đứng chờ**; đến muộn
  thì **bị phạt** nhưng vẫn giao được
- **thời gian dừng** `service_time` — số phút xe đứng lại để giao

Mọi mốc thời gian tính bằng **phút kể từ 00:00**. Nên `480` là 8 giờ sáng.

### Cách tính thời gian của một tuyến

Đây là chỗ hay sai nhất, nên đọc kỹ:

```
Xe rời kho lúc shift_start.
Với mỗi đơn trong tuyến:
    cộng thêm thời gian chạy = khoảng cách / speed
    NẾU tới sớm hơn ready_time  ->  đứng chờ tới ready_time
    ghi lại "giờ đến"
    cộng thêm service_time
Cuối cùng chạy về kho.
```

Hai điều rút ra:

1. **Chờ là có thật.** Ghé một khách quá sớm khiến xe đứng không, và mọi khách phía sau
   trong tuyến bị đẩy lùi theo.
2. **Trễ tính lúc ĐẾN**, không phải lúc giao xong.

### Bốn luật cứng — phạm là mất trắng bài đó

1. Mỗi đơn xuất hiện **tối đa một lần** trong toàn bộ các tuyến.
2. Không được bịa `order_id` không có thật.
3. Số tuyến không rỗng **không vượt quá** `num_vehicles`.
4. Tổng `demand` mỗi tuyến **không vượt quá** `vehicle_capacity`.

Chỉ instance vi phạm bị 0 điểm, các instance khác không sao.

### Ba luật mềm — không mất bài, chỉ tốn tiền

- Giao sau `due_time` → phạt.
- Về kho sau `shift_end` → phạt.
- **Không giao một đơn** → phạt. Nhưng hợp lệ. Và đôi khi là đúng.

---

## Bước 3 — Đọc dữ liệu

File CSV có một dòng cho mỗi đơn hàng. Các cột thông tin chung của đề lặp lại trên mọi
dòng — hơi thừa, nhưng đổi lại đọc bằng pandas là xong một dòng.

**Cách 1 — dùng thư viện có sẵn (khuyến nghị):**

```python
from swiftroute.io_csv import read_instances

for inst in read_instances("data/sample_orders.csv"):
    print(inst.instance_id, inst.n, "đơn,", inst.num_vehicles, "xe")

    for o in inst.orders:
        print(o.id, o.x, o.y, o.demand, o.ready_time, o.due_time, o.service_time)

    inst.dist(3, 9)        # khoảng cách giữa đơn 3 và đơn 9
    inst.dist_depot(3)     # khoảng cách từ kho tới đơn 3
    inst.travel_time(12.5) # 12.5 km mất bao nhiêu phút
```

**Cách 2 — pandas, nếu bạn quen hơn:**

```python
import pandas as pd

df = pd.read_csv("data/sample_orders.csv")
for instance_id, g in df.groupby("instance_id", sort=False):
    num_vehicles = int(g.iloc[0].num_vehicles)
    capacity = int(g.iloc[0].vehicle_capacity)
```

---

## Bước 4 — Viết solver đầu tiên

Lời giải cho một instance là **danh sách các tuyến**, mỗi tuyến là danh sách `order_id`
theo đúng thứ tự ghé.

```python
[[7, 3, 12], [5, 1, 9, 4]]     # xe 1 ghé 7 rồi 3 rồi 12; xe 2 ghé 5, 1, 9, 4
```

Không đưa kho vào danh sách — xe mặc nhiên xuất phát và kết thúc ở kho.

Một solver tối giản, nhét đơn vào xe nào còn chỗ:

```python
from swiftroute.io_csv import read_instances
from swiftroute.io_submission import write_submission
from swiftroute.metrics import evaluate


def solve(inst):
    routes = [[] for _ in range(inst.num_vehicles)]
    loads = [0] * inst.num_vehicles

    for order in sorted(inst.orders, key=lambda o: o.due_time):
        for i in range(inst.num_vehicles):
            if loads[i] + order.demand <= inst.vehicle_capacity:
                routes[i].append(order.id)
                loads[i] += order.demand
                break
        # không xe nào chở nổi -> bỏ đơn, hợp lệ, chịu phạt

    return [r for r in routes if r]


solutions = {}
for inst in read_instances("data/sample_orders.csv"):
    routes = solve(inst)
    print(inst.instance_id, evaluate(inst, routes).public_summary())
    solutions[inst.instance_id] = routes

write_submission("TEN_DOI.json", "TEN_DOI", solutions)
```

`evaluate` chính là bộ mô phỏng mà ban tổ chức dùng để chấm. Gọi bao nhiêu lần tuỳ thích
trong vòng lặp tìm kiếm của bạn:

```python
stats = evaluate(inst, routes)

stats.feasible              # có phạm luật cứng không
stats.violations            # nếu có thì phạm gì
stats.total_distance        # tổng km
stats.vehicles_used         # số xe dùng
stats.unserved_ids          # các đơn bị bỏ
stats.lateness_per_order    # số phút trễ của TỪNG đơn
stats.overtime_per_route    # số phút về muộn của TỪNG tuyến
stats.routes[0].arrivals    # giờ đến từng điểm, rất hữu ích khi debug
```

---

## Bước 5 — Đây mới là bài toán thật

Bạn đã có lời giải hợp lệ. Giờ phải làm nó **rẻ**. Nhưng "rẻ" nghĩa là gì?

Chi phí là một hàm **tăng** theo đúng năm đại lượng này:

1. tổng quãng đường
2. số xe sử dụng
3. mức độ trễ hẹn
4. thời gian làm ngoài ca
5. các đơn bị bỏ (có tính khối lượng)

Không có gì ngoài năm cái này. Không cái nào bị bỏ qua. **Trọng số thì không công bố.**

Nên việc đầu tiên bạn cần làm là **tự viết hàm chi phí của riêng mình**:

```python
def my_cost(inst, routes):
    s = evaluate(inst, routes)
    if not s.feasible:
        return float("inf")

    return (
        A * s.total_distance
        + B * s.vehicles_used
        + C * sum(s.lateness_per_order)          # thật sự tuyến tính à?
        + D * sum(s.overtime_per_route)
        + E * len(s.unserved_ids)                # thật sự không phụ thuộc demand à?
    )
```

`A B C D E` là **giả thuyết của bạn**. Mọi thứ về sau đều dựa lên chúng. Đoán sai thì
thuật toán dù giỏi đến đâu cũng đang leo nhầm ngọn núi.

Vài câu để tự hỏi:

- Một chiếc xe thêm vào đáng giá bao nhiêu **km**? 10 km? 100 km? Con số này thay đổi
  hoàn toàn hình dạng lời giải tốt.
- Trễ 200 phút có tệ đúng bằng **hai lần** trễ 100 phút không? Hay tệ hơn thế nhiều?
- Bỏ một đơn đắt hơn hay rẻ hơn việc chạy hẳn một chuyến riêng cho nó?
- Đơn nặng bị bỏ có tệ hơn đơn nhẹ bị bỏ không?

Bạn có hai nguồn thông tin để trả lời:

- **`validate.py`** cho bạn năm đại lượng đo được. Không cho giá.
- **Bảng xếp hạng** cho bạn một con số điểm sau mỗi đợt chấm. Bạn được phép nộp nhiều
  lần và quan sát điểm nhúc nhích ra sao. Việc này hoàn toàn hợp lệ và được khuyến khích.

Một cảnh báo thật lòng: **bộ public không kích hoạt cả năm thành phần.** Sẽ có thành
phần luôn bằng 0 trên bộ public. Đừng kết luận nó không quan trọng — bộ private thì kích
hoạt hết, và mạnh.

---

## Bước 6 — Làm lời giải tốt lên

Theo thứ tự đáng làm trước:

**a. Xây dựng thông minh hơn.** Đừng nhét đơn vào xe đầu tiên còn chỗ. Với mỗi đơn, thử
chèn vào **mọi vị trí trong mọi tuyến**, chọn chỗ làm chi phí tăng ít nhất.

```python
best = None
for r in range(len(routes)):
    for pos in range(len(routes[r]) + 1):
        candidate = routes[r][:pos] + [order.id] + routes[r][pos:]
        ...  # tính chi phí, giữ phương án rẻ nhất
```

**b. Chèn theo "hối tiếc".** Thay vì luôn chèn đơn rẻ nhất, hãy chèn đơn mà **nếu để lát
nữa mới chèn thì sẽ đắt hơn nhiều nhất**. Tức là chọn đơn có chênh lệch lớn nhất giữa
chỗ tốt nhất và chỗ tốt nhì. Thường tốt hơn hẳn tham lam thuần.

**c. Cải thiện cục bộ.** Có lời giải rồi thì thử vặn nó:

- dời một đơn sang tuyến khác
- đổi chỗ hai đơn giữa hai tuyến
- đảo ngược một đoạn trong cùng tuyến (2-opt)
- dời một đoạn 2–3 đơn liền nhau sang chỗ khác (or-opt)

Cứ nhận mọi thay đổi làm chi phí giảm, lặp tới khi không cải thiện được nữa.

**d. Thoát khỏi cực trị địa phương.** Cải thiện cục bộ sẽ kẹt. Hai cách kinh điển:

- **Phá rồi sửa:** gỡ ngẫu nhiên 10–30 đơn ra khỏi lời giải, chèn lại bằng cách tốt
  nhất bạn có. Lặp hàng nghìn lần. Đơn giản mà cực mạnh.
- **Luyện kim mô phỏng:** thỉnh thoảng chấp nhận cả thay đổi làm xấu đi, với xác suất
  giảm dần theo thời gian.

**e. Cân nhắc bỏ đơn cho tử tế.** Nếu chèn một đơn làm chi phí tăng nhiều hơn tiền phạt
bỏ nó, thì **đừng chèn**. Solver của bạn nên tự quyết định điều này, chứ không nên mặc
định giao hết.

---

## Bước 7 — Trước khi nộp

Bắt buộc:

```bash
python validate.py --orders <file_đề>.csv --submission TEN_DOI.json
```

Kiểm tra đủ ba điều:

- [ ] Mọi instance đều báo **hợp lệ**
- [ ] File nộp có **đủ mọi `instance_id`** của bộ đề (thiếu bài nào bài đó 0 điểm)
- [ ] Tên file là **tên đội** của bạn, ví dụ `TEAM_ALPHA.json`

Rồi đính kèm file vào kênh Discord. Nộp lại bao nhiêu lần cũng được — lần cuối cùng
trước giờ đóng cổng là lần được tính.

---

## Bước 8 — Chuẩn bị cho vòng private

Đây là chỗ nhiều đội mất điểm oan, nên đọc kỹ.

Bộ private được phát ra **sát giờ kết thúc**, và cổng nộp chỉ mở khoảng 45 phút. Nó có
20 bài, to hơn và chặt hơn bộ public.

Nghĩa là:

1. **Đặt ngân sách thời gian cho mỗi instance.** Ví dụ 60 giây rồi dừng, dùng lời giải
   tốt nhất tới lúc đó. Đừng để một bài khó nuốt hết cả giờ đồng hồ.

   ```python
   import time
   deadline = time.time() + 60
   while time.time() < deadline:
       ...  # cải thiện tiếp
   ```

2. **Luôn giữ sẵn lời giải hợp lệ tốt nhất hiện có** và ghi nó ra file. Đừng chờ thuật
   toán hội tụ.

3. **Diễn thử toàn bộ quy trình trước.** Chạy đúng lệnh bạn sẽ chạy, trên bộ public, và
   bấm giờ. Nếu phút thứ 44 mới phát hiện script ghi sai định dạng thì không cứu kịp.

---

## Những lỗi hay gặp nhất

| Lỗi | Hậu quả |
|---|---|
| Quên `ready_time` | Xe đứng chờ, mọi khách phía sau bị trễ dây chuyền |
| Chỉ tối ưu quãng đường | Bỏ qua bốn trong năm thứ bị đo |
| Cố giao bằng được mọi đơn | Thua các đội biết bỏ đúng đơn cần bỏ |
| Cho rằng bỏ đơn luôn tệ | Cũng sai. Nó là một đánh đổi |
| Cho rằng phạt trễ là tuyến tính | Hãy tự hỏi lại. Đề chỉ hứa hàm **tăng**, không hứa tuyến tính |
| Đưa `order_id` của kho vào tuyến | Kho không phải một đơn hàng |
| Nộp thiếu instance | Bài thiếu bị 0 điểm |
| Không đặt ngân sách thời gian | Vòng private chỉ có 45 phút cho 20 bài |
| Chỉ chạy `validate.py` ở phút chót | Chạy ngay từ đầu, và chạy thường xuyên |

---

## Cần trợ giúp

Hỏi trên kênh Discord của cuộc thi. Ban tổ chức trả lời được câu hỏi về **luật chơi** và
**định dạng file**.

Câu hỏi về trọng số chi phí thì không — đó là bài thi.
