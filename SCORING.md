# Chấm điểm

## Công thức

Với mỗi instance:

```
điểm_instance = min(150, 100 × chi_phí_tham_chiếu / chi_phí_của_bạn)
```

`chi_phí_của_bạn` là tổng chi phí vận hành của lời giải bạn nộp, tính từ năm đại lượng
nêu trong [PROBLEM.md](PROBLEM.md): quãng đường, số xe huy động, mức trễ hẹn, thời gian
ngoài ca, và các đơn bị bỏ.

`chi_phí_tham_chiếu` là chi phí của lời giải mà ban tổ chức đạt được trên chính instance
đó. Nó được chốt trước cuộc thi và không thay đổi theo bài nộp của các đội.

Nghĩa là:

- **100 điểm** — bạn ngang lời giải của ban tổ chức.
- **Trên 100** — bạn tốt hơn ban tổ chức. Chuyện này xảy ra được.
- Mỗi instance có trần **150 điểm**, để một bài may mắn không lật được cả bảng.

Cách tính chi phí là như nhau trên mọi instance, public lẫn private. Cùng một lời giải
thì luôn ra cùng một chi phí.

## Điểm chung cuộc

Trung bình cộng điểm của tất cả instance trong bộ **private**.

Bảng xếp hạng public chạy trên bộ public trong suốt buổi thi. Nó **không** tính vào kết
quả chung cuộc — nó ở đó để bạn có phản hồi.

## Khi nào bị 0 điểm

Tính riêng cho từng instance, không lan sang instance khác:

- Vi phạm một trong bốn luật cứng ở [PROBLEM.md](PROBLEM.md).
- Thiếu `instance_id` đó trong file nộp.

Riêng trường hợp file JSON hỏng tới mức không đọc được thì **cả** file mất điểm — nên
hãy chạy `validate.py` trước khi nộp.

## Cân đối thời gian

Bộ private chỉ được phát ra ở cuối buổi và cổng nộp đóng sau một khoảng thời gian ngắn
(xem [RULES.md](RULES.md)). Hệ quả thực tế:

**Code của bạn phải chạy xong bộ private trong khoảng thời gian đó.** Một heuristic chạy
15 phút cho mỗi instance là vô dụng nếu bạn có 20 instance và 40 phút. Hãy tự đặt ngân
sách thời gian cho mỗi instance, và luôn giữ sẵn lời giải hợp lệ tốt nhất tới thời điểm
hiện tại để ghi ra file.
