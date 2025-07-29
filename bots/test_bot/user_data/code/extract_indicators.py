import os
import sys
import json
import argparse
import glob
import re
import pandas as pd
import importlib.util
import inspect  # <-- needed for dynamic __init__ check

def find_user_data_dir():
    """Walk up parent dirs until config.json is found."""
    here = os.path.abspath(os.path.dirname(__file__))
    last = None
    while here != last:
        if os.path.exists(os.path.join(here, 'config.json')):
            return here
        last = here
        here = os.path.dirname(here)
    print("[ERROR] Could not find user_data root with config.json. Aborting.")
    sys.exit(1)

def find_strategy_file(strategy_name, strategy_dir, recursive=True):
    print(f"[DEBUG] Looking for strategy '{strategy_name}' in: {strategy_dir} (recursive={recursive})")
    pattern = re.compile(rf'class\s+{strategy_name}\s*\(.*IStrategy.*\)\s*:')
    if recursive:
        files = glob.glob(os.path.join(strategy_dir, '**/*.py'), recursive=True)
    else:
        files = glob.glob(os.path.join(strategy_dir, '*.py'))
    print(f"[DEBUG] Found {len(files)} python files in strategies directory")
    for file in files:
        print(f"[DEBUG] Checking {file}")
        with open(file, 'r', encoding='utf-8') as f:
            code = f.read()
            if pattern.search(code):
                print(f"[DEBUG] Matched class in {file}")
                return file
    print(f"[DEBUG] No matching strategy class found in any file")
    return None

