#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Admin Bot - Bot Telegram để quản lý và chạy các lệnh hệ thống
"""

import subprocess
import json
import sys
import logging
import requests
import datetime
from datetime import datetime
from pathlib import Path
import shutil
import os
import re
import warnings
from telegram.warnings import PTBUserWarning

# Tắt các cảnh báo phiền phức từ thư viện PTB (JobQueue, per_message, v.v.)
warnings.filterwarnings("ignore", category=PTBUserWarning)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# --- PHẦN QUAN TRỌNG: FIX PATH ---
VERSION = "2026.02.07.08"

def get_init_root():
    return Path(__file__).resolve().parent

ROOT = get_init_root()
SCRIPT_DIR = ROOT / "script"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))

from other_utils import read_config, get_vietnam_time

# Đường dẫn file khởi tạo
CONFIG_PATH = str(ROOT / "config" / "config.cfg")
# Load config sơ bộ để check REPO_HOME
config = read_config(CONFIG_PATH)

# Nếu có cấu hình REPO_HOME, cập nhật lại ROOT
custom_repo = config.get("SYSTEM", "REPO_HOME", fallback="").strip()
if custom_repo:
    ROOT = Path(os.path.expanduser(custom_repo))
    SCRIPT_DIR = ROOT / "script"
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.append(str(SCRIPT_DIR))

# --- KIỂM TRA CẤU HÌNH BẮT BUỘC ---
def check_mandatory_config(config):
    """Kiểm tra các trường bắt buộc, nếu thiếu thì yêu cầu chạy install.sh"""
    mandatory = {
        "TELEGRAM_TOKEN_OPENCLAW_ADMIN": "Token bot Telegram",
        "ADMIN_CHAT_ID": "ID Chat Admin"
    }
    missing = []
    
    # Check API_KEYS section
    token = config.get("API_KEYS", "TELEGRAM_TOKEN_OPENCLAW_ADMIN", fallback="").strip()
    admin_id = config.get("API_KEYS", "ADMIN_CHAT_ID", fallback="").strip()
    
    if not token: missing.append("TELEGRAM_TOKEN_OPENCLAW_ADMIN")
    if not admin_id: missing.append("ADMIN_CHAT_ID")
    
    if missing:
        print("\n" + "!"*50)
        print("❌ LỖI: CẤU HÌNH THIẾU THÔNG TIN BẮT BUỘC!")
        print(" Các trường còn trống: " + ", ".join(missing))
        print("\n👉 Vui lòng chạy lệnh sau để thiết lập lại hệ thống:")
        print(f"   bash {ROOT}/install.sh")
        print("!"*50 + "\n")
        sys.exit(1)

check_mandatory_config(config)

# Cập nhật lại các đường dẫn full
CONFIG_PATH = str(ROOT / "config" / "config.cfg")
COMMAND_LIST_PATH = str(ROOT / "script" / "command_list.json")
JSON_MODEL_PATH = str(ROOT / "config" / "ai_no_free.json")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def run_shell_command(command, timeout=30):
    """Helper để chạy lệnh shell và lấy stdout/stderr, lọc bỏ cảnh báo Node.js"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=timeout
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        # Lọc bỏ DeprecationWarning của punycode (thường gặp trong Node.js/openclaw)
        if stdout:
            stdout = "\n".join([line for line in stdout.splitlines() if "[DEP0040]" not in line])
        if stderr:
            stderr = "\n".join([line for line in stderr.splitlines() if "[DEP0040]" not in line])
            
        return stdout, stderr
    except Exception as e:
        return "", str(e)


def load_commands():
    """Đọc danh sách lệnh từ command_list.json"""
    try:
        if not Path(COMMAND_LIST_PATH).exists():
            logger.error(f"❌ Không tìm thấy file {COMMAND_LIST_PATH}")
            return []
        
        with open(COMMAND_LIST_PATH, "r", encoding="utf-8") as f:
            commands = json.load(f)
        
        logger.info(f"✅ Đã load {len(commands)} lệnh từ command_list.json")
        return commands
    except Exception as e:
        logger.error(f"❌ Lỗi khi đọc command_list.json: {e}")
        return []


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /start"""
    user = update.effective_user
    commands = load_commands()
    
    cmd_list = ""
    if commands:
        for cmd in commands:
            alias = cmd.get("command_alias", "")
            desc = cmd.get("Description", "")
            cmd_list += f"• {alias} - {desc}\n"
    else:
        cmd_list = "• Không có lệnh nào\n"
    
    welcome_msg = (
        f"👋 Xin chào <b>{user.first_name}</b>!\n\n"
        f"🤖 Tôi là <b>OpenClaw Admin Bot</b> (v{VERSION})\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📋 <b>Các lệnh có sẵn:</b>\n"
        f"{cmd_list}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 Gõ /cmd để xem menu lệnh\n"
        f"💡 Gõ /help để xem hướng dẫn\n"
        f"💡 Gõ /status để kiểm tra bot\n\n"
        f"⚡ Sẵn sàng phục vụ!"
    )
    await update.message.reply_text(welcome_msg, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /help"""
    help_msg = (
        "📖 <b>HƯỚNG DẪN SỬ DỤNG</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>1. Lệnh /cmd</b>\n"
        "   Hiển thị menu các lệnh AI có thể thực thi\n\n"
        "<b>2. Chọn lệnh từ menu</b>\n"
        "   Nhấn vào nút tương ứng để chạy lệnh\n\n"
        "<b>3. Nhận kết quả</b>\n"
        "   Bot sẽ thực thi và phản hồi kết quả\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Mọi lệnh được định nghĩa trong command_list.json</i>"
    )
    await update.message.reply_text(help_msg, parse_mode='HTML')

# --- MANUAL COMMAND HANDLER STATES ---
WAITING_FOR_CMD = 1

async def manual_command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bắt đầu trợ năng nhập lệnh thủ công"""
    # Nếu được gọi từ button (callback_query)
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "💻 <b>MANUAL MODE ACTIVATED</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Bạn đã vào chế độ nhập lệnh trực tiếp.\n"
            "Vui lòng nhập lệnh shell bạn muốn chạy:\n"
            "(Gõ /cancel để thoát)",
            parse_mode='HTML'
        )
    else:
        # Nếu được gọi từ lệnh /manual
        await update.message.reply_text(
            "🛠 <b>MANUAL MODE</b>\n"
            "Nhập lệnh shell bạn muốn chạy (hoặc gõ /cancel để hủy):",
            parse_mode='HTML'
        )
    return WAITING_FOR_CMD

async def manual_command_exec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Thực thi lệnh nhập từ user"""
    cmd = update.message.text
    user = update.effective_user
    
    logger.info(f"Manual cmd from {user.first_name}: {cmd}")
    await update.message.reply_text(f"⏳ Đang chạy: <code>{cmd}</code>...", parse_mode='HTML')
    
    stdout, stderr = run_shell_command(cmd, timeout=60)
    output = stdout or "Success"
    if stderr:
        output += f"\nSTDERR:\n{stderr}"
        
    if len(output) > 3000:
        output = output[:3000] + "\n...[truncated]"

    await update.message.reply_text(f"<pre>{output}</pre>", parse_mode='HTML')
    await update.message.reply_text("Nhập lệnh tiếp theo hoặc /cancel:")
    return WAITING_FOR_CMD

