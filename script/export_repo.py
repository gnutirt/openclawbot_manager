
import os
import shutil
import re

def ignore_patterns(path, names):
    """
    Returns a set of names to ignore.
    path: current directory being visited
    names: list of filenames in that directory
    """
    ignored = set()
    
    # Get the relative path from the root of the copy operation
    # This is a bit tricky with copytree's ignore callback, so we check names directly
    
    for name in names:
        # 1. Global exclusions
        if name in ['docker', 'docs', '.git', '__pycache__', 'export', '.antigravity', '.idea', 'venv', '.venv']:
            ignored.add(name)
            continue
            
        # 2. Pattern exclusions (starts with 'test')
        # Check if it's a file or directory starting with 'test'
        if name.startswith('test'):
            ignored.add(name)
            continue

        # 3. Specific file exclusions (if any)
        if name.endswith('.pyc') or name.endswith('.backup'):
            ignored.add(name)

    return ignored

def sanitize_config(config_path):
    """
    Reads the config file and clears all values, keeping keys and comments.
    """
    if not os.path.exists(config_path):
        print(f"⚠️ Config file not found at {config_path}")
        return

    print(f"🧹 Sanitizing config file: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#') or stripped.startswith('['):
            new_lines.append(line)
            continue
        
        # Check for key = value pair
        if '=' in line:
            # Split by the first equals sign
            key, _ = line.split('=', 1)
            # Keep the indentation and the key, but remove the value
            # We assume standard "KEY = VALUE" format
            new_lines.append(f"{key.rstrip()} = \n")
        else:
            new_lines.append(line)

    with open(config_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("✅ Config sanitized.")

def export_repo():
    source_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Repo root
    export_dir = os.path.join(source_dir, 'export')

    print(f"🚀 Starting export from {source_dir} to {export_dir}")

    # Remove existing export directory if it exists
    if os.path.exists(export_dir):
        print(f"🗑️ Removing existing export directory: {export_dir}")
        shutil.rmtree(export_dir)

    # Copy the repository
    try:
        shutil.copytree(source_dir, export_dir, ignore=ignore_patterns)
        print("✅ Repository files copied.")
    except Exception as e:
        print(f"❌ Error copying repository: {e}")
        return

    # Sanitize config.cfg
    config_path = os.path.join(export_dir, 'config', 'config.cfg')
    sanitize_config(config_path)

    print("\n🎉 Export completed successfully!")
    print(f"📂 Output directory: {export_dir}")

if __name__ == "__main__":
    export_repo()
