# OpenClaw Admin Bot

**(English / Tiếng Việt)**

> [!IMPORTANT]
> **English Support Soon! / Sắp có hỗ trợ tiếng Anh!**

A professional Telegram bot designed to manage and monitor OpenClaw systems directly from your chat interface.
*Một bot Telegram chuyên nghiệp giúp quản lý và giám sát hệ thống OpenClaw trực tiếp từ giao diện chat.*

**Version:** 2026.02.07.07

All notable changes to this project will be documented in this file.
*Mọi thay đổi đáng chú ý của dự án sẽ được ghi lại trong file này.*

## [2026.02.07.08] - 2026-02-07

### Fixed / Sửa Lỗi

- **Config BOM Issue**: Improved `read_config` utility to automatically handle UTF-8 with BOM (`utf-8-sig`) and other encodings. Fixed crash when editing config on Windows.
  *Sửa lỗi BOM trong Config: Cải thiện tiện ích `read_config` để tự động xử lý UTF-8 có BOM (`utf-8-sig`) và các bảng mã khác. Khắc phục lỗi crash khi sửa config trên Windows.*

## [2026.02.07.07] - 2026-02-07

### Added / Thêm Mới

- **Refined Light Restore UX ✨**: Completely redesigned "Light (Workspace)" flow. Select target workspace first, then drop your `.md` file for immediate overwrite.
  *Tinh chỉnh trải nghiệm Restore Light ✨: Thiết kế lại hoàn toàn luồng khôi phục Workspace lẻ. Chọn workspace đích trước, sau đó thả file .md để ghi đè ngay lập tức.*
- **Clean Workspace Selection**: The workspace list is now filtered based on your `SYSTEM:WORKSPACES` configuration, hiding system paths and clutter.
  *Danh sách Workspace tinh gọn: Danh sách workspace hiện được lọc dựa trên cấu hình `SYSTEM:WORKSPACES`, ẩn các đường dẫn hệ thống rác.*
- **Visual Polish**: Improved emojis and interactive prompts for a more premium "dropfile" experience.
  *Tinh chỉnh giao diện: Cải thiện emoji và các thông báo chờ file để mang lại trải nghiệm chuyên nghiệp hơn.*

## [2026.02.07.06] - 2026-02-07

### Added / Thêm Mới

- **Telegram Restore Menu**: Interactive selection for System (JSON), Full (Tar), and Light (Workspace) restore modes.
  *Menu Restore Telegram: Chọn loại khôi phục tương tác (System, Full, Light).*
- **Targeted Light Restore**: Select specific workspace before uploading `.tar.gz` to ensure files go to the right place.
  *Light Restore định danh: Chọn workspace đích trước khi upload file để đảm bảo tính chính xác.*
- **Backup Browsing**: Local restore now lists the 6 most recent backups with timestamps instead of auto-picking the latest.
  *Duyệt Backup Local: Hiển thị danh sách 6 bản backup gần nhất để người dùng tự chọn.*
- **Smart Navigation**: Added "Main Menu" and "Back" buttons to all restore success/failure screens.
  *Điều hướng thông minh: Thêm nút về Menu chính và nút Quay lại vào các màn hình kết quả.*

### Fixed / Sửa Lỗi

- **Ambiguous Restore**: Fixed potential bug where specific workspace restore could pick wrong file in multi-backup folders.
  *Sửa lỗi khôi phục nhầm: Khắc phục trường hợp restore workspace lẻ có thể chọn nhầm file trong thư mục chứa nhiều backup.*

## [2026.02.07.05] - 2026-02-07

### Added / Thêm Mới

- **Major Backup Redesign**: New hierarchical backup system (Local/Telegram -> Config/All/Single -> Full/Light).
  *Tái thiết kế Backup: Hệ thống sao lưu phân cấp hoàn toàn mới (Local/Telegram -> Config/All/Single -> Full/Light).*
- **Workspace Separation**: "All Workspaces" mode now auto-separates archives per workspace.
  *Tách biệt Workspace: Chế độ "All Workspaces" tự động tách riêng từng file nén cho mỗi workspace.*
- **Light Backup Mode**: Streamlined backup mode for only 6 core Agent .md files.
  *Chế độ Light Backup: Sao lưu tinh gọn chỉ dành cho 6 file core (.md) của Agent.*
- **Categorized Storage**: Organized into local subfolders: `system/`, `full/`, `light/`.
  *Lưu trữ phân loại: Phân loại thư mục lưu trữ cục bộ: `system/`, `full/`, `light/`.*
- **Intelligent Restoration**: Smart installer auto-detects and restores based on new categories.
  *Khôi phục thông minh: Bộ cài đặt thông minh tự tìm kiếm và khôi phục theo phân loại mới.*
