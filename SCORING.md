# Chấm điểm

## Công thức

Với mỗi instance:

```
chi_phí_của_bạn = f(quãng đường, số xe, mức trễ hẹn, thời gian ngoài ca, các đơn bị bỏ)

điểm_instance   = min(150, 100 × chi_phí_tham_chiếu / chi_phí_của_bạn)
```

`f` là hàm không được công bố. Những gì bạn được biết chắc chắn về nó:

- Nó nhận đúng **năm** đại lượng trên. Không hơn, không kém.
- Nó **tăng** theo từng đại lượng: mọi thứ khác giữ nguyên, đại lượng nào tăng thì chi
  phí tăng, không bao giờ giảm.
- Nó **giống hệt nhau** trên tất cả các instance, public lẫn private. Không có instance
  nào được chấm bằng công thức riêng.
- Nó xác định: cùng một lời giải luôn cho cùng một chi phí.

`chi_phí_tham_chiếu` là chi phí lời giải mà ban tổ chức đạt được bằng một metaheuristic
chạy đủ lâu. Nó cố định trước cuộc thi và không thay đổi theo bài nộp của các đội.

## Điểm chung cuộc

Trung bình cộng điểm của tất cả instance trong bộ **private**.

Bảng xếp hạng public chạy trên bộ public trong suốt buổi thi. Nó **không** tính vào kết
quả chung cuộc. Nó tồn tại để bạn có tín hiệu phản hồi.

## Khi nào bị 0 điểm

Tính riêng cho từng instance, không lan sang instance khác:

- Vi phạm một trong bốn luật cứng ở [PROBLEM.md](PROBLEM.md).
- Thiếu `instance_id` đó trong file nộp.
- File JSON hỏng tới mức không đọc được — trường hợp này thì **cả** file mất điểm, nên
  hãy chạy `validate.py` trước khi nộp.

## Về việc dò tìm hàm chi phí

Bạn được phép, và được khuyến khích, nộp nhiều lần lên bảng xếp hạng public với các lời
giải khác nhau để suy ra `f`. Đó là một phần của bài toán.

Vài điều nên biết trước khi tốn thời gian:

- Bộ public **không** kích hoạt cả năm thành phần. Trên bộ public, các lời giải tử tế
  đều không giao trễ, không làm ngoài ca và không bỏ đơn nào. Nghĩa là bạn **không thể**
  đo được ba thành phần đó chỉ bằng bảng xếp hạng public. Bộ private thì kích hoạt cả
  năm, và mạnh.
- Điểm trả về là một con số duy nhất trên mỗi instance. Nó không tách được thành từng
  khoản.
- Đừng giả định hàm là tuyến tính theo cả năm biến.

Cách dùng thời gian hiệu quả hơn: viết một heuristic mạnh, có tham số trọng số nội bộ
điều chỉnh được, rồi dùng bảng xếp hạng public để hiệu chỉnh những tham số mà bộ public
*có* nói cho bạn biết, và suy luận có cơ sở về phần còn lại.

## Cân đối thời gian

Bộ private chỉ được phát ra ở cuối buổi và cổng nộp đóng sau một khoảng thời gian ngắn
(xem [RULES.md](RULES.md)). Hệ quả thực tế:

**Code của bạn phải chạy xong bộ private trong khoảng thời gian đó.** Một heuristic chạy
15 phút cho mỗi instance là vô dụng nếu bạn có 20 instance và 40 phút. Hãy tự đặt ngân
sách thời gian cho mỗi instance, và đảm bảo lúc nào cũng có sẵn lời giải hợp lệ tốt nhất
tới thời điểm hiện tại để ghi ra file.