async def manual_command_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Thoát chế độ manual"""
    await update.message.reply_text("❌ Đã thoát Manual Mode.")
    return ConversationHandler.END

# --- QUẢN LÝ BACKUP ---
def get_openclaw_home():
    """Lấy đường dẫn OpenClaw Home từ config hoặc mặc định"""
    cfg_home = config.get("SYSTEM", "OPENCLAW_HOME", fallback="").strip()
    if cfg_home:
        return Path(os.path.expanduser(cfg_home))
    return Path.home() / ".openclaw"

def get_backup_dir():
    """Lấy đường dẫn thư mục backup từ config hoặc mặc định trong ROOT"""
    cfg_path = config.get("SYSTEM", "BACKUP_PATH", fallback="").strip()
    if cfg_path:
        path = Path(os.path.expanduser(cfg_path))
        os.makedirs(path, exist_ok=True)
        return path
    path = ROOT / "backup"
    
    # Init subdirectories and placeholders
    for sub in ["system", "full", "light"]:
        sub_path = path / sub
        os.makedirs(sub_path, exist_ok=True)
        readme = sub_path / "README.txt"
        if not readme.exists():
            with open(readme, "w", encoding="utf-8") as f:
                f.write(f"Thư mục này chứa các bản backup loại '{sub.upper()}'.\n")
                f.write("Hiện tại chưa có bản backup nào.\n")
                f.write("Vui lòng thực hiện Backup từ menu Bot OpenClaw Admin.\n")
                
    return path

BACKUP_SRC = get_openclaw_home() / "openclaw.json"
BACKUP_DIR = get_backup_dir()
BACKUP_DEST = BACKUP_DIR / "openclaw.json"

# --- QUẢN LÝ FILESTATION ---
# --- QUẢN LÝ FILESTATION ---
FILESTATION_DIR = ROOT / "FileStation"
os.makedirs(FILESTATION_DIR, exist_ok=True)

readme_fs = FILESTATION_DIR / "README.txt"
if not readme_fs.exists():
    with open(readme_fs, "w", encoding="utf-8") as f:
        f.write("Thư mục này là FileStation - nơi lưu trữ file tạm thời của bot.\n")
        f.write("Các file gửi lên bot (không phải format backup) sẽ được lưu vào đây.\n")
        f.write("Bạn có thể tải file về bằng cách chat tên file vào bot (ví dụ: 'report.pdf').\n")

def get_unique_filename(filename):
    """Nếu file trùng tên trong FileStation, đánh số (1), (2)..."""
    base, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    path = FILESTATION_DIR / new_filename
    while path.exists():
        new_filename = f"{base}({counter}){extension}"
        path = FILESTATION_DIR / new_filename
        counter += 1
    return new_filename

def perform_copy(src, dest):
    try:
        if not os.path.exists(src): return False, f"Source không tìm thấy: {src}"
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)
        return True, f"Đã khôi phục thành công."
    except Exception as e:
        return False, str(e)

def create_compressed_backup(target='system', mode='full', save_local=True, timestamp=None):
    """
    Tạo bản nén backup theo cấu trúc mới:
    - target: 'system', [workspace_name]
    - mode: 'full', 'light'
    - save_local: True/False
    - timestamp: YYYYMMDD_HHMMSS (dùng chung cho các đợt backup hàng loạt)
    """
    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    openclaw_dir = get_openclaw_home()
    
    if target == 'system':
        rel_path = Path("system") / timestamp
        mode_label = "system"
    elif mode == 'full':
        rel_path = Path("full") / timestamp
        mode_label = f"full_{target}"
    else: # light
        rel_path = Path("light") / target / timestamp
        mode_label = f"light_{target}"
        
    # Xác định thư mục lưu trữ
    if save_local:
        final_backup_dir = BACKUP_DIR / rel_path
    else:
        import tempfile
        final_backup_dir = Path(tempfile.gettempdir()) / f"openclaw_tmp_{timestamp}"
    
    os.makedirs(final_backup_dir, exist_ok=True)
    
    backup_file = final_backup_dir / f"openclaw_{mode_label}_{timestamp}.{'json' if target == 'system' else 'tar.gz'}"
    
    if not openclaw_dir.exists():
        return None, "Không tìm thấy thư mục OpenClaw Home"
    
    try:
        if target == 'system':
             config_src = openclaw_dir / "openclaw.json"
             if not config_src.exists(): return None, "Không tìm thấy openclaw.json"
             shutil.copy2(config_src, backup_file)
             return str(backup_file), None

        import tarfile
        with tarfile.open(backup_file, "w:gz") as tar:
            if mode == 'full':
                ws_path = openclaw_dir / target
                if not ws_path.exists():
                    return None, f"Không tìm thấy Workspace: {target}"
                
                def exclude_junk(tarinfo):
                    # Các thư mục hệ thống/không cần thiết
                    junk_dirs = [".git", "__pycache__", "node_modules", "venv", ".venv", "env", "cognee_env"]
                    for junk in junk_dirs:
                        if f"/{junk}" in tarinfo.name or tarinfo.name.endswith(junk):
                            return None
                    return tarinfo
                    
                tar.add(ws_path, arcname=target, filter=exclude_junk)
            else: # light
                ws_path = openclaw_dir / target
                if not ws_path.exists():
                    return None, f"Không tìm thấy Workspace: {target}"
                md_files = ["HEARTBEAT.md", "IDENTITY.md", "MEMORY.md", "USER.md", "TOOLS.md", "SOUL.md"]
                found_any = False
                for md in md_files:
                    src_md = ws_path / md
                    if src_md.exists():
                        tar.add(src_md, arcname=f"{target}/{md}")
                        found_any = True
                if not found_any:
                    return None, f"Workspace {target} không có các file .md cần thiết."
                    
        return str(backup_file), None
    except Exception as e:
        return None, str(e)


def get_cliproxy_stats():
    """Lấy thống kê nhanh từ Management API của CLIProxy"""
    
    # Load from config
    url = config.get("API_KEYS", "CLIPROXY_MANAGEMENT_URL", fallback="http://127.0.0.1:8317/v0/management")
    key = config.get("API_KEYS", "CLIPROXY_MANAGEMENT_KEY", fallback="")
    headers = {"Authorization": f"Bearer {key}"}
    stats_text = "\n📊 <b>CLIProxy Quick Stats:</b>\n"
    try:
        usage_res = requests.get(f"{url}/usage", headers=headers, timeout=2)
        if usage_res.status_code == 200:
            data = usage_res.json().get("usage", {})
            tokens = data.get("total_tokens", 0)
            token_str = format_tokens_short(tokens)
            stats_text += f"• Usage: <code>{data.get('total_requests', 0)}</code> reqs | <code>{token_str}</code> tokens\n"
        else:
            stats_text += "• Usage: <i>Unauthorized (401)</i>\n"
        
        auth_res = requests.get(f"{url}/auth-files", headers=headers, timeout=2)
        if auth_res.status_code == 200:
            files = auth_res.json().get("files", [])
            ready_count = sum(1 for f in files if f.get("status") == "ready")
            stats_text += f"• Auth: <code>{ready_count}/{len(files)}</code> files ready\n"
    except Exception as e:
        stats_text += f"• Error: <code>{str(e)[:50]}</code>\n"
    return stats_text

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý khi user gửi file: Backup để restore hoặc file thường vào FileStation"""
    if not update.message or not update.message.document:
        return
    
    doc = update.message.document
    file_name = doc.file_name.lower()

    # Kiểm tra pending mode từ menu
    pending_mode = context.user_data.get('pending_restore_mode')
    pending_workspace = context.user_data.get('pending_restore_workspace')
    
    # Logic nhận diện file backup
    is_json = file_name.endswith('.json')
    is_tar = file_name.endswith('.tar.gz')
    is_md = file_name.endswith('.md')
    is_system_backup = is_json and ('openclaw' in file_name)
    
    # Nếu đang đợi restore cụ thể
    if pending_mode:
        if pending_mode == 'system' and not is_json:
            await update.message.reply_text("❌ <b>Sai định dạng:</b> Vui lòng gửi file <code>.json</code> cho System Restore.", parse_mode='HTML')
            return
        if pending_mode == 'full' and not is_tar:
            await update.message.reply_text("❌ <b>Sai định dạng:</b> Vui lòng gửi file <code>.tar.gz</code> cho Full Backup Restore.", parse_mode='HTML')
            return
        if pending_mode == 'light' and not is_md:
            await update.message.reply_text("❌ <b>Sai định dạng:</b> Vui lòng gửi file <code>.md</code> cho Light Restore (Workspace).", parse_mode='HTML')
            return
            
        is_backup = True # Force backup flow
    else:
        # Auto-detect nếu không chọn menu
        is_backup = is_tar or is_system_backup

    if is_backup:
        msg = await update.message.reply_text("⏳ <b>Đang tải file backup... [0%]</b>", parse_mode='HTML')
        try:
            new_file = await context.bot.get_file(doc.file_id)
            temp_path = ROOT / f"temp_upload_{doc.file_name}"

            await msg.edit_text("⏳ <b>Đang nhận file:</b> <code>[████░░░░░░] 40%</code>", parse_mode='HTML')
            await new_file.download_to_drive(custom_path=temp_path)
            await msg.edit_text("⏳ <b>Đang nhận file:</b> <code>[██████████] 100%</code>", parse_mode='HTML')
            
            context.user_data['pending_restore_path'] = str(temp_path)
            
            # Xử lý Logic theo Mode
            if pending_mode == 'system' or (not pending_mode and is_system_backup):
                mode_label = "SYSTEM CONFIG"
                context.user_data['pending_restore_is_full'] = False # System logic
                desc = "Khôi phục cấu hình hệ thống (openclaw.json)."
                
            elif pending_mode == 'light':
                mode_label = f"LIGHT ({pending_workspace})"
                context.user_data['pending_restore_is_full'] = False # Light uses specific logic
                desc = f"Khôi phục dữ liệu Light vào workspace <b>{pending_workspace}</b>."
                
            elif pending_mode == 'full':
                # Try parse workspace from filename: openclaw_full_wsname_date.tar.gz
                # Pattern: openclaw_full_(.*)_\d{8}
                match = re.search(r"openclaw_full_(.*)_\d{8}", file_name)
                ws_name = match.group(1) if match else "Unknown"
                mode_label = f"FULL ({ws_name})"
                context.user_data['pending_restore_is_full'] = True
                desc = f"Khôi phục toàn bộ workspace <b>{ws_name}</b> (ghi đè)."
                
            else: # Auto-detect Tar fallback
                mode_label = "FULL BUNDLE"
                context.user_data['pending_restore_is_full'] = True
                desc = "Khôi phục toàn bộ nội dung từ file nén."

            keyboard = [
                [InlineKeyboardButton("✅ CÓ, RESTORE NGAY", callback_data="act_tg_restore_confirm")],
                [InlineKeyboardButton("❌ HỦY BỎ", callback_data="act_tg_restore_cancel")]
            ]
            await msg.edit_text(
                f"📥 <b>NHẬN FILE THÀNH CÔNG</b>\n"
                f"Loại: <b>{mode_label}</b>\n"
                f"File: <code>{doc.file_name}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"ℹ️ {desc}\n"
                f"⚠️ <b>CẢNH BÁO:</b> Dữ liệu cũ sẽ bị ghi đè!",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        except Exception as e:
            await msg.edit_text(f"❌ <b>Lỗi xử lý backup:</b> {e}")
    else:
        # Flow FileStation
        msg = await update.message.reply_text(f"⏳ <b>Đang lưu vào FileStation... [0%]</b>", parse_mode='HTML')
        try:
            new_file = await context.bot.get_file(doc.file_id)
            save_name = get_unique_filename(doc.file_name)
            dest_path = FILESTATION_DIR / save_name
            
            await msg.edit_text(f"⏳ <b>Đang lưu:</b> <code>{save_name}</code> <code>[████░░░░░░] 45%</code>", parse_mode='HTML')
            await new_file.download_to_drive(custom_path=dest_path)
            
            await msg.edit_text(
                f"✅ <b>ĐÃ LƯU VÀO FILESTATION</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Tên gốc: <code>{doc.file_name}</code>\n"
                f"Lưu tại: <code>{save_name}</code>\n"
                f"Dung lượng: <code>{doc.file_size / 1024:.1f} KB</code>",
                parse_mode='HTML'
            )
        except Exception as e:
            await msg.edit_text(f"❌ <b>Lỗi FileStation:</b> {e}")

async def handle_text_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý khi user nhập text: Kiểm tra xem có phải tên file trong FileStation không"""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    if text.startswith('/'): return
    
    file_path = FILESTATION_DIR / text
    if file_path.exists() and file_path.is_file():
        msg = await update.message.reply_text(f"⏳ <b>Phát hiện yêu cầu file:</b> <code>{text}</code>...", parse_mode='HTML')
        try:
            # Progress simulation
            await msg.edit_text(f"⏳ <b>Đang gửi:</b> <code>{text}</code> <code>[██████░░░░] 60%</code>", parse_mode='HTML')
            with open(file_path, 'rb') as f:
                await context.bot.send_document(
                    chat_id=update.message.chat.id,
                    document=f,
                    filename=text,
                    caption=f"📂 FileStation Auto-Send\n⏰ {get_vietnam_time()}"
                )
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ <b>Lỗi gửi file:</b> {e}")

def format_tokens_short(n):
    """Định dạng token sang k hoặc M"""
    if n >= 1000000: return f"{n/1000000:.2f}M"
    if n >= 1000: return f"{n/1000:.1f}k"
    return str(n)

def parse_simple_kv(text):
    """Parse output dạng | Key | Value | hoặc Key: Value"""
    data = {}
    if not text: return data
    for line in text.splitlines():
        if "id" in line.lower(): continue # Skip lines containing "id"
        if "│" in line:
            parts = [p.strip() for p in line.split("│") if p.strip()]
            if len(parts) >= 2 and parts[0] != "Item":
                data[parts[0]] = parts[1]
        elif ":" in line:
            parts = line.split(":", 1)
            data[parts[0].strip()] = parts[1].strip()
    return data

async def generate_full_report(update_func=None):
    """Tạo báo cáo chuyên nghiệp bằng cách parse dữ liệu CLI (có tiến trình)"""
    now = get_vietnam_time()
    url = CLIPROXY_URL
    key = CLIPROXY_KEY
    headers = {"Authorization": f"Bearer {key}"}
    
    if update_func: await update_func("⏳ <b>Đang chạy (1/3):</b> Kiểm tra trạng thái hệ thống...")
    
    report_msg = f"📊 <b>OPENCLAW SYSTEM REPORT</b>\n"
    report_msg += f"<i>v{VERSION} | {now}</i>\n"
    report_msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # 1. Parse Status & Gateway
    status_out, _ = run_shell_command("openclaw status")
    status_data = parse_simple_kv(status_out)
    
    gw_info = status_data.get("Gateway service", "Unknown")
    gw_status = "🟢 Active" if "running" in gw_info.lower() else "🔴 Stopped"
    
    report_msg += f"🌐 <b>Gateway:</b> {gw_status}\n"
    report_msg += f"🖥️ <b>OS:</b> <code>{status_data.get('OS', 'N/A')}</code>\n\n"
    
    if update_func: await update_func("⏳ <b>Đang chạy (2/3):</b> Lấy danh sách Sessions & Channels...")
    
    # 2. Parse Sessions & Channels
    sessions_out, _ = run_shell_command("openclaw sessions")
    sessions_lines = []
    
    # Simple parser for sessions output
    found_header = False
    for line in sessions_out.splitlines():
        if "Kind" in line and "Key" in line and "Age" in line:
            found_header = True
            continue
        if found_header and line.strip():
            # Xóa System ID ngay lập tức khỏi dòng
            clean_line = re.sub(r'system\s+id:[\w\-]+', '', line, flags=re.IGNORECASE).strip()
            
            # Tách cột thô bằng pipe (|) và khoảng trắng
            parts = [p.strip() for p in re.split(r'[│|]', clean_line) if p.strip()]
            if not parts:
                parts = [p.strip() for p in re.split(r'\s{2,}', clean_line) if p.strip()]
            
            # Logic nhận diện cột dựa trên keyword
            v_age = next((p for p in parts if "ago" in p.lower()), "N/A")
            v_model = next((p for p in parts if any(m in p.lower() for m in ["gpt", "claude", "gemini", "llama", "mixtral"])), "N/A")
            v_tokens = next((p for p in parts if "%" in p), "N/A")
            
            # Nếu không tìm thấy bằng keyword, fallback dựa trên vị trí cột chuẩn (2, 3, 4)
            # 0:Kind, 1:Key, 2:Age, 3:Model, 4:Tokens
            if v_model == "N/A" and len(parts) >= 5: v_model = parts[3]
            if v_tokens == "N/A" and len(parts) >= 5: v_tokens = parts[4]
            if v_age == "N/A" and len(parts) >= 5: v_age = parts[2]

            if v_model != "N/A":
                display = f"   • {v_age} | {v_model} | <code>{v_tokens}</code>"
                # Chặn trùng lặp chính xác nội dung dòng display
                if display not in sessions_lines:
                    sessions_lines.append(display)
    
    if sessions_lines:
        report_msg += "🧵 <b>Active Sessions:</b>\n"
        report_msg += "\n".join(sessions_lines[:5]) # Show up to 5 sessions
        if len(sessions_lines) > 5:
            report_msg += f"\n   <i>...và {len(sessions_lines)-5} session khác.</i>"
        report_msg += "\n\n"
    
    channels_out, _ = run_shell_command("openclaw channels list")
    ch_lines = [l for l in channels_out.splitlines() if "OK" in l or "ON" in l]
    if ch_lines:
        report_msg += "📡 <b>Channels:</b>\n"
        for l in ch_lines:
            parts = [p.strip() for p in l.split("│") if p.strip()]
            if len(parts) >= 3:
                report_msg += f"   • {parts[0]}: 🟢 {parts[2]}\n"
    
    # Active Model
    models_out, _ = run_shell_command("openclaw models")
    default_model = "Unknown"
    for line in models_out.splitlines():
        if "Default" in line and ":" in line:
            default_model = line.split(":", 1)[1].strip()
            break
    report_msg += f"\n🤖 <b>Active Model:</b>\n<code>{default_model}</code>\n"
    
    if update_func: await update_func("⏳ <b>Đang chạy (3/3):</b> Đang đo lường tài nguyên...")
    
    report_msg += "\n━━━━━━━━━━━━━━━━━━━━\n"
    
    # 3. API Usage
    if url and key and url.strip() and key.strip():
        try:
            usage_res = requests.get(f"{url}/usage", headers=headers, timeout=5)
            if usage_res.status_code == 200:
                usage_data = usage_res.json().get("usage", {})
                report_msg += f"📈 <b>Usage Stats:</b>\n"
                report_msg += f"• Requests: <code>{usage_data.get('total_requests', 0)}</code>\n"
                report_msg += f"• Tokens: <code>{format_tokens_short(usage_data.get('total_tokens', 0))}</code>\n"
                
                auth_res = requests.get(f"{url}/auth-files", headers=headers, timeout=5)
                if auth_res.status_code == 200:
                    files = auth_res.json().get("files", [])
                    ready = sum(1 for f in files if f.get("status") in ["active", "ready"])
                    report_msg += f"🛡️ <b>Auth:</b> <code>{ready}/{len(files)}</code> files ready\n"
        except:
            report_msg += "⚠️ <i>API Stats temporarily unavailable</i>\n"
        
        report_msg += "━━━━━━━━━━━━━━━━━━━━\n"
    report_msg += "💡 Dùng /cmd để mở menu."
    return report_msg

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /report"""
    # Gửi tin nhắn tạo tiến trình ban đầu
    loading_msg = await update.message.reply_text("⏳ <b>Đang khởi tạo báo cáo...</b>", parse_mode='HTML')
    
    async def update_progress(txt):
        await loading_msg.edit_text(txt, parse_mode='HTML')
        
    report_msg = await generate_full_report(update_func=update_progress)
    await loading_msg.edit_text(report_msg, parse_mode='HTML')

async def scheduled_report(context: ContextTypes.DEFAULT_TYPE):
    """Job gửi báo cáo định kỳ"""
    job = context.job
    chat_id = job.chat_id
    if not chat_id: return
    report_msg = await generate_full_report()
    try:
        await context.bot.send_message(chat_id=chat_id, text=report_msg, parse_mode='HTML')
    except Exception as e:
        logger.error(f"❌ Error sending scheduled report: {e}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /status"""
    now = get_vietnam_time()
    proxy_stats = get_cliproxy_stats()
    status_msg = (
        "📊 <b>OPENCLAW SYSTEM STATUS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 Time: <code>{now}</code>\n"
        "✅ Bot Admin: <b>Active</b>\n"
        f"{proxy_stats}"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Dùng /cmd để mở menu điều khiển."
    )
    await update.message.reply_text(status_msg, parse_mode='HTML')

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE, is_refresh=False):
    """Lệnh /cmd - Menu chính tối ưu (Fast Load)"""
    query = update.callback_query
    if is_refresh and query:
        await query.edit_message_text("⏳ <b>Đang làm mới menu...</b>", parse_mode='HTML')

    now = get_vietnam_time()
    
    ws_list_str = config.get("SYSTEM", "WORKSPACES", fallback="Chưa cấu hình")
    masked_url = CLIPROXY_URL[:15] + "..." if CLIPROXY_URL else "Chưa thiết lập"
    
    keyboard = [
        [InlineKeyboardButton("🚀 Update Openclaw", callback_data="menu_update")],
        [InlineKeyboardButton("📊 System Report", callback_data="report")],
            [InlineKeyboardButton("💾 Backup & Restore", callback_data="menu_backup")],
            [InlineKeyboardButton("📁 FileStation", callback_data="menu_fs_list")],
        [InlineKeyboardButton("🛠 Model Manual", callback_data="menu_manual")],
        [InlineKeyboardButton("🎲 Model Random", callback_data="menu_random")],
        [InlineKeyboardButton("🌐 Gateway Control", callback_data="menu_gateway")],
        [InlineKeyboardButton("ℹ️ Info List", callback_data="menu_info")],
        [InlineKeyboardButton("💻 Manual Shell Cmd", callback_data="start_manual_mode")],
    ]
    menu_msg = (
        "🤖 <b>OPENCLAW ADMIN MENU</b>\n"
        f"Version: {VERSION}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 <i>Last Active: {now}</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📂 <b>Root:</b> <code>{ROOT}</code>\n"
        f"📁 <b>Workspaces:</b> <code>{ws_list_str}</code>\n"
        f"🌐 <b>CLIProxy:</b> <code>{masked_url}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Chọn lệnh bạn muốn thực thi:\n"
    )
    
    if update.message:
        await update.message.reply_text(menu_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    elif query:
        await query.edit_message_text(menu_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


def load_models_by_type(model_type):
    """Load models từ ai_no_free.json"""
    try:
        if not Path(JSON_MODEL_PATH).exists(): return []
        with open(JSON_MODEL_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        all_models = data.get("models", [])
        return [m for m in all_models if m.get("model_type") == model_type]
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        return []


def create_model_menu(model_type, page=0, models_per_page=5):
    """Tạo menu chọn model với phân trang"""
    models = load_models_by_type(model_type)
    if not models: return None, "Không tìm thấy model nào"
    total_models = len(models)
    total_pages = (total_models + models_per_page - 1) // models_per_page
    page = max(0, min(page, total_pages - 1))
    start_idx = page * models_per_page
    end_idx = min(start_idx + models_per_page, total_models)
    page_models = models[start_idx:end_idx]
    keyboard = []
    for model in page_models:
        full_path = model.get("full_path", "")
        model_name = full_path.split("/")[-1] if full_path else "Unknown"
        service = model.get("service", "")
        keyboard.append([InlineKeyboardButton(f"{'🔹' if service == 'cliproxy' else '🔸'} {model_name}", callback_data=f"select_{full_path.replace('/', '_')}")])
    nav_buttons = []
    if page > 0: nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"menu_{model_type}_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1: nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"menu_{model_type}_{page+1}"))
    if nav_buttons: keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("◀️ Quay về", callback_data="menu_manual")])
    emoji = {"claude": "🤖", "gemini": "💎", "gpt": "🚀"}.get(model_type, "🤖")
    message = f"{emoji} <b>MODEL {model_type.upper()}</b>\n━━━━━━━━━━━━━━━━━━━━\nTrang {page+1}/{total_pages} ({total_models} models)\n"
    return InlineKeyboardMarkup(keyboard), message


async def execute_shell_command_callback(query, command, title):
    """Helper để chạy lệnh shell từ callback (Override message)"""
    now = get_vietnam_time()
    await query.edit_message_text(f"⏳ <b>[{title}] Running...</b>\n<code>{command}</code>", parse_mode='HTML')
    stdout, stderr = run_shell_command(command, timeout=120)
    output = stdout or "Success"
    if stderr: output += f"\nSTDERR: {stderr}"
    if len(output) > 2000: output = output[:2000] + "\n...[Truncated]"
    await query.edit_message_text(f"✅ <b>[{title}] DONE</b>\n⏰ {now}\n<pre>{output}</pre>", parse_mode='HTML')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý khi user nhấn nút trong inline keyboard"""
    query = update.callback_query
    await query.answer()
    callback_data = query.data
    
    if callback_data == "noop": return
    if callback_data == "menu_update":
        keyboard = [
            [InlineKeyboardButton("✅ YES, UPDATE NOW", callback_data="act_update")],
            [InlineKeyboardButton("❌ NO", callback_data="back_main")]
        ]
        await query.edit_message_text("🚀 <b>CONFIRM UPDATE?</b>\nRunning <code>openclaw update</code>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return
    if callback_data == "act_update":
        await execute_shell_command_callback(query, "openclaw update", "OpenClaw Update")
        return
    if callback_data == "back_main":
        await ai_command(update, context)
        return
    if callback_data == "report":
        async def update_progress(txt):
            await query.edit_message_text(txt, parse_mode='HTML')
            
        report_msg = await generate_full_report(update_func=update_progress)
        keyboard = [[InlineKeyboardButton("◀️ Quay về", callback_data="back_main")]]
        await query.edit_message_text(report_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return


    # --- MENU BACKUP MỚI (v2026.02.07.05) ---
    if callback_data == "menu_backup":
        keyboard = [
            [InlineKeyboardButton("💻 BACKUP TO LOCAL STORAGE", callback_data="menu_bk_src_local")],
            [InlineKeyboardButton("📤 BACKUP TO TELEGRAM", callback_data="menu_bk_src_tg")],
            [InlineKeyboardButton("📥 RESTORE SYSTEM", callback_data="menu_restore_select")],
            [InlineKeyboardButton("🧹 Dọn dẹp Backup", callback_data="act_cleanup")],
            [InlineKeyboardButton("◀️ Quay về", callback_data="back_main")]
        ]
        await query.edit_message_text("💾 <b>BACKUP & RESTORE</b>\n━━━━━━━━━━━━━━━━━━━━\nChọn phương thức lưu trữ bản sao lưu:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return
    
    if callback_data.startswith("menu_bk_src_"):
        src = callback_data.replace("menu_bk_src_", "")
        src_label = "LOCAL" if src == "local" else "TELEGRAM"
        keyboard = [
            [InlineKeyboardButton("⚙️ Config Hệ thống", callback_data=f"confirm_bk_system_{src}")],
            [InlineKeyboardButton("📦 Toàn bộ Workspace", callback_data=f"confirm_bk_all_{src}")],
            [InlineKeyboardButton("📁 Theo Workspace cụ thể", callback_data=f"menu_bk_target_ws_{src}")],
            [InlineKeyboardButton("◀️ Quay về", callback_data="menu_backup")]
        ]
        await query.edit_message_text(f"📤 <b>BACKUP [{src_label}]</b>\n━━━━━━━━━━━━━━━━━━━━\nChọn đối tượng muốn sao lưu:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return

    if callback_data.startswith("menu_bk_target_ws_"):
        src = callback_data.replace("menu_bk_target_ws_", "")
        ws_list = config.get("SYSTEM", "WORKSPACES", fallback="").split(",")
        ws_list = [ws.strip() for ws in ws_list if ws.strip()]
        
        if not ws_list:
            await query.edit_message_text("⚠️ <b>Chưa cấu hình Workspace!</b>", 
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Quay về", callback_data=f"menu_bk_src_{src}")]]), 
                                          parse_mode='HTML')
            return
            
        keyboard = []
        for ws in ws_list:
            keyboard.append([InlineKeyboardButton(f"📁 {ws}", callback_data=f"menu_bk_mode_{ws}_{src}")])
        keyboard.append([InlineKeyboardButton("◀️ Quay về", callback_data=f"menu_bk_src_{src}")])
        
        await query.edit_message_text(f"📁 <b>CHỌN WORKSPACE [{src.upper()}]</b>\n━━━━━━━━━━━━━━━━━━━━\nChọn workspace cần sao lưu:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return

    if callback_data.startswith("menu_bk_mode_"):
        parts = callback_data.split("_")
        ws_name = parts[3]
        src = parts[4]
        
        keyboard = [
            [InlineKeyboardButton("✨ LIGHT (Chỉ .md)", callback_data=f"confirm_bk_light_{ws_name}_{src}")],
            [InlineKeyboardButton("📦 FULL (Toàn bộ folder)", callback_data=f"confirm_bk_full_{ws_name}_{src}")],
            [InlineKeyboardButton("◀️ Quay về", callback_data=f"menu_bk_target_ws_{src}")]
        ]
        await query.edit_message_text(f"⚙️ <b>CHẾ ĐỘ SAO LƯU [{ws_name}]</b>\n━━━━━━━━━━━━━━━━━━━━\nNguồn: {src.upper()}\nChọn mức độ chi tiết:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return

    if callback_data.startswith("confirm_bk_"):
        parts = callback_data.split("_")
        target_info = ""
        if parts[2] == "system":
            target_info = "⚙️ Config Hệ thống"
            action_data = f"act_bk_system_{parts[3]}"
        elif parts[2] == "all":
            target_info = "📦 Toàn bộ Workspace"
            action_data = f"act_bk_all_{parts[3]}"
        else: # mode_ws_name_src
            mode = parts[2]
            ws_name = parts[3]
            src = parts[4]
            target_info = f"📁 {ws_name} ({mode.upper()})"
            action_data = f"act_bk_{mode}_ws_{ws_name}_{src}"
            
        src_label = "Lưu Local" if callback_data.endswith("_local") else "Gửi Telegram"
        keyboard = [[InlineKeyboardButton("✅ XÁC NHẬN", callback_data=action_data)], [InlineKeyboardButton("❌ HỦY", callback_data="menu_backup")]]
        
        await query.edit_message_text(
            f"⚠️ <b>XÁC NHẬN SAO LƯU</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"Đối tượng: <b>{target_info}</b>\n"
            f"Phương thức: <b>{src_label}</b>\n\n"
            f"Bạn có chắc muốn thực hiện không?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return

    if callback_data.startswith("act_bk_"):
        parts = callback_data.split("_")
        src = parts[-1]
        save_local = (src == "local")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        await query.edit_message_text(f"⏳ <b>Đang khởi tạo sao lưu...</b> ({src.upper()})", parse_mode='HTML')
        
        targets = []
        if parts[2] == "system":
            targets.append(('system', 'full'))
        elif parts[2] == "all":
            ws_list = config.get("SYSTEM", "WORKSPACES", fallback="").split(",")
            ws_list = [ws.strip() for ws in ws_list if ws.strip()]
            for ws in ws_list: targets.append((ws, 'full'))
        else:
            mode = parts[2]
            ws_name = parts[4]
            targets.append((ws_name, mode))
            
        success_files, errors = [], []
        for i, (tgt, mode) in enumerate(targets):
            await query.edit_message_text(f"⏳ <b>Đang sao lưu ({i+1}/{len(targets)}):</b> <code>{tgt}</code>...", parse_mode='HTML')
            file_path, err = create_compressed_backup(target=tgt, mode=mode, save_local=save_local, timestamp=timestamp)
            if err:
                errors.append(f"{tgt}: {err}")
            else:
                success_files.append((tgt, file_path))
                if not save_local:
                    try:
                        with open(file_path, 'rb') as f:
                            await context.bot.send_document(
                                chat_id=query.message.chat.id,
                                document=f,
                                filename=os.path.basename(file_path),
                                caption=f"☁️ <b>Backup: {tgt}</b>\nMode: {mode.upper()}\n⏰ {get_vietnam_time()}",
                                parse_mode='HTML'
                            )
                        os.remove(file_path)
                    except Exception as e: errors.append(f"Gửi {tgt} lỗi: {e}")

        result_msg = f"✅ <b>HOÀN TẤT SAO LƯU</b>\n━━━━━━━━━━━━━━━━━━━━\nPhương thức: <b>{src.upper()}</b>\nThành công: <code>{len(success_files)}</code>\n"
        if errors: result_msg += f"Thất bại: <code>{len(errors)}</code>\n\n❌ <b>LỖI:</b>\n" + "\n".join(errors[:5])
        else: result_msg += "\n🎉 <i>Tất cả đã sẵn sàng!</i>"
        if save_local: result_msg += f"\n\n📂 <b>Vị trí:</b> <code>backup/</code>"

        keyboard = [[InlineKeyboardButton("◀️ Quay về", callback_data="menu_backup")]]
        await query.edit_message_text(result_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return

    # --- MENU RESTORE (v2026.02.07.05) ---
    if callback_data == "menu_restore_select":
        keyboard = [
            [InlineKeyboardButton("⚙️ Config Hệ thống", callback_data="act_rs_system")],
            [InlineKeyboardButton("📦 Toàn bộ Workspace (Full)", callback_data="act_rs_full_all")],
            [InlineKeyboardButton("📁 Theo Workspace cụ thể", callback_data="menu_restore_ws")],
            [InlineKeyboardButton("☁️ Restore từ Telegram", callback_data="info_rs_tg")],
            [InlineKeyboardButton("◀️ Quay về", callback_data="menu_backup")]
        ]
        await query.edit_message_text("📥 <b>RESTORE OPTIONS</b>\n━━━━━━━━━━━━━━━━━━━━\nChọn đối tượng muốn khôi phục:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return

    if callback_data == "menu_restore_ws":
        ws_list = config.get("SYSTEM", "WORKSPACES", fallback="").split(",")
        ws_list = [ws.strip() for ws in ws_list if ws.strip()]
        if not ws_list:
            await query.edit_message_text("⚠️ <b>Chưa cấu hình Workspace!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Quay về", callback_data="menu_restore_select")]]), parse_mode='HTML')
            return
        keyboard = [[InlineKeyboardButton(f"📁 {ws}", callback_data=f"menu_rs_choice_{ws}")] for ws in ws_list]
        keyboard.append([InlineKeyboardButton("◀️ Quay về", callback_data="menu_restore_select")])
        await query.edit_message_text("📁 <b>CHỌN WORKSPACE KHÔI PHỤC</b>\n━━━━━━━━━━━━━━━━━━━━\nChọn workspace cần khôi phục:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return

    if callback_data.startswith("menu_rs_choice_"):
        ws_name = callback_data.replace("menu_rs_choice_", "")
        keyboard = [
            [InlineKeyboardButton("📦 Restore bản FULL", callback_data=f"act_rs_full_ws_{ws_name}")],
            [InlineKeyboardButton("✨ Restore bản LIGHT", callback_data=f"act_rs_light_ws_{ws_name}")],
            [InlineKeyboardButton("◀️ Quay về", callback_data="menu_restore_ws")]
        ]
        await query.edit_message_text(f"📥 <b>KHÔI PHỤC [{ws_name}]</b>\n━━━━━━━━━━━━━━━━━━━━\nChọn loại bản sao lưu:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return

    if callback_data.startswith("act_rs_"):
        action = callback_data.replace("act_rs_", "")
        if action == "system":
            sub_dir, mode_display = Path("system"), "Config Hệ thống"
        elif action == "full_all":
            sub_dir, mode_display = Path("full"), "Toàn bộ Workspace"
        elif action.startswith("full_ws_"):
            ws_name = action.replace("full_ws_", "")
            sub_dir, mode_display = Path("full"), f"FULL Workspace [{ws_name}]"
        elif action.startswith("light_ws_"):
            ws_name = action.replace("light_ws_", "")
            sub_dir, mode_display = Path("light") / ws_name, f"LIGHT Workspace [{ws_name}]"
        else:
            await query.edit_message_text("❌ Lỗi: Lệnh restore không hợp lệ."); return

        parent_dir = BACKUP_DIR / sub_dir
        await query.edit_message_text(f"⏳ <b>[{mode_display}] Đang tìm kiếm...</b>", parse_mode='HTML')
        
        # Nếu thư mục không tồn tại hoặc chỉ có README.txt
        if not parent_dir.exists():
             return await query.edit_message_text(f"⚠️ <b>Chưa có bản backup nào!</b>\nThư mục <code>{sub_dir}</code> chưa được tạo.", parse_mode='HTML')

        # Lọc ra các thư mục con (timestamp)
        sub_folders = [d for d in os.listdir(parent_dir) if os.path.isdir(parent_dir / d)]
        
        if not sub_folders:
            return await query.edit_message_text(f"⚠️ <b>Chưa có bản backup nào!</b>\nVui lòng thực hiện Backup trước khi Restore.\n(Không tìm thấy bản ghi nào trong <code>{sub_dir}/</code>)", parse_mode='HTML')

        # === LOGIC MỚI: DUYỆT & CHỌN VERSION ===
        sub_folders.sort(reverse=True) # Mới nhất lên đầu
        valid_backups = []
        
        for ts in sub_folders:
            ts_folder = parent_dir / ts
            has_file = False
            
            if action == 'system':
                has_file = any(f.endswith(".json") for f in os.listdir(ts_folder))
            elif "full_all" in action:
                has_file = any(f.endswith(".tar.gz") for f in os.listdir(ts_folder))
            elif "ws_" in action: # ws specific
                target_ws = ws_name 
                files = [f for f in os.listdir(ts_folder) if f.endswith(".tar.gz") and f"_{target_ws}_" in f]
                has_file = bool(files)
            
            if has_file: valid_backups.append(ts)
            if len(valid_backups) >= 6: break # Lấy tối đa 6 bản gần nhất

        if not valid_backups:
             return await query.edit_message_text(f"⚠️ <b>Không tìm thấy dữ liệu!</b>\nCó {len(sub_folders)} thư mục backup nhưng không có file phù hợp cho yêu cầu này.", parse_mode='HTML')

        # Tạo Menu chọn Timestamp
        context.user_data['restore_target_action'] = action
        context.user_data['restore_target_subdir'] = str(sub_dir) # Để dùng lại

        keyboard = []
        for ts in valid_backups:
            # Format lại Time cho dễ đọc: YYYYMMDD_HHMMSS -> YYYY-MM-DD HH:MM:SS
            try:
                dt_obj = datetime.datetime.strptime(ts, "%Y%m%d_%H%M%S")
                display_ts = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
            except: display_ts = ts
            
            keyboard.append([InlineKeyboardButton(f"📅 {display_ts}", callback_data=f"conf_rs_ts_{ts}")])
        
        keyboard.append([InlineKeyboardButton("◀️ Quay về", callback_data="menu_restore_select")])
        
        await query.edit_message_text(
            f"📥 <b>CHỌN PHIÊN BẢN RESTORE</b>\n"
            f"Mode: <b>{mode_display}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Tìm thấy {len(valid_backups)} bản sao lưu gần nhất:", 
            reply_markup=InlineKeyboardMarkup(keyboard), 
            parse_mode='HTML'
        )
        return

    # === LOGIC THỰC THI RESTORE (SAU KHI CHỌN VERSION) ===
    if callback_data.startswith("conf_rs_ts_"):
        ts = callback_data.replace("conf_rs_ts_", "")
        action = context.user_data.get('restore_target_action')
        sub_dir_str = context.user_data.get('restore_target_subdir')
        
        if not action or not sub_dir_str:
            await query.edit_message_text("❌ <b>Lỗi Context:</b> Vui lòng thực hiện lại từ đầu.", parse_mode='HTML')
            return

        parent_dir = BACKUP_DIR / sub_dir_str
        target_folder = parent_dir / ts
        
        if not target_folder.exists():
             await query.edit_message_text(f"❌ <b>Lỗi:</b> Thư mục bản ghi {ts} không còn tồn tại.", parse_mode='HTML')
             return

        msg_loading = f"⏳ <b>Đang khôi phục bản {ts}...</b>"
        await query.edit_message_text(msg_loading, parse_mode='HTML')
        
        try:
            ok, msg = False, "Lỗi không xác định"
            
            # --- CASE 1: SYSTEM CONFIG ---
            if action == 'system':
                archives = [f for f in os.listdir(target_folder) if f.endswith(".json")]
                if archives:
                    src_json = target_folder / archives[0]
                    ok, msg = perform_copy(src_json, BACKUP_SRC)
                    if ok:
                        _, _ = run_shell_command("openclaw gateway restart")
                        msg = f"Đã khôi phục System Config từ bản {ts}"
                else: msg = "Không tìm thấy file .json"

            # --- CASE 2: FULL / LIGHT ---
            else:
                archives = [f for f in os.listdir(target_folder) if f.endswith(".tar.gz")]
                # Filter lại workspace nếu cần (đảm bảo an toàn)
                if "ws_" in action:
                    target_ws = action.split("ws_")[-1]
                    archives = [f for f in archives if f"_{target_ws}_" in f]
                
                if not archives:
                     ok, msg = False, "Không tìm thấy file backup (.tar.gz) trong bản ghi này."
                else:
                    import tarfile
                    openclaw_home = get_openclaw_home()
                    count = 0
                    for arch in archives:
                        try:
                            with tarfile.open(target_folder / arch, "r:gz") as tar:
                                tar.extractall(path=openclaw_home)
                            count += 1
                        except Exception as ex:
                            msg = f"Lỗi: {ex}"
                    
                    if count > 0: ok, msg = True, f"Đã restore {count} file từ bản {ts}"
                    else: ok, msg = False, "Không giải nén được file nào."

            # KẾT QUẢ
            keyboard = [
                [InlineKeyboardButton("◀️ Quay lại List", callback_data=f"act_rs_{action}")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")]
            ]
            if ok: await query.edit_message_text(f"✅ <b>RESTORE THÀNH CÔNG!</b>\n{msg}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            else: await query.edit_message_text(f"❌ <b>Thất bại:</b> {msg}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

        except Exception as e:
            await query.edit_message_text(f"❌ <b>Lỗi Critical:</b> {e}", parse_mode='HTML')
        return


    # --- CÁC TÍNH NĂNG KHÁC ---
    if callback_data == "act_cleanup":
        await query.edit_message_text("⏳ <b>Đang dọn dẹp các bản sao lưu cũ...</b>", parse_mode='HTML')
        try:
            deleted_count = 0
            def cleanup_recursive(dir_path):
                nonlocal deleted_count
                if not os.path.exists(dir_path): return
                items = [d for d in os.listdir(dir_path) if os.path.isdir(dir_path / d)]
                if len(items) <= 1: return
                items.sort(); items.pop()
                for old in items:
                    try: shutil.rmtree(dir_path / old); deleted_count += 1
                    except: pass
            cleanup_recursive(BACKUP_DIR / "system")
            cleanup_recursive(BACKUP_DIR / "full")
            if (BACKUP_DIR / "light").exists():
                for ws in os.listdir(BACKUP_DIR / "light"): cleanup_recursive(BACKUP_DIR / "light" / ws)
            keyboard = [[InlineKeyboardButton("◀️ Quay về", callback_data="menu_backup")]]
            await query.edit_message_text(f"✅ <b>Dọn dẹp thành công!</b>\nĐã xóa <code>{deleted_count}</code> đợt sao lưu cũ.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except Exception as e: await query.edit_message_text(f"❌ <b>Lỗi dọn dẹp:</b> {e}")
        return

    if callback_data == "menu_fs_list":
        try:
            files = [f for f in os.listdir(FILESTATION_DIR) if os.path.isfile(FILESTATION_DIR / f)]
            if not files:
                msg = "📂 <b>FILE STATION</b>\n━━━━━━━━━━━━━━━━━━━━\nThư mục đang trống.\nHãy ném bất kỳ file nào vào đây để lưu trữ."
                keyboard = [[InlineKeyboardButton("◀️ Quay về", callback_data="back_main")]]
            else:
                msg = f"📂 <b>FILE STATION</b>\n━━━━━━━━━━━━━━━━━━━━\nTìm thấy <b>{len(files)}</b> file:\n\n"
                keyboard = [[InlineKeyboardButton(f"📥 Lấy {f}", callback_data=f"act_fs_get_{f}")] for f in files[:10]]
                if len(files) > 10: msg += "\n<i>...và các file khác.</i>"
                keyboard.append([InlineKeyboardButton("◀️ Quay về", callback_data="back_main")])
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except Exception as e: await query.edit_message_text(f"❌ <b>Lỗi FileStation:</b> {e}")
        return

    if callback_data.startswith("act_fs_get_"):
        filename = callback_data.replace("act_fs_get_", "")
        file_path = FILESTATION_DIR / filename
        try:
            await query.edit_message_text(f"⏳ <b>Đang gửi:</b> <code>{filename}</code>...", parse_mode='HTML')
            with open(file_path, 'rb') as f:
                await context.bot.send_document(chat_id=query.message.chat.id, document=f, filename=filename, caption=f"📂 FileStation | {get_vietnam_time()}")
            await query.delete_message()
        except Exception as e: await query.edit_message_text(f"❌ <b>Lỗi gửi file:</b> {e}")
        return

    if callback_data == "info_rs_tg":
        keyboard = [
            [InlineKeyboardButton("⚙️ Config (System)", callback_data="act_tg_wait_system")],
            [InlineKeyboardButton("📦 Full Bundle", callback_data="act_tg_wait_full")],
            [InlineKeyboardButton("✨ Light (Workspace)", callback_data="menu_tg_light_ws_select")],
            [InlineKeyboardButton("◀️ Quay về", callback_data="menu_restore_select")]
        ]
        await query.edit_message_text(
            "☁️ <b>RESTORE TỪ TELEGRAM</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Vui lòng chọn loại dữ liệu bạn muốn khôi phục:", 
            reply_markup=InlineKeyboardMarkup(keyboard), 
            parse_mode='HTML'
        )
        return

    if callback_data == "act_tg_wait_system":
        context.user_data['pending_restore_mode'] = 'system'
        context.user_data.pop('pending_restore_workspace', None)
        await query.edit_message_text(
            "⚙️ <b>RESTORE: SYSTEM CONFIG</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Vui lòng gửi file <code>.json</code> cấu hình vào đây.\n"
            "💡 Tên file không quan trọng, bot sẽ tự nhận.", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Quay lại", callback_data="info_rs_tg")]]),
            parse_mode='HTML'
        )
        return

    if callback_data == "act_tg_wait_full":
        context.user_data['pending_restore_mode'] = 'full'
        context.user_data.pop('pending_restore_workspace', None)
        await query.edit_message_text(
            "📦 <b>RESTORE: FULL BUNDLE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Vui lòng gửi file <code>.tar.gz</code> full backup vào đây.\n"
            "💡 Bot sẽ cố gắng đọc tên Workspace từ tên file.", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Quay lại", callback_data="info_rs_tg")]]),
            parse_mode='HTML'
        )
        return

    if callback_data == "menu_tg_light_ws_select":
        # Lấy danh sách workspace từ config hệ thống
        ws_list_str = config.get("SYSTEM", "WORKSPACES", fallback="")
        workspaces = [ws.strip() for ws in ws_list_str.split(",") if ws.strip()]
        
        if not workspaces:
            await query.answer("❌ Chưa cấu hình Workspace trong SYSTEM:WORKSPACES!", show_alert=True)
            return

        keyboard = []
        for ws in workspaces:
            keyboard.append([InlineKeyboardButton(f"📁 {ws}", callback_data=f"act_tg_wait_light_ws_{ws}")])
        keyboard.append([InlineKeyboardButton("◀️ Quay lại", callback_data="info_rs_tg")])
        
        await query.edit_message_text(
            "✨ <b>RESTORE LIGHT (WORKSPACE)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Vui lòng chọn Workspace đích để khôi phục file:", 
            reply_markup=InlineKeyboardMarkup(keyboard), 
            parse_mode='HTML'
        )
        return

    if callback_data.startswith("act_tg_wait_light_ws_"):
        ws_name = callback_data.replace("act_tg_wait_light_ws_", "")
        context.user_data['pending_restore_mode'] = 'light'
        context.user_data['pending_restore_workspace'] = ws_name
        
        await query.edit_message_text(
            f"📥 <b>ĐANG CHỜ FILE... [{ws_name}]</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"Vui lòng <b>thả (drop) 1 file .md</b> vào đây.\n"
            f"💡 File sẽ được ghi đè trực tiếp vào workspace <code>{ws_name}</code>.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Quay lại", callback_data="menu_tg_light_ws_select")]]),
            parse_mode='HTML'
        )
        return
    if callback_data == "act_tg_restore_confirm":
        file_path = context.user_data.get('pending_restore_path')
        mode = context.user_data.get('pending_restore_mode')
        workspace = context.user_data.get('pending_restore_workspace')
        
        if not file_path or not os.path.exists(file_path):
            await query.edit_message_text("❌ <b>Lỗi:</b> Không tìm thấy dữ liệu tạm thời để restore.")
            return

        msg_loading = f"⏳ <b>Đang khôi phục...</b>"
        await query.edit_message_text(msg_loading, parse_mode='HTML')
        
        try:
            import tarfile
            ok, msg = False, "Lỗi không xác định"
            
            # --- CASE 1: FULL RESTORE ---
            if mode == 'full' or (not mode and file_path.endswith('.tar.gz')):
                with tarfile.open(file_path, "r:gz") as tar:
                    tar.extractall(path=get_openclaw_home().parent) # Parent vì trong tar đã có folder .openclaw hoặc workspace
                ok, msg = True, "Đã khôi phục toàn bộ nội dung từ file nén."

            # --- CASE 2: LIGHT RESTORE (Workspace Specific) ---
            elif mode == 'light':
                if not workspace: raise Exception("Thiếu thông tin workspace đích.")
                dest_ws = get_openclaw_home() / workspace
                
                # Check file type
                if not file_path.endswith('.md'):
                    raise Exception("File Restore Light phải là định dạng .md")

                if not dest_ws.exists(): 
                     # Nếu workspace chưa có, tạo mới
                     os.makedirs(dest_ws, exist_ok=True)
                
                # Copy file .md vào workspace
                file_name = os.path.basename(file_path).split("temp_upload_")[-1] # Lấy tên gốc
                # Fix: temp_upload_filename -> filename
                if file_name.startswith("temp_upload_"): file_name = file_name.replace("temp_upload_", "")
                
                dest_file = dest_ws / file_name
                shutil.copy2(file_path, dest_file)
                
                ok, msg = True, f"Đã khôi phục file <b>{file_name}</b> vào workspace 📂 <code>{workspace}</code>."

            # --- CASE 3: SYSTEM CONFIG ---
            elif mode == 'system' or (not mode and file_path.endswith('.json')):
                # Copy và đổi tên thành openclaw.json
                ok, msg = perform_copy(file_path, BACKUP_SRC)
                if ok:
                    # Chạy lệnh restart gateway
                    _, _ = run_shell_command("openclaw gateway restart")
                    msg = "Restore cấu hình thành công, đã khởi động lại Gateway."
            
            # --- CLEANUP & FINISH ---
            if ok:
                keyboard = [
                    [InlineKeyboardButton("◀️ Quay về Restore", callback_data="menu_restore_select")],
                    [InlineKeyboardButton("🏠 Về Main Menu", callback_data="back_main")]
                ]
                await query.edit_message_text(f"✅ <b>RESTORE THÀNH CÔNG!</b>\n{msg}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            else:
                await query.edit_message_text(f"❌ <b>Thất bại:</b> {msg}", parse_mode='HTML')
                
        except Exception as e:
            await query.edit_message_text(f"❌ <b>Lỗi Restore:</b> {e}", parse_mode='HTML')
        finally:
            # Cleanup: Luôn chạy để đảm bảo không sót file temp trên VPS
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"🗑️ Đã dọn dẹp file tạm: {file_path}")
                except Exception as ex:
                    logger.error(f"❌ Lỗi dọn dẹp file {file_path}: {ex}")
            context.user_data.pop('pending_restore_path', None)
            context.user_data.pop('pending_restore_is_full', None)
            context.user_data.pop('pending_restore_mode', None)
            context.user_data.pop('pending_restore_workspace', None)
        return
    if callback_data == "act_tg_restore_cancel":
        file_path = context.user_data.get('pending_restore_path')
        if file_path and os.path.exists(file_path): os.remove(file_path)
        context.user_data.pop('pending_restore_path', None)
        await query.edit_message_text("❌ <b>Đã hủy bỏ</b> việc Restore từ Telegram.")
        return
    if callback_data == "menu_gateway":
        keyboard = [[InlineKeyboardButton("▶️ Start", callback_data="cmd_gateway_start")],[InlineKeyboardButton("⏹️ Stop", callback_data="cmd_gateway_stop")],[InlineKeyboardButton("🔄 Restart", callback_data="cmd_gateway_restart")],[InlineKeyboardButton("◀️ Quay về", callback_data="back_main")]]
        await query.edit_message_text("🌐 <b>GATEWAY CONTROL</b>\nChọn lệnh:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return
    if callback_data.startswith("cmd_gateway_"):
        action = callback_data.replace("cmd_gateway_", "")
        await execute_shell_command_callback(query, f"openclaw gateway {action}", f"Gateway {action.upper()}")
        return
    if callback_data == "menu_info":
        keyboard = [[InlineKeyboardButton("📡 Channels", callback_data="cmd_list_channels")],[InlineKeyboardButton("🕵️ Agents", callback_data="cmd_list_agents")],[InlineKeyboardButton("🧵 Sessions", callback_data="cmd_list_sessions")],[InlineKeyboardButton("◀️ Quay về", callback_data="back_main")]]
        await query.edit_message_text("ℹ️ <b>INFO LISTS</b>\nChọn thông tin cần xem:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return
    if callback_data.startswith("cmd_list_"):
        what = callback_data.replace("cmd_list_", "")
        cmd = f"openclaw {what} list" if what != "sessions" else "openclaw sessions"
        await execute_shell_command_callback(query, cmd, f"List {what.upper()}")
        return
    if callback_data == "menu_manual":
        keyboard = [[InlineKeyboardButton("🤖 Claude", callback_data="menu_claude_0")], [InlineKeyboardButton("💎 Gemini", callback_data="menu_gemini_0")], [InlineKeyboardButton("🚀 GPT", callback_data="menu_gpt_0")], [InlineKeyboardButton("◀️ Quay về", callback_data="back_main")]]
        await query.edit_message_text("🛠 <b>MODEL MANUAL</b>\nChọn loại AI:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return
    if callback_data == "menu_random":
        keyboard = [[InlineKeyboardButton("🎲 Random Gemini", callback_data="randomai_gemini")], [InlineKeyboardButton("🎰 Random Cliproxy", callback_data="random_ai_switch")], [InlineKeyboardButton("◀️ Quay về", callback_data="back_main")]]
        await query.edit_message_text("🎲 <b>MODEL RANDOM</b>\nChọn chế độ random:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return
    if callback_data.startswith("menu_") and "_" in callback_data:
        parts = callback_data.split("_")
        if len(parts) >= 3:
            model_type, page = parts[1], int(parts[2])
            reply_markup, message = create_model_menu(model_type, page)
            if reply_markup: await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
            return
    if callback_data.startswith("select_"):
        model_path = callback_data.replace("select_", "").replace("_", "/", 1)
        await execute_shell_command_callback(query, f"openclaw models set {model_path}", "Switch Model")
        return
    if callback_data == "start_manual_mode":
        # Không làm gì ở đây, handler ConversationHandler sẽ tự bắt entry_point
        return

    selected_alias = f"/{callback_data}"
    commands = load_commands()
    for cmd in commands:
        if cmd.get("command_alias") == selected_alias:
            await execute_shell_command_callback(query, cmd.get("command"), f"Exec {selected_alias}")
            return

# Load Global Config
config = read_config(CONFIG_PATH)
CLIPROXY_URL = config.get('API_KEYS', 'CLIPROXY_MANAGEMENT_URL', fallback="")
CLIPROXY_KEY = config.get('API_KEYS', 'CLIPROXY_MANAGEMENT_KEY', fallback="")

def main():
    """Khởi động bot"""
    TOKEN = config.get('API_KEYS', 'TELEGRAM_TOKEN_OPENCLAW_ADMIN', fallback=None)
    if not TOKEN:
        print(f"❌ Lỗi: Không tìm thấy TELEGRAM_TOKEN_OPENCLAW_ADMIN trong {CONFIG_PATH}")
        sys.exit(1)
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("cmd", ai_command))
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('manual', manual_command_start),
            CallbackQueryHandler(manual_command_start, pattern="^start_manual_mode$")
        ],
        states={WAITING_FOR_CMD: [MessageHandler(filters.TEXT & ~filters.COMMAND, manual_command_exec)]},
        fallbacks=[CommandHandler('cancel', manual_command_cancel)],
        per_message=False
    )
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_request))
    application.add_handler(CallbackQueryHandler(button_callback))
    # Cấu hình các Chat ID nhận báo cáo (Hỗ trợ cả ID cá nhân và ID Kênh đồng thời)
    targets = []
    id_admin = config.get("API_KEYS", "ADMIN_CHAT_ID", fallback=None)
    id_legacy = config.get("API_KEYS", "TELEGRAM_CHAT_ID_CHANNEL_LOG", fallback=None)
    
    if id_admin: targets.append(id_admin)
    if id_legacy and id_legacy not in targets: targets.append(id_legacy)

    if targets and application.job_queue:
        for idx, target_id in enumerate(targets):
            application.job_queue.run_repeating(
                scheduled_report, 
                interval=7200, 
                first=10 + (idx * 5), # Delay nhẹ giữa các job
                chat_id=target_id, 
                name=f"periodic_report_{idx}"
            )
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
