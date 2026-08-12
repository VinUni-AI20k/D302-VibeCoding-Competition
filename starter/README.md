# Bắt đầu

## Kiểm tra vòng lặp chạy được

```bash
python starter/solver_starter.py --orders data/sample_orders.csv --out TEN_DOI.json --team TEN_DOI
python validate.py --orders data/sample_orders.csv --submission TEN_DOI.json
```

Cần Python 3.10 trở lên. Không cần cài gì thêm — gói này chỉ dùng thư viện chuẩn.

## Bên trong gói có gì

```
GUIDE.md                  hướng dẫn từng bước. Đọc trước.
PROBLEM.md                đề bài chính thức
DATA_FORMAT.md            định dạng CSV và JSON
SCORING.md                cách chấm điểm
RULES.md                  thể lệ và mốc thời gian
validate.py               kiểm tra lời giải, in các đại lượng thô
starter/solver_starter.py lời giải mẫu ngây thơ
swiftroute/               thư viện đọc đề và đo lời giải
data/sample_orders.csv    3 bài nhỏ để chạy thử
```

## Những gì thư viện cho sẵn

```python
from swiftroute.io_csv import read_instances
from swiftroute.io_submission import write_submission
from swiftroute.metrics import evaluate

instances = read_instances("data/sample_orders.csv")
inst = instances[0]

inst.num_vehicles, inst.vehicle_capacity, inst.speed
inst.shift_start, inst.shift_end
inst.orders                    # tuple các Order
inst.order(7)                  # tra theo order_id
inst.dist(3, 9)                # khoảng cách giữa hai đơn
inst.dist_depot(3)             # khoảng cách từ kho
inst.travel_time(km)           # đổi km sang phút

stats = evaluate(inst, [[3, 9, 4], [7, 1]])
stats.feasible                 # có vi phạm luật cứng không
stats.violations               # nếu có thì vi phạm gì
stats.total_distance
stats.vehicles_used
stats.unserved_ids
stats.lateness_per_order       # phút trễ của từng đơn đã giao
stats.overtime_per_route
stats.routes[0].arrivals       # thời điểm đến từng điểm, để debug
```

`evaluate` chạy đúng bộ mô phỏng mà ban tổ chức dùng. Bạn có thể gọi nó bao nhiêu lần
tuỳ ý trong vòng lặp tìm kiếm của mình. Nó trả về các đại lượng thô; quy đổi chúng thành
một con số chi phí để so sánh hai lời giải là việc của bạn.

## Đường đi gợi ý

1. Cho chạy được vòng lặp: đọc CSV → sinh lời giải hợp lệ → ghi JSON → validate.
2. Viết một hàm chi phí **của riêng bạn**, tự chọn trọng số cho năm đại lượng. Mọi bước
   sau đều tối ưu theo hàm này, nên nó quyết định rất nhiều.
3. Xây dựng lời giải khởi đầu tử tế: chèn theo hối tiếc thường tốt hơn nhiều so với
   chèn tham lam thuần.
4. Cải thiện cục bộ: dời đơn giữa các tuyến, đổi chỗ, đảo đoạn trong tuyến.
5. Thoát cực trị địa phương: phá rồi sửa lại (large neighbourhood search), hoặc luyện
   kim mô phỏng.
6. Hiệu chỉnh trọng số của mình dựa trên bảng xếp hạng public.

Bước 2 quyết định phần lớn kết quả. Đừng bỏ qua nó để nhảy thẳng vào bước 5.

## Sai lầm hay gặp

- **Quên `ready_time`.** Đến sớm không phải là đến đúng giờ; xe phải đứng chờ, và thời
  gian chờ đẩy mọi điểm phía sau trong tuyến trễ theo.
- **Tối ưu quãng đường và chỉ quãng đường.** Chi phí vận hành gồm tới năm đại lượng.
- **Cho rằng phải giao hết đơn.** Không phải. Đôi khi bỏ là đúng.
- **Cho rằng bỏ đơn luôn tệ.** Cũng không phải. Nó là một đánh đổi.
- **Không đặt ngân sách thời gian.** Vòng private chỉ có 45 phút cho 20 instance.
- **Chỉ chạy validate ở phút cuối.** Chạy ngay từ đầu, và chạy thường xuyên.
