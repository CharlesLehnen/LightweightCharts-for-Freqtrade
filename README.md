# Lightweight-Charts for Freqtrade Guide

[Freqtrade](https://github.com/freqtrade/freqtrade) is an open-source cryptocurrency bot managment system, complete with capabilities for backtesting and deployment. 

[TradingView](https://www.tradingview.com/pricing/?share_your_love=talker91) is a powerful commercial charting platform that is widely used in the trading community. They provide [Lightweight-Charts](https://www.tradingview.com/lightweight-charts/), an open-source Javascript based library based on for creating financial charts in web applications.

Compared to TradingView/Lightweight-Charts, Freqtrade's built-in plotting capabilities are limited. These [Plotly](https://plotly.com/) based charts do not providethe same level of interactivity or visual appeal.

I was inspired by the [Lightweight-Charts-Python](https://github.com/louisnw01/lightweight-charts-python) library to create a solution that allows Freqtrade users to visualize their trading strategies using Lightweight-Charts. This requires a Javascript script to be run inside of the Freqtrade Docker container. 

If this is your first time setting up Freqtrade, see the [Initialization section](#initialization) below and refer to the [Freqtrade Quickstart Guide](https://www.freqtrade.io/en/latest/quickstart/).

If Freqtrade is already set up, you can skip to the [Lightweight-Charts Plotting section](#lightweight-charts-plotting) section.



## Lightweight-Charts Plotting
1) Generate a backtest (*see [Backtesting](#backtesting) section below*)
2) Run [`code/feather_to_csv.py`(code/feather_to_csv.py) to convert the feather files Freqtrade generated to CSVs
can I make this a link to a specific file?

3) Run [`code/unzip_backtest_results.py`](code/unzip_backtest_results.py) to unzip backtest results

4) In terminal:
    - `docker-compose up -d`
    - `docker exec -it freqtrade bash`
    - `python3 code/extract_indicators.py --strategy <DesiredStrategyName>`

5) Open [`code/lightweight-charts.html`](code/lightweight-charts.html) in browser. Personally, I use LiveServer VSCode extension. Use the file pickers to select the newly generated files in:
    - bots/<bot>/user_data/<exchange>/backtest_results/<desired_backtest_results>/<desired_backtest_results.json>
    - bots/<bot>/user_data/<exchange>/<Pair_Timeframe.csv>
    - bots/<bot>/user_data/data/indicator_data

---


## Initialization
*This is a guide to how I set-up Freqtrader on Windows. There are many other ways to do so.*

1) Install Docker Desktop (this may require you to update WSL too)
2) Open Docker Desktop
2) In Anaconda prompt:
    - cd to Git repo folder
    - `conda create -n <env name> python=3.10` 
    - `conda activate <env name>`
    - `conda install pandas matplotlib numpy jupyter`
    - `pip install freqtrade ccxt`

3) [In terminal:](https://www.freqtrade.io/en/2020.11/docker_quickstart/)
    - `mkdir bots/<bot>`
    - `cd bots/<bot>`
    - `curl https://raw.githubusercontent.com/freqtrade/freqtrade/stable/docker-compose.yml -o docker-compose.yml`
    - `docker-compose pull`
    - `docker-compose run --rm freqtrade create-userdir --userdir user_data`
    - `docker-compose run --rm freqtrade new-config --config user_data/config.json`
    - In `command:` section of "docker-compose.yml," need to switch to strategy you want to run via `--strategy <StrategyName>`


## Backteststing
0) In bots/<bot>/user_data/config.json
- Be sure set to `"method": "StaticPairList", ` and pairs selected in the `pairs_whitelist`. For example: "BTC/USDT"
1) In terminal:
    - `docker-compose up -d`
    - `docker exec -it freqtrade bash`
        - If this doesn't work, can double check name with `docker ps`
    - `freqtrade download-data`
        - To force refresh, may need to delete current files to overwrite them
    - `freqtrade backtesting --export=trades --strategy <StrategyName> --timeframe <Xy> --timerange <YEARMoDa-YEARMoDa>`
        - Note that timeframe and timerange are optional, both will revert to defaults

---

# License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

Only under the following terms:
- Attribution — You must give appropriate credit: Charles Lehnen
- NonCommercial — You may not use the material for commercial purposes without gaining commercial licensing.
- For commercial licensing - Please contact CharlesLehnen@gmail.com

You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

See LICENSE for full details. 

