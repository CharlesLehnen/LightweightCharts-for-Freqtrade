#!/usr/bin/env python3
"""
Main orchestrator for Freqtrade backtesting + LightweightCharts visualization workflow.
Cross-platform (Windows/Linux/Mac).
"""
import os
import sys
import json
import subprocess
import glob
import re
from pathlib import Path


def print_header(text):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def find_bots():
    """Find all bot directories under bots/"""
    # Go up one level from code/ to project root
    bots_dir = Path(__file__).parent.parent / 'bots'
    if not bots_dir.exists():
        print("[ERROR] No 'bots' directory found.")
        print(f"[DEBUG] Looked in: {bots_dir.absolute()}")
        return []
    
    bot_list = []
    for item in bots_dir.iterdir():
        if item.is_dir() and (item / 'user_data').exists():
            bot_list.append(item.name)
    
    return sorted(bot_list)


def find_strategies(bot_name):
    """Find all strategy files in bot's strategies directory"""
    strat_dir = Path(__file__).parent.parent / 'bots' / bot_name / 'user_data' / 'strategies'
    if not strat_dir.exists():
        print(f"[ERROR] Strategies directory not found: {strat_dir}")
        return []
    
    strategy_files = glob.glob(str(strat_dir / '**/*.py'), recursive=True)
    strategies = []
    
    # Extract class names that inherit from IStrategy
    pattern = re.compile(r'class\s+(\w+)\s*\(.*IStrategy.*\)\s*:')
    for file in strategy_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = pattern.findall(content)
            strategies.extend(matches)
    
    return sorted(set(strategies))


def load_config(bot_name):
    """Load config.json for a bot"""
    config_path = Path(__file__).parent.parent / 'bots' / bot_name / 'user_data' / 'config.json'
    if not config_path.exists():
        print(f"[WARN] Config not found: {config_path}")
        return {}
    
    print(f"[DEBUG] Loading config: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_container_name(bot_name):
    """Get running container name for a bot"""
    bot_dir = Path(__file__).parent.parent / 'bots' / bot_name
    compose_file = bot_dir / 'docker-compose.yml'
    
    if not compose_file.exists():
        print(f"[ERROR] docker-compose.yml not found in {bot_dir}")
        return None
    
    # Try to read container_name from docker-compose.yml
    with open(compose_file, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'container_name:\s*(\S+)', content)
        if match:
            return match.group(1)
    
    # Fallback: use docker ps
    print("[DEBUG] Container name not in docker-compose.yml, checking docker ps...")
    result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'],
                          capture_output=True, text=True)
    names = result.stdout.strip().split('\n')
    
    # Try to match bot name
    for name in names:
        if bot_name.replace('_', '') in name.replace('_', ''):
            return name
    
    # Return first freqtrade container if found
    for name in names:
        if 'freqtrade' in name.lower():
            return name
    
    return None


def ensure_container_running(bot_name):
    """Ensure docker container is running"""
    print_header("Checking Docker Container")
    
    bot_dir = Path(__file__).parent.parent / 'bots' / bot_name
    
    # Check if container is running
    container_name = get_container_name(bot_name)
    if container_name:
        result = subprocess.run(['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Names}}'],
                              capture_output=True, text=True)
        if container_name in result.stdout:
            print(f"[INFO] Container '{container_name}' is running")
            return container_name
    
    print(f"[INFO] Starting container for bot '{bot_name}'...")
    subprocess.run(['docker', 'compose', 'up', '-d'], cwd=bot_dir, check=True)
    
    container_name = get_container_name(bot_name)
    if not container_name:
        print("[ERROR] Could not determine container name")
        sys.exit(1)
    
    print(f"[INFO] Container '{container_name}' started")
    return container_name


