# OpenClaw Admin Bot

**(English / Tiếng Việt)**

> [!IMPORTANT]
> **English Support Soon! / Sắp có hỗ trợ tiếng Anh!**

A professional Telegram bot designed to manage and monitor OpenClaw systems directly from your chat interface.
*Một bot Telegram chuyên nghiệp giúp quản lý và giám sát hệ thống OpenClaw trực tiếp từ giao diện chat.*

**Version:** 2026.02.07.07

## Core Features / Tính Năng Cốt Lõi

- 🤖 **Comprehensive UI**: Centralized menu for all admin tasks via `/cmd`.
  *Giao diện toàn diện: Menu tập trung cho mọi tác vụ quản trị qua `/cmd`.*
- 📊 **Intelligent Reporting**: Aggregated system status with strict "System ID" filtering and CLI Proxy bypass.
  *Báo cáo thông minh: Tổng hợp trạng thái hệ thống, lọc bỏ ID hệ thống rác và bỏ qua lỗi Proxy.*
- 💾 **Advanced Backup/Restore**: Hierarchical timestamped folders, excludes junk files (`.git`, `venv`). Support list browsing & version selection.
  *Sao lưu/Khôi phục nâng cao: Phân cấp thư mục, loại bỏ file rác (`.git`). Hỗ trợ duyệt và chọn phiên bản backup để khôi phục.*
- ☁️ **Interactive Telegram Restore**: Menu-driven restore for System (JSON), Full (Tar), and Light (Workspace-specific).
  *Restore tương tác qua Telegram: Menu chọn chế độ khôi phục thông minh cho System, Full và Light.*
- 📁 **FileStation Service**: Dedicated area for file exchange via Telegram with auto-versioning and `README.txt` generation.
  *Dịch vụ FileStation: Khu vực riêng để trao đổi file qua Telegram, tự động đánh số phiên bản và tạo hướng dẫn.*
- 🛡️ **Safety Guard**: Automatic configuration check at startup. `REPO_HOME` and `OPENCLAW_HOME` supports intelligent defaults.
  *Bảo vệ an toàn: Tự động kiểm tra cấu hình khi khởi động. Hỗ trợ đường dẫn mặc định thông minh.*
- 🌐 **Gateway Control**: Start, Stop, and Restart your gateway with automatic restarts after restores.
  *Điều khiển Gateway: Bật, Tắt, Khởi động lại gateway và tự động restart sau khi khôi phục dữ liệu.*
- 💻 **Manual Shell Mode**: Instant entry into the shell command input state from the menu.
  *Chế độ lệnh thủ công: Cho phép nhập lệnh shell Linux trực tiếp từ menu bot.*
- 🚀 **One-Click Update**: System-wide updates via the "Update Openclaw" button.
  *Cập nhật một chạm: Cập nhật toàn bộ hệ thống qua nút bấm trên bot.*
- 📦 **1-Command Install**: Simplified automated deployment for Linux VPS.
  *Cài đặt 1 lệnh: Triển khai tự động đơn giản cho VPS Linux.*

## Commands / Danh Sách Lệnh

- `/cmd` - Open the interactive Admin Menu. *(Mở Menu quản trị tương tác)*
- `/manual` - Start Manual Shell Mode. *(Vào chế độ nhập lệnh shell)*
- `/report` - Generate a detailed system health report. *(Tạo báo cáo sức khỏe hệ thống)*
- `/status` - Show quick system status and proxy usage. *(Xem nhanh trạng thái và proxy)*

## Installation & Setup (VPS) / Cài Đặt (VPS)

### 🚀 Option 1: Automatic Install (Recommended) / Cách 1: Tự động (Khuyên dùng)

Run this single command on your Linux VPS:
*Chạy duy nhất lệnh sau trên VPS Linux của bạn:*

```bash
git clone https://github.com/gnutirt/openclawbot.git && cd openclawbot && bash install.sh
```

*The script will install Python, dependencies, prompt for Token/ChatID, and set up systemd service.*
*Script sẽ tự động cài Python, thư viện, hỏi Token/ChatID và thiết lập chạy ngầm (systemd).*

### 🛠️ Option 2: Manual Install / Cách 2: Thủ công

1. **Clone repository**:

   ```bash
   git clone https://github.com/gnutirt/openclawbot.git && cd openclawbot
   ```

2. **Install dependencies / Cài thư viện**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure / Cấu hình**: Edit `config/config.cfg`.

4. **Run / Chạy bot**:

   ```bash
   python openclaw_admin_bot.py
   ```

## File Structure / Cấu Trúc File

- `openclaw_admin_bot.py`: Main entry point (Root). *(File chạy chính)*
- `config/`: Configuration files. *(Chứa file cấu hình)*
- `script/`: Helper modules and background logic. *(Module hỗ trợ và logic ngầm)*
- `FileStation/`: Temporary storage for uploaded files. *(Nơi lưu trữ file tạm)*
- `backup/`: Local backup storage (`system`, `full`, `light`). *(Nơi lưu file backup)*
- `requirements.txt`: Python dependencies. *(Danh sách thư viện)*

---
*Developed with focus on efficiency and system reliability.*
