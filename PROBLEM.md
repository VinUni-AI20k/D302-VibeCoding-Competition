# SwiftRoute — Last-Mile Delivery Challenge

## Bối cảnh

Bạn vận hành đội xe giao hàng chặng cuối của một sàn thương mại điện tử. Mỗi sáng, toàn
bộ đơn của ngày đổ về một kho trung tâm. Bạn có một số xe tải giống hệt nhau và một ca
làm việc. Việc của bạn: quyết định xe nào đi đâu, theo thứ tự nào.

Bạn sẽ không tìm được lời giải tối ưu. Không ai tìm được. Mục tiêu là **tốt hơn người
khác**.

## Dữ liệu

Một *instance* gồm:

| Trường | Ý nghĩa |
|---|---|
| `num_vehicles` | số xe tối đa được phép dùng |
| `vehicle_capacity` | tải trọng mỗi xe |
| `depot_x`, `depot_y` | toạ độ kho, tính bằng km |
| `shift_start`, `shift_end` | ca làm việc, tính bằng phút kể từ 00:00 |
| `speed` | tốc độ xe, km mỗi phút |

Mỗi đơn hàng gồm:

| Trường | Ý nghĩa |
|---|---|
| `order_id` | định danh, duy nhất trong một instance |
| `x`, `y` | toạ độ giao hàng, km |
| `demand` | khối lượng, cùng đơn vị với `vehicle_capacity` |
| `ready_time` | sớm nhất có thể giao |
| `due_time` | hẹn giao trước thời điểm này |
| `service_time` | số phút dừng tại điểm giao |

Khoảng cách giữa hai điểm là khoảng cách Euclid. Thời gian di chuyển là khoảng cách chia
cho `speed`. Không có tắc đường, không có đường một chiều, bản đồ phẳng.

## Một chuyến xe diễn ra thế nào

Mọi xe rời kho lúc `shift_start` và phải quay về kho.

```
t   = shift_start
pos = kho

với mỗi đơn trong tuyến, theo đúng thứ tự bạn đưa ra:
    t   += khoảng_cách(pos, đơn) / speed
    nếu t < ready_time:  t = ready_time        # đến sớm thì phải chờ
    thời điểm đến = t
    t   += service_time
    pos  = vị trí đơn

t += khoảng_cách(pos, kho) / speed             # thời điểm về tới kho
```

Trễ hẹn của một đơn được tính tại **thời điểm đến**, không phải lúc giao xong:
`max(0, thời_điểm_đến − due_time)`.

## Luật cứng

Vi phạm bất kỳ điều nào dưới đây thì lời giải cho instance đó bị **0 điểm**. Các instance
khác không bị ảnh hưởng.

1. Mỗi `order_id` xuất hiện **tối đa một lần** trên toàn bộ các tuyến.
2. Không được xuất hiện `order_id` không có trong instance.
3. Số tuyến không rỗng không được vượt quá `num_vehicles`.
4. Tổng `demand` của mỗi tuyến không được vượt quá `vehicle_capacity`.

## Luật mềm

Những điều này **không** làm lời giải mất hiệu lực. Chúng làm bạn tốn tiền.

- **Giao trễ.** `due_time` là lời hứa, không phải hàng rào. Đến sau `due_time` vẫn được
  giao, nhưng bị phạt.
- **Về muộn.** Về kho sau `shift_end` vẫn được, nhưng bị phạt.
- **Bỏ đơn.** Đơn nào không nằm trong tuyến nào thì coi như không giao. Điều này được
  phép và đôi khi là lựa chọn đúng, nhưng bị phạt.

## Bạn đang tối ưu cái gì

Đây là phần quan trọng nhất của đề bài, nên đọc kỹ.

Tổng chi phí vận hành là một hàm **tăng** theo đúng năm đại lượng sau:

1. Tổng quãng đường của tất cả các xe.
2. Số xe được sử dụng, tức số tuyến không rỗng.
3. Mức độ trễ hẹn của các đơn đã giao.
4. Thời gian làm ngoài ca, tính trên các xe về kho sau `shift_end`.
5. Các đơn bị bỏ, có tính đến khối lượng của chúng.

**Trọng số của từng thành phần và dạng hàm không được công bố.** Không có thành phần nào
ngoài năm cái trên. Không có thành phần nào trong năm cái trên bị bỏ qua.

Đây là cố ý. Trong công việc thật, hiếm khi ai đưa cho bạn hàm mục tiêu — bạn phải suy ra
nó từ những gì tổ chức thưởng và phạt. Ở đây cũng vậy: **suy ra hàm chi phí là một phần
của bài thi**, ngang hàng với việc viết heuristic tốt.

Bạn có hai nguồn thông tin:

- `validate.py` cho bạn biết năm đại lượng trên đo được bao nhiêu ở lời giải của bạn.
  Nó **không** cho bạn biết mỗi đại lượng đáng giá bao nhiêu.
- Bảng xếp hạng public cho bạn một con số điểm. Nộp nhiều lần với các lời giải khác nhau
  và quan sát điểm thay đổi ra sao là hoàn toàn hợp lệ, và được khuyến khích.

Một cảnh báo thẳng thắn: các instance public **không** kích hoạt cả năm thành phần. Đừng
kết luận rằng thành phần nào đó không quan trọng chỉ vì nó bằng 0 trên bộ public.

## Chấm điểm

Mỗi instance được chấm bằng cách so chi phí của bạn với chi phí lời giải tham chiếu của
ban tổ chức:

```
điểm_instance = 100 × chi_phí_tham_chiếu / chi_phí_của_bạn        (chặn trên ở 150)
```

- 100 điểm nghĩa là bạn ngang lời giải của ban tổ chức.
- Trên 100 nghĩa là bạn thắng ban tổ chức. Chuyện này xảy ra được.
- Lời giải không hợp lệ, hoặc thiếu instance trong file nộp, được 0 điểm cho instance đó.

Điểm chung cuộc là trung bình cộng trên các instance của bộ private.

## Bắt đầu từ đâu

```bash
python starter/solver_starter.py --orders data/sample_orders.csv --out TEN_DOI.json --team TEN_DOI
python validate.py --orders data/sample_orders.csv --submission TEN_DOI.json
```

Lời giải mẫu rất tệ. Đó là chủ ý — nó chỉ chứng minh vòng lặp chạy được.

`data/sample_orders.csv` là ba bài nhỏ để bạn chạy thử. Bộ đề thi thật — bộ public và bộ
private — được ban tổ chức phát riêng trên Discord theo lịch trong [RULES.md](RULES.md).

Xem [GUIDE.md](GUIDE.md) để có hướng dẫn từng bước, [DATA_FORMAT.md](DATA_FORMAT.md)
cho định dạng file, và [RULES.md](RULES.md) cho thể lệ và mốc thời gian.
