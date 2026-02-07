import os
import subprocess
import glob
from pathlib import Path

def run_command(cmd, cwd=None):
    """Chạy lệnh shell và trả về kết quả."""
    try:
        # Sử dụng shell=True để hỗ trợ các ký tự mở rộng như ~
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def perform_restore(file_name=None):
    home = str(Path.home())
    workspace = os.path.join(home, ".openclaw/workspace")
    repo_bot_path = os.path.join(workspace, "Github/openclawbot")
    backup_dir = os.path.join(repo_bot_path, "backup")
    
    print(f"🐻 Gấu đang chuẩn bị quy trình khôi phục hệ thống...")
    
    # 1. Kiểm tra thư mục backup
    if not os.path.exists(backup_dir):
        print(f"❌ Lỗi: Không tìm thấy thư mục backup tại {backup_dir}")
        return

    # 2. Tìm danh sách các bản backup
    backups = glob.glob(os.path.join(backup_dir, "*.tar.gz"))
    backups.sort(reverse=True) # Mới nhất lên đầu
    
    if not backups:
        print("❌ Lỗi: Không có bản backup nào trong thư mục.")
        return

    # 3. Chọn file để restore
    if file_name:
        target_file = os.path.join(backup_dir, file_name)
    else:
        target_file = backups[0] # Mặc định lấy bản mới nhất
    
    if not os.path.exists(target_file):
        print(f"❌ Lỗi: Không tìm thấy file {target_file}")
        return

    print(f"📦 Đang khôi phục từ bản: {os.path.basename(target_file)}")
    print(f"⚠️ Cảnh báo: Việc này sẽ ghi đè lên các cấu hình hiện tại trong .openclaw")
    
    # 4. Thực hiện lệnh giải nén
    # -C {home} để giải nén vào đúng vị trí gốc
    tar_cmd = f'tar -xzvf "{target_file}" -C "{home}"'
    
    print("⏳ Đang thực hiện giải nén...")
    success, output = run_command(tar_cmd)
    
    if success:
        print(f"✅ Khôi phục thành công!")
        print(f"🚀 Gấu Đại Ca vui lòng kiểm tra lại hệ thống hoặc restart Gateway nếu cần.")
    else:
        print(f"❌ Lỗi trong quá trình khôi phục: {output}")

if __name__ == "__main__":
    # Gấu Đại Ca có thể truyền tên file vào đây nếu muốn restore bản cũ hơn
    # Ví dụ: perform_restore("openclaw_backup_20260204_120000.tar.gz")
    perform_restore()
