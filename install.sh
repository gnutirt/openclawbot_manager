#!/bin/bash

# OpenClaw Admin Bot - One-Command Installer
# Hỗ trợ cài đặt tự động cho người dùng mới trên Linux (Ubuntu/Debian)

set -e

echo "🚀 Bắt đầu cài đặt OpenClaw Admin Bot..."

# 1. Cập nhật hệ thống & Cài đặt dependencies
echo "📦 Đang cài đặt các gói phụ thuộc (Python3, Pip, Git)..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv git

# 2. Tạo môi trường ảo (Virtual Environment)
echo "🐍 Đang thiết lập môi trường Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 3. Cài đặt Python requirements
echo "📥 Đang cài đặt thư viện Python..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Fallback nếu file ở root hoặc script/
    if [ -f "script/requirements.txt" ]; then
        pip install -r script/requirements.txt
    else
        echo "⚠️ Không tìm thấy requirements.txt, đang cài đặt các gói cơ bản..."
        pip install "python-telegram-bot[job-queue]" requests
    fi
fi

# 4. Cấu hình tương tác
echo ""
echo "⚙️  PHẦN CẤU HÌNH (Rất quan trọng):"
echo "-----------------------------------"

# Kiểm tra file config
CONFIG_FILE="config/config.cfg"
mkdir -p config

# Hỏi thông tin nếu chưa có
echo "💡 Mẹo: Lấy ID cá nhân từ @userinfobot hoặc ID Kênh từ @GetMyIdBot"
read -p "🔹 Nhập Telegram Bot Token: " TG_TOKEN
read -p "🔹 Nhập Telegram Chat ID (Cá nhân hoặc Kênh nhận báo cáo): " TG_CHAT_ID

cat <<EOF > $CONFIG_FILE
[API_KEYS]
# Telegram Bot Token — lấy từ @BotFather
TELEGRAM_TOKEN_OPENCLAW_ADMIN = $TG_TOKEN

# Chat ID của admin hoặc Kênh nhận báo cáo (lấy từ @userinfobot hoặc @GetMyIdBot)
ADMIN_CHAT_ID = $TG_CHAT_ID

# Thông tin CLIProxy (Để trống nếu không dùng)
CLIPROXY_MANAGEMENT_URL = 
CLIPROXY_MANAGEMENT_KEY = 

[SYSTEM]
# Thư mục gốc chứa dữ liệu OpenClaw (Để trống để mặc định là ~/.openclaw)
OPENCLAW_HOME = 

# Thư mục chứa mã nguồn bot (Để trống bot sẽ tự động lấy thư mục hiện tại)
REPO_HOME = 

# Thư mục lưu trữ Backup (Để trống sẽ tạo 'backup/' trong REPO_HOME)
BACKUP_PATH = 

# Danh sách Workspace (Cách nhau bởi dấu phẩy, dùng cho Full Backup)
WORKSPACES = 
EOF

echo "✅ Đã lưu cấu hình vào $CONFIG_FILE"

# 5. Tạo Systemd Service để chạy ngầm
echo "🔄 Đang thiết lập chạy ngầm (Systemd)..."
SERVICE_FILE="/etc/systemd/system/openclaw-admin.service"
WORKING_DIR=$(pwd)
USER_NAME=$(whoami)

sudo bash -c "cat <<EOF > $SERVICE_FILE
[Unit]
Description=OpenClaw Admin Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$WORKING_DIR
ExecStart=$WORKING_DIR/venv/bin/python $WORKING_DIR/openclaw_admin_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

# 6. Kích hoạt service
echo "⚡ Đang khởi chạy Bot..."
sudo systemctl daemon-reload
sudo systemctl enable openclaw-admin
sudo systemctl restart openclaw-admin

echo "-----------------------------------"
echo "🎉 CHÚC MỪNG! OpenClaw Admin Bot đã cài đặt xong."
echo "✅ Bot đang chạy ngầm trên hệ thống."
echo "💡 Bạn có thể kiểm tra trạng thái bằng lệnh: sudo systemctl status openclaw-admin"
echo "🚀 Bây giờ hãy mở Telegram và gõ /start để kiểm tra!"
