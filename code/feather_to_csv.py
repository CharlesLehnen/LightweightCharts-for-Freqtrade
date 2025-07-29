import os
import pandas as pd

def find_root_dir():
    """Go up to root"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def all_data_dirs(root_dir):
    """Lookup all data folders inside of different bots"""
    bots_dir = os.path.join(root_dir, 'bots')
    if not os.path.isdir(bots_dir):
        print(f"[ERROR] No 'bots' folder found at: {bots_dir}")
        return
    for bot in os.listdir(bots_dir):
        data_dir = os.path.join(bots_dir, bot, 'user_data', 'data')
        if os.path.isdir(data_dir):
            yield data_dir

def main():
    root = find_root_dir()
    print(f"[DEBUG] Using root: {root}")
    for data_dir in all_data_dirs(root):
        print(f"[DEBUG] Processing data dir: {data_dir}")
        for root_, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.feather'):
                    feather_path = os.path.join(root_, file)
                    csv_path = feather_path[:-8] + '_tv.csv'
                    print(f"[INFO] {feather_path} -> {csv_path}")
                    df = pd.read_feather(feather_path)
                    # Convert 'date' or 'time' to seconds-since-epoch if needed
                    if 'date' in df.columns:
                        df['time'] = pd.to_datetime(df['date']).astype(int) // 10**9
                    elif 'time' not in df.columns:
                        print(f"[WARN] No 'date' or 'time' column in {feather_path}, skipping.")
                        continue
                    cols = {c: c for c in ['open', 'high', 'low', 'close', 'volume']}
                    df = df.rename(columns=cols)
                    df[['time','open','high','low','close','volume']].to_csv(csv_path, index=False)

if __name__ == "__main__":
    main()