def run_backtest(bot_name, strategy, config):
    """Run freqtrade backtesting"""
    print_header(f"Running Backtest: {strategy}")
    
    container_name = ensure_container_running(bot_name)
    
    timeframe = config.get('timeframe', '1h')
    timerange = input(f"[INPUT] Timerange (YYYYMMDD-YYYYMMDD) [press enter for default]:").strip()
    
    cmd = [
        'docker', 'exec', container_name,
        'freqtrade', 'backtesting',
        '--export', 'trades',
        '--strategy', strategy,
        '--timeframe', timeframe
    ]
    
    if timerange:
        cmd.extend(['--timerange', timerange])
    
    print(f"[DEBUG] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("[ERROR] Backtest failed")
        sys.exit(1)
    
    print("[SUCCESS] Backtest completed")


def prepare_visualization_files(bot_name, strategy):
    """Run all scripts needed to prepare files for LightweightCharts"""
    print_header("Preparing Visualization Files")
    
    bot_dir = Path(__file__).parent.parent / 'bots' / bot_name
    code_dir = Path(__file__).parent
    container_name = ensure_container_running(bot_name)
    
    # 1. Convert feather to CSV
    print("\n[STEP 1/4] Converting feather files to CSV...")
    feather_script = code_dir / 'feather_to_csv.py'
    if feather_script.exists():
        subprocess.run([sys.executable, str(feather_script)], check=True)
        print("[SUCCESS] Feather files converted")
    else:
        print(f"[WARN] feather_to_csv.py not found at {feather_script}")
    
    # 2. Unzip backtest results
    print("\n[STEP 2/4] Unzipping backtest results...")
    unzip_script = code_dir / 'unzip_backtest_results.py'
    if unzip_script.exists():
        subprocess.run([sys.executable, str(unzip_script)], check=True)
        print("[SUCCESS] Backtest results unzipped")
    else:
        print(f"[WARN] unzip_backtest_results.py not found at {unzip_script}")
    
    # 3. Copy extract_indicators.py into container if needed
    print("\n[STEP 3/4] Ensuring extract_indicators.py is in container...")
    user_data_code = bot_dir / 'user_data' / 'code'
    user_data_code.mkdir(parents=True, exist_ok=True)
    
    extract_script = code_dir / 'extract_indicators.py'
    if extract_script.exists():
        dest = user_data_code / 'extract_indicators.py'
        with open(extract_script, 'r', encoding='utf-8') as src:
            with open(dest, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        print(f"[SUCCESS] Copied extract_indicators.py to {dest}")
    else:
        print(f"[ERROR] extract_indicators.py not found at {extract_script}")
        sys.exit(1)
    
    # 4. Run extract_indicators.py inside container
    print(f"\n[STEP 4/4] Extracting indicators for {strategy}...")
    cmd = [
        'docker', 'exec', container_name,
        'python3', 'user_data/code/extract_indicators.py',
        '--strategy', strategy
    ]
    
    print(f"[DEBUG] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("[ERROR] Indicator extraction failed")
        sys.exit(1)
    
    print("[SUCCESS] Indicators extracted")
    print_summary(bot_name, strategy)


def print_summary(bot_name, strategy):
    """Print summary of where to find output files"""
    print_header("Files Ready for Visualization")
    
    project_root = Path(__file__).parent.parent
    bot_dir = project_root / 'bots' / bot_name
    config = load_config(bot_name)
    exchange = config.get('exchange', {}).get('name', 'unknown')
    pair_whitelist = config.get('exchange', {}).get('pair_whitelist', [])
    pair = pair_whitelist[0] if pair_whitelist else 'UNKNOWN'
    timeframe = config.get('timeframe', '1h')
    
    pair_base = pair.replace('/', '').replace('_', '')
    pair_uscore = pair.replace('/', '_')
    
    print("\nOpen code/lightweight-charts.html in your browser and load:")
    print(f"\n📊 OHLCV CSV:")
    print(f"   bots/{bot_name}/user_data/data/{exchange}/{pair_base}-{timeframe}_tv.csv")
    print(f"   (or {pair_uscore}-{timeframe}_tv.csv)")
    
    print(f"\n📈 Indicator CSV:")
    print(f"   bots/{bot_name}/user_data/data/indicator_data/indicator_data_{strategy}.csv")
    
    print(f"\n💹 Trades JSON:")
    backtest_dir = bot_dir / 'user_data' / 'backtest_results'
    if backtest_dir.exists():
        # Find most recent backtest result
        results = sorted(backtest_dir.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
        if results:
            print(f"   {results[0].relative_to(project_root)}")
        else:
            print(f"   bots/{bot_name}/user_data/backtest_results/<latest>.json")
    else:
        print(f"   bots/{bot_name}/user_data/backtest_results/<latest>.json")
    
    print("\n")


def interactive_menu():
    """Main interactive menu"""
    print_header("Freqtrade Backtest + Visualization Tool")
    
    # Step 1: Select bot
    bots = find_bots()
    if not bots:
        print("[ERROR] No bots found in bots/ directory")
        sys.exit(1)
    
    print("\nAvailable bots:")
    for i, bot in enumerate(bots, 1):
        print(f"  {i}. {bot}")
    
    bot_idx = int(input("\n[INPUT] Select bot number: ").strip()) - 1
    if bot_idx < 0 or bot_idx >= len(bots):
        print("[ERROR] Invalid selection")
        sys.exit(1)
    
    bot_name = bots[bot_idx]
    print(f"[INFO] Selected bot: {bot_name}")
    
    # Step 2: Select strategy
    strategies = find_strategies(bot_name)
    if not strategies:
        print(f"[ERROR] No strategies found in bots/{bot_name}/user_data/strategies/")
        sys.exit(1)
    
    print(f"\nAvailable strategies in {bot_name}:")
    for i, strat in enumerate(strategies, 1):
        print(f"  {i}. {strat}")
    
    strat_idx = int(input("\n[INPUT] Select strategy number: ").strip()) - 1
    if strat_idx < 0 or strat_idx >= len(strategies):
        print("[ERROR] Invalid selection")
        sys.exit(1)
    
    strategy = strategies[strat_idx]
    print(f"[INFO] Selected strategy: {strategy}")
    
    # Step 3: Action menu
    config = load_config(bot_name)
    
    print("\nWhat would you like to do?")
    print("  1. Run backtest only")
    print("  2. Prepare visualization files only")
    print("  3. Run backtest + prepare visualization files")
    
    action = input("\n[INPUT] Select action: ").strip()
    
    if action == '1':
        run_backtest(bot_name, strategy, config)
    elif action == '2':
        prepare_visualization_files(bot_name, strategy)
    elif action == '3':
        run_backtest(bot_name, strategy, config)
        prepare_visualization_files(bot_name, strategy)
    else:
        print("[ERROR] Invalid action")
        sys.exit(1)
    
    print_header("Done!")


if __name__ == '__main__':
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)