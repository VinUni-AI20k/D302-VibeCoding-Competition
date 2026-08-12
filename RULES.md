# Thể lệ

## Mốc thời gian

| Thời điểm | Việc xảy ra |
|---|---|
| Trước buổi thi | Repo cùng toàn bộ tài liệu, công cụ và bộ sample đã có sẵn |
| Đầu buổi | Phát `public_orders.csv` (5 bài) trên Discord |
| Suốt buổi | Nộp bài lên kênh Discord bao nhiêu lần tuỳ ý; bảng xếp hạng public cập nhật khoảng **30 phút một lần** |
| T − 45 phút | Phát `private_orders.csv` (20 instance) |
| T | **Đóng cổng nộp.** File nộp sau thời điểm này không được chấm |
| T + 20 phút | Công bố bảng xếp hạng chung cuộc |

Ban tổ chức sẽ chốt giờ cụ thể trên Discord vào đầu buổi.

## Nộp bài

- **Tên đội phải là duy nhất** và đăng ký trước với ban tổ chức. Dùng đúng tên đó cho
  cả hai chỗ: tên file, và khoá `"team"` bên trong JSON. Hai chỗ lệch nhau thì khoá
  `"team"` được ưu tiên — nên nhớ sửa nó, đừng để nguyên `TEN_DOI` của file mẫu.
- Một đội, một file JSON: `TEN_DOI.json`.
- Đăng lên đúng kênh Discord đã chỉ định. Đính kèm file — đừng nén, đừng dán JSON dưới
  dạng text.
- Nộp lại thoải mái. **Lần nộp cuối cùng trước giờ đóng cổng là lần được tính**, kể cả
  khi nó tệ hơn lần trước. Nếu Discord tự thêm hậu tố kiểu `TEN_DOI (1).json` thì không
  sao, ban tổ chức vẫn gom đúng về đội bạn.
- File JSON hỏng tới mức không đọc được thì **cả file** mất điểm, không chỉ một bài.
  Chạy `validate.py` trước khi nộp.

## Được và không được

**Được:**

- Dùng bất kỳ thư viện, solver, hay AI coding assistant nào.
- Chạy code bao lâu tuỳ thích trong khoảng thời gian được cho.
- Nộp lại bao nhiêu lần tuỳ ý trong vòng public.
- Đọc mã nguồn trong gói được phát.

**Không được:**

- Hardcode lời giải cho từng instance thay vì tính ra. Sẽ bị phát hiện — bộ private chỉ
  phát ra 45 phút trước giờ đóng cổng.
- Chia sẻ code hoặc lời giải giữa các đội.
- Nộp bài dưới nhiều tên đội khác nhau, dù là để thử nghiệm.
- Tấn công hạ tầng chấm điểm, hoặc cố lấy dữ liệu private trước giờ phát.

## Vòng private

Đây là chỗ hầu hết các đội mất điểm, nên đọc kỹ:

Bộ private có **20 instance, mỗi bài từ 100 đến 200 đơn** — to hơn và chặt hơn bộ public.
Bạn có khoảng 45 phút kể từ lúc nhận file cho tới lúc đóng cổng, và đó là toàn bộ thời
gian để chạy code lẫn nộp bài. Hãy tính ngân sách dựa trên con số đó: 20 bài trong 40
phút nghĩa là trung bình khoảng 2 phút một bài, kể cả thời gian tải file và nộp.

Hệ quả:

1. Đặt ngân sách thời gian **cho mỗi instance**, đừng để một bài khó nuốt hết giờ.
2. Ghi ra file lời giải hợp lệ tốt nhất hiện có, đừng chờ tới khi thuật toán hội tụ.
3. Chạy thử toàn bộ quy trình trên bộ public **trước** khi vòng private bắt đầu. Nếu
   phút thứ 44 mới phát hiện script ghi sai định dạng thì không cứu kịp.
4. Chạy `validate.py` lên file private trước khi nộp. Mất 5 giây và cứu được cả buổi.

## Khiếu nại

Có thắc mắc về điểm thì nhắn trên Discord kèm tên đội. Ban tổ chức giữ điểm chi tiết
từng instance và lý do bị 0 điểm của mọi bài nộp.

Sự cố mạng hay Discord lỗi ngay sát giờ: báo trong kênh **trước** giờ đóng cổng. Báo sau
thì không giải quyết được.
