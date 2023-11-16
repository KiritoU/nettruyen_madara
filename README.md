# Sử dụng tool:

## Chạy file update:

> tmux a -t 0
> python update.py

## Chạy file crawl all:

> tmux a -t 3
> python crawl_all.py

## Trong session tmux:

**Khi muốn dừng tool**: ấn tổ hợp phím: Ctrl C
**Khi muốn chạy lại tool**: python update.py (hoặc python crawl_all.py)

# Cài đặt cần lưu ý ở file settings.py (trong trường hợp cần sửa lại hoặc chạy tool ở vps khác):

- **user, password, host, port, database**: Kết nối tới database
- **TABLE_PREFIX:** Bắt đầu tên table trong database (Hiện tại là XBFUe\_)
- **CHAPTER_PREFIX:** Dòng chữ nhỏ ở trên mỗi chapter

- **CUSTOM_CDN:** Domain site lưu ảnh cho truyện
- **UPLOAD_FOLDER:** Folder gốc để lưu ảnh (nên để ở /var/www/html/ để dễ config nginx)

- **IMAGE_SAVE_PATH:** Folder để lưu ảnh của từng chapter
- **THUMB_SAVE_PATH:** Folder lưu ảnh covers (Sau đó sẽ copy lên hosting - tự động 1 phút / lần)

- **TELEGRAM_BOT_TOKEN:** Token của bot telegram (tạo trong chat với BotFather). Điền vào giữa dấu ""
- **TELEGRAM_CHAT_ID:** Telegram ID của user hoặc group nhận thông báo khi domain nettruyen có thể die. Điền vào giữa dấu ""

- **WAIT_BETWEEN_LATEST:** Thời gian đợi giữa 2 lần cào page 1 nettruyen để update: 5 \* 60 là 5 phút
- **WAIT_BETWEEN_ALL**: Thời gian đợi giữa 2 lần cào từ page 2 tới page cuối của nettruyen để cào các truyện còn lại: 1 \* 20 là 20 giây

- **NETTRUYEN_HOMEPAGE**: Domain của nettruyen (Đổi trong trường hợp nettruyen đổi)

# Trong trường hợp restart VPS cần chạy các lệnh sau sau khi ssh vào VPS

> cd nettruyen_madara
> tmux new -s 0
> source /venv/bin/activate
> Bấm và giữ Ctrl sau đó ấn B, sau đó nhả 2 phím và ấn D (dùng để ẩn session tmux - vẫn chạy bình thường)

> tmux new -s 3
> source /venv/bin/activate
> Bấm và giữ Ctrl sau đó ấn B, sau đó nhả 2 phím và ấn D

Sau đó sử dụng theo hướng dẫn trên
