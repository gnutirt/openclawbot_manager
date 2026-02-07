import os
import subprocess
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None):
    """Chạy lệnh shell và trả về kết quả."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def perform_backup():
    home = str(Path.home())
    workspace = os.path.join(home, ".openclaw/workspace")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"openclaw_backup_{timestamp}.tar.gz"
    
    # Các đường dẫn quan trọng
    repo_bot_path = os.path.join(workspace, "Github/openclawbot")
    backup_dest_dir = os.path.join(repo_bot_path, "backup")
    
    # Đảm bảo thư mục backup tồn tại trong repo
    if not os.path.exists(backup_dest_dir):
        os.makedirs(backup_dest_dir, exist_ok=True)
    
    # Ghi đè file openclaw.json vào thư mục backup trước
    config_src = os.path.join(home, ".openclaw/openclaw.json")
    config_dest = os.path.join(backup_dest_dir, "openclaw.json")
    if os.path.exists(config_src):
        print(f"📑 Đang sao chép cấu hình hệ thống (openclaw.json)...")
        run_command(f'cp "{config_src}" "{config_dest}"')

    backup_file_path = os.path.join(backup_dest_dir, backup_name)
    
    print(f"🐻 Gấu đang tiến hành sao lưu hệ thống...")
    print(f"📦 Đang đóng gói dữ liệu vào: {backup_name}")
    
    # Danh sách loại trừ để giảm dung lượng (không backup môi trường ảo và log)
    exclude_list = [
        ".openclaw/workspace/cognee_env",
        ".openclaw/workspace/Github",
        ".openclaw/workspace/antigravity",
        ".openclaw/workspace/squashfs-root",
        ".openclaw/agents/*/browser-data", # Loại trừ data trình duyệt của agents
        "*.log",
        "*.tmp",
        "*.pyc",
        "__pycache__"
    ]
    
    exclude_args = " ".join([f'--exclude="{item}"' for item in exclude_list])
    
    # Lệnh nén tar
    tar_cmd = f'tar {exclude_args} -czf "{backup_file_path}" -C "{home}" .openclaw'
    
    success, output = run_command(tar_cmd)
    
    if success:
        size_mb = os.path.getsize(backup_file_path) / (1024 * 1024)
        print(f"✅ Đã nén xong! Dung lượng: {size_mb:.2f} MB")
        
        # Thực hiện Git để đẩy lên cloud
        print("☁️ Đang đồng bộ bản backup lên GitHub...")
        
        # Chỉ giữ lại bản backup mới nhất trong thư mục để tránh làm nặng repo GitHub (tùy chọn)
        # Nếu Gấu Đại Ca muốn giữ nhiều bản, bỏ qua phần xóa này.
        
        git_cmds = [
            "git add .",
            f'git commit -m "Auto-backup: {timestamp}"',
            "git push"
        ]
        
        all_git_ok = True
        for cmd in git_cmds:
            ok, msg = run_command(cmd, cwd=repo_bot_path)
            if not ok:
                print(f"⚠️ Cảnh báo Git ({cmd}): {msg}")
                # Không break để cố gắng chạy tiếp các lệnh sau nếu có thể
        
        if all_git_ok:
            print(f"🚀 Tuyệt vời! Hệ thống đã được sao lưu và bảo vệ trên mây.")
    else:
        print(f"❌ Lỗi trong quá trình nén: {output}")

if __name__ == "__main__":
    perform_backup()
