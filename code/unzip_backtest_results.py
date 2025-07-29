import zipfile
import os

def find_root_dir():
    """Go up from <root>/code/ to <root>."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def all_backtest_dirs(root_dir):
    """Yield all <root>/bots/<bot>/user_data/backtest_results directories."""
    bots_dir = os.path.join(root_dir, 'bots')
    if not os.path.isdir(bots_dir):
        print(f"[ERROR] No 'bots' folder found at: {bots_dir}")
        return
    for bot in os.listdir(bots_dir):
        bt_dir = os.path.join(bots_dir, bot, 'user_data', 'backtest_results')
        if os.path.isdir(bt_dir):
            yield bt_dir

def unzip_all_in_folder(folder_path):
    """Unzips all .zip files in a single folder (no recursion)."""
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if zipfile.is_zipfile(item_path):
            extract_folder = os.path.join(folder_path, os.path.splitext(item)[0])
            os.makedirs(extract_folder, exist_ok=True)
            with zipfile.ZipFile(item_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
            print(f"Extracted: {item} to {extract_folder}")

def main():
    root = find_root_dir()
    print(f"[DEBUG] Using root: {root}")
    for bt_dir in all_backtest_dirs(root):
        print(f"[DEBUG] Checking for zipfiles in: {bt_dir}")
        unzip_all_in_folder(bt_dir)

if __name__ == "__main__":
    main()