- **Recursive Cleanup**: Smart cross-folder cleanup, keeping latest versions for each type.
  *Dọn dẹp đệ quy: Dọn dẹp thông minh xuyên thư mục, giữ lại bản mới nhất cho từng loại.*

## [2026.02.07.04] - 2026-02-07

### Changed / Thay Đổi

- **Config Flexibility**: `REPO_HOME` and `OPENCLAW_HOME` can now be empty (auto defaults).
  *Linh hoạt cấu hình: `REPO_HOME` và `OPENCLAW_HOME` hiện đã có thể để trống (tự động nhận giá trị mặc định).*
- **Mandatory Check Fix**: Only `TOKEN` and `ADMIN_ID` are strictly required.
  *Sửa lỗi kiểm tra bắt buộc: Chỉ bắt buộc `TOKEN` và `ADMIN_ID`.*

## [2026.02.07.03] - 2026-02-07

### Added / Thêm Mới

- **Configuration Safeguard**: Auto-checks required fields (`TOKEN`, `ADMIN_ID`) at startup.
  *Bảo vệ cấu hình: Bot tự động kiểm tra các trường bắt buộc (`TOKEN`, `ADMIN_ID`) khi khởi động.*
- **Auto-Install Prompt**: Guides user to run `install.sh` if config is incomplete.
  *Nhắc cài đặt tự động: Hướng dẫn người dùng chạy `install.sh` nếu cấu hình chưa hoàn thiện.*

### Changed / Thay Đổi

- **Version Bump**: Upgraded to v2026.02.07.03.
  *Nâng cấp phiên bản: Nâng cấp lên bản v2026.02.07.03.*

## [2026.02.07.02] - 2026-02-07

### Added / Thêm Mới

- **Hierarchical Backups**: Organized backups into timestamped folders `YYYYMMDD_HH_SS`.
  *Sao lưu phân cấp: Sao lưu tổ chức theo thư mục timestamp `YYYYMMDD_HH_SS` gọn gàng.*
- **Granular Restore**: Restore individual files like `MEMORY.md`, `IDENTITY.md`.
  *Khôi phục chi tiết: Cho phép khôi phục lẻ từng file `MEMORY.md`, `IDENTITY.md`, `SOUL.md`...*
- **FileStation Feature**: Telegram file exchange hub with auto-versioning.
  *Tính năng FileStation: Trạm trung chuyển file qua Telegram với khả năng tự đánh số khi trùng tên.*
- **Transfer Progress**: Progress bar (%) for uploads/downloads.
  *Tiến trình tải**: Hiển thị thanh tiến trình và phần trăm (%) khi upload/download file.*

## [2026.02.07.01] - 2026-02-07

### Added / Thêm Mới

- **One-Command Installer**: `install.sh` for automated deployment.
  *Trình cài đặt 1 lệnh: `install.sh` cho việc triển khai tự động.*
- **Backup Cleanup**: Button to purge old backups.
  *Dọn dẹp Backup: Nút xóa các bản backup cũ.*
- **Direct JSON Backup**: "Quick Backup" sends raw `openclaw.json`.
  *Backup cấu hình trực tiếp: Gửi thẳng file JSON thay vì nén.*
- **CLI Proxy Bypass**: Auto-skip stats if proxy config missing.
  *Bỏ qua Proxy CLI: Tự động bỏ qua thống kê nếu thiếu cấu hình.*

### Changed / Thay Đổi

- **Immediate Manual Mode**: "MANUAL SHELL MODE" enters input state instantly.
  *Chế độ thủ công tức thì: Vào thẳng chế độ nhập lệnh.*
- **Improved Naming**: Renamed `TELEGRAM_CHAT_ID_CHANNEL_LOG` to `ADMIN_CHAT_ID`.
  *Cải thiện đặt tên: Đổi tên biến ID chat admin cho dễ hiểu.*
- **Silent CLI Errors**: Hidden shell errors in reports.
  *Ẩn lỗi CLI: Ẩn các lỗi kỹ thuật shell trong báo cáo.*
- **Auto-Restart Gateway**: Auto-restart after restore.
  *Tự động khởi động lại Gateway: Sau khi restore thành công.*

### Fixed / Sửa Lỗi

- **Indentation Error**: Fixed API usage report indentation.
  *Lỗi thụt lề: Sửa lỗi hiển thị báo cáo API.*
- **Unified Requirements**: Updated `python-telegram-bot[job-queue]`.
  *Đồng bộ thư viện: Cập nhật thư viện bot telegram.*

## [2026.02.07.00] - 2026-02-07

### Core Features / Tính Năng Chính

- **Update Feature**: "🚀 Update Openclaw" button.
- **Tiered Backup & Restore**: Quick vs Full modes via Local/Telegram.
- **Privacy Filtering**: Removed System ID from reports.