def dynamic_import_strategy(strategy_path, strategy_name):
    print(f"[DEBUG] Importing strategy class {strategy_name} from {strategy_path}")
    module_name = os.path.splitext(os.path.basename(strategy_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, strategy_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return getattr(module, strategy_name, None)

def load_config(path):
    print(f"[DEBUG] Loading config: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--strategy', '-s', required=True, help='Strategy class name')
    parser.add_argument('--timeframe', '-i', help='Timeframe (e.g. 5m)')
    parser.add_argument('--pair', '-p', help='Pair (e.g. BTC/USDT)')
    parser.add_argument('--timerange', help='YYYYMMDD-YYYYMMDD')
    parser.add_argument('--config', '-c', help='Config path (default: auto-find root)')
    parser.add_argument('--output', help='CSV output path', default='indicator_output.csv')  # no longer used!
    parser.add_argument('--strategy-path', help='Custom strategies path')
    args = parser.parse_args()

    # Find freqtrade user_data root dir by looking for config.json
    user_data_dir = find_user_data_dir()
    print(f"[DEBUG] Detected freqtrade user_data root: {user_data_dir}")

    # Now, set everything RELATIVE to that root:
    strat_dir = args.strategy_path or os.path.join(user_data_dir, 'strategies')
    data_dir = os.path.join(user_data_dir, 'data')
    config_path = args.config or os.path.join(user_data_dir, 'config.json')

    print(f"[DEBUG] strat_dir: {strat_dir}")
    print(f"[DEBUG] data_dir: {data_dir}")
    print(f"[DEBUG] config: {config_path}")

    # Load config.json
    config = load_config(config_path) if os.path.exists(config_path) else {}

    # CLI > config > fallback
    timeframe = args.timeframe or config.get('timeframe', '5m')
    # Pair fallback: if not provided, use first in whitelist if present, else error
    if args.pair:
        pair = args.pair
    else:
        pairlist = (config.get('exchange', {}) or {}).get('pair_whitelist') or []
        if pairlist:
            pair = pairlist[0]
        else:
            print("[ERROR] No pair provided and no pair_whitelist in config. Use --pair or add pair_whitelist.")
            sys.exit(1)
    timerange = args.timerange or config.get('timerange', None)
    # output = args.output  # <-- not used anymore!

    print(f"[DEBUG] timeframe: {timeframe}")
    print(f"[DEBUG] pair: {pair}")
    print(f"[DEBUG] timerange: {timerange}")

    # Strategy discovery (Freqtrade-style)
    strat_file = find_strategy_file(args.strategy, strat_dir, recursive=True)
    if not strat_file:
        print(f"Strategy {args.strategy} not found in {strat_dir}")
        sys.exit(1)
    print(f"[DEBUG] Found strategy file: {strat_file}")

    # Import
    strat_cls = dynamic_import_strategy(strat_file, args.strategy)
    if not strat_cls:
        print(f"Could not import {args.strategy} from {strat_file}")
        sys.exit(1)

    # Get exchange name from config (required)
    exchange_name = config.get('exchange', {}).get('name', None)
    if not exchange_name:
        print('[ERROR] Exchange name not found in config.json.')
        sys.exit(1)
    print(f"[DEBUG] exchange_name: {exchange_name}")

    # --- [Robust OHLCV file location logic] ---
    pair_base = pair.replace('/', '').replace('_', '')      # BTC/USDT -> BTCUSDT
    pair_uscore = pair.replace('/', '_')                    # BTC/USDT -> BTC_USDT

    data_exchange_dir = os.path.join(data_dir, exchange_name)
    feather1 = os.path.join(data_exchange_dir, f"{pair_base}-{timeframe}.feather")
    feather2 = os.path.join(data_exchange_dir, f"{pair_uscore}-{timeframe}.feather")
    csv1 = os.path.join(data_exchange_dir, f"{pair_base}-{timeframe}.csv")
    csv2 = os.path.join(data_exchange_dir, f"{pair_uscore}-{timeframe}.csv")

    print(f"[DEBUG] Looking for OHLCV file (prefer feather):\n  {feather1}\n  {feather2}\n  {csv1}\n  {csv2}")

    ohlcv_file = None
    if os.path.exists(feather1):
        ohlcv_file = feather1
        print(f"[DEBUG] Using OHLCV feather: {feather1}")
        df = pd.read_feather(ohlcv_file)
    elif os.path.exists(feather2):
        ohlcv_file = feather2
        print(f"[DEBUG] Using OHLCV feather: {feather2}")
        df = pd.read_feather(ohlcv_file)
    elif os.path.exists(csv1):
        ohlcv_file = csv1
        print(f"[DEBUG] Using OHLCV CSV: {csv1}")
        df = pd.read_csv(ohlcv_file)
    elif os.path.exists(csv2):
        ohlcv_file = csv2
        print(f"[DEBUG] Using OHLCV CSV: {csv2}")
        df = pd.read_csv(ohlcv_file)
    else:
        print(f"[ERROR] OHLCV file not found in any of these locations.")
        sys.exit(1)
    # --- end robust OHLCV block ---

    # Standardize columns
    df.columns = [c.lower() for c in df.columns]
    if 'time' not in df.columns:
        if 'date' in df.columns:
            df['time'] = pd.to_datetime(df['date']).astype(int) // 10**9
        else:
            print('Missing time or date column.')
            sys.exit(1)
    # Timerange
    if timerange:
        tmin, tmax = timerange.split('-')
        tmin = int(pd.Timestamp(tmin, tz='UTC').timestamp())
        tmax = int(pd.Timestamp(tmax, tz='UTC').timestamp())
        df = df[(df['time'] >= tmin) & (df['time'] <= tmax)]

    # ---- This is the NEW block (instantiate with config if possible) ----
    strat = None
    try:
        sig = inspect.signature(strat_cls)
        if 'config' in sig.parameters:
            strat = strat_cls(config=config)
        else:
            strat = strat_cls()
    except TypeError as e:
        print(f"[WARN] Could not instantiate with config: {e}")
        try:
            strat = strat_cls()
        except Exception as e2:
            print(f"[ERROR] Failed to instantiate strategy: {e2}")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to instantiate strategy: {e}")
        sys.exit(1)

    if not hasattr(strat, 'populate_indicators'):
        print("Strategy does not have populate_indicators")
        sys.exit(1)
    print("[DEBUG] Running populate_indicators()")
    df_out = strat.populate_indicators(df.copy(), metadata={})
    base_cols = {'time', 'date', 'open', 'high', 'low', 'close', 'volume'}
    indicator_cols = [c for c in df_out.columns if c not in base_cols]
    print(f"[DEBUG] Indicator columns: {indicator_cols}")

    # --- NEW OUTPUT LOGIC: Save always to data/indicator_data/indicator_data_<StrategyName>.csv ---
    indicator_dir = os.path.join(data_dir, 'indicator_data')
    os.makedirs(indicator_dir, exist_ok=True)
    output = os.path.join(indicator_dir, f"indicator_data_{args.strategy}.csv")
    print(f"[DEBUG] Output path set to: {output}")

    df_out[['time'] + indicator_cols].to_csv(output, index=False)
    print(f"Output: {output}")

if __name__ == '__main__':
    main()
