#other_utils.py
import os
import configparser
import codecs
from pathlib import Path
from datetime import datetime, timedelta, timezone
def read_config(path: str = "config/config.cfg"):
    """
    Đọc file cấu hình .cfg với cơ chế tự động nhận diện bảng mã (Encoding).
    Hỗ trợ UTF-8 cho tiếng Việt và CP1252 cho các định dạng cũ.
    """
    cfg = configparser.ConfigParser()
    
    # Kiểm tra file có tồn tại không trước khi đọc
    if not os.path.exists(path):
        print(f"⚠️ Warning: Configuration file not found at: {path}")
        return cfg

    # Danh sách encoding thử nghiệm (quan trọng: utf-8-sig để bỏ qua BOM)
    encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'latin-1']

    for encoding in encodings:
        try:
            # Thử đọc với encoding hiện tại
            with codecs.open(path, "r", encoding) as f:
                cfg.read_file(f)
            return cfg
        except (UnicodeDecodeError, Exception):
            continue
            
    print(f"❌ Error: Could not read config file {path} with any supported encoding.")
    return cfg

def get_config_value(cfg, section: str, key: str, default: any = None):
    """
    Hàm tiện ích để lấy giá trị từ config mà không lo bị crash nếu thiếu key.
    """
    return cfg.get(section, key, fallback=default)
def get_vietnam_time():
    """Lấy thời gian hiện tại theo múi giờ Việt Nam (UTC+7)"""
    tz_vn = timezone(timedelta(hours=7))
    return datetime.now(tz_vn).strftime("%H:%M - %d/%m/%Y")
if __name__ == "__main__":
    from pathlib import Path
    
    # Lấy đường dẫn gốc của project (thư mục cha của utils)
    ROOT = Path(__file__).resolve().parent.parent
    
    # Kết nối đến file config chuẩn
    TEST_PATH = str(ROOT / "config" / "config.cfg")
    
    print(f"--- 🔎 Testing config at: {TEST_PATH} ---")
    config = read_config(TEST_PATH)
    
    if config.sections():
        print(f"✅ Đọc thành công file: {TEST_PATH}")
        print(f"Các mục tìm thấy: {config.sections()}")
    else:
        print("❌ File config rỗng hoặc không tìm thấy đúng đường dẫn.")