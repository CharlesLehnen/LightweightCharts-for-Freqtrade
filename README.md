# Lightweight-Charts for Freqtrade Guide

[Freqtrade](https://github.com/freqtrade/freqtrade) is an open-source cryptocurrency bot managment system, complete with capabilities for backtesting and deployment. 

[TradingView](https://www.tradingview.com/pricing/?share_your_love=talker91) is a powerful commercial charting platform that is widely used in the trading community. They provide [Lightweight-Charts](https://www.tradingview.com/lightweight-charts/), an open-source Javascript based library based on for creating financial charts in web applications.

Compared to TradingView/Lightweight-Charts, Freqtrade's built-in plotting capabilities are limited. These [Plotly](https://plotly.com/) based charts do not providethe same level of interactivity or visual appeal.

I was inspired by the [Lightweight-Charts-Python](https://github.com/louisnw01/lightweight-charts-python) library to create a solution that allows Freqtrade users to visualize their trading strategies using Lightweight-Charts. This requires a Javascript script to be run inside of the Freqtrade Docker container. 

If this is your first time setting up Freqtrade, see the [Initialization section](#initialization) below and refer to the [Freqtrade Quickstart Guide](https://www.freqtrade.io/en/latest/quickstart/).

If Freqtrade is already set up, you can skip to the [Lightweight-Charts Plotting section](#lightweight-charts-plotting) section.



## Lightweight-Charts Plotting
1) Generate a backtest (*see [Backtesting](#backtesting) section below*)
2) Run code/feather_to_csv.py to convert the feather files Freqtrade generated to CSVs
can I make this a link to a specific file?

3) Run code/unzip_backtest_results.py to unzip backtest results

4) In terminal:
    - `docker-compose up -d`
    - `docker exec -it freqtrade bash`
    - `python3 code/extract_indicators.py --strategy <DesiredStrategyName>`

5) Open "code/lightweight-charts.html" in browser. Personally, I use LiveServer VSCode extension. Use the file pickers to select the newly generated files in:
    - <freqtrade user>/<bot>/<exchange>/backtest_results/<desired_backtest_results>/<desired_backtest_results.json>
    - <freqtrade user>/<bot>/<exchange>/<Pair_Timeframe.csv>
    - <freqtrade user>/<bot>/data/indicator_data



## Initialization:
*This is a guide to how I set-up Freqtrader on Windows. There are many other ways to do so.*

1) Install Docker (this may ask you to update WSL too)
2) Open Docker
2) In Anaconda prompt:
    - cd to Git repo folder
    - `conda create -n freqtrade-env python=3.10` 
    - `conda activate freqtrade-env`
    - `conda install pandas matplotlib numpy jupyter`
    - `pip install freqtrade ccxt`
    - `conda env export > freqtrade-env.yml`
    - `pip freeze > requirements.txt`

3) [In terminal:](https://www.freqtrade.io/en/2020.11/docker_quickstart/)
    - `mkdir bots/ft_userdata`
    - `cd bots/ft_userdata/`
    - `curl https://raw.githubusercontent.com/freqtrade/freqtrade/stable/docker-compose.yml -o docker-compose.yml`
    - `docker-compose pull`
    - `docker-compose run --rm freqtrade create-userdir --userdir user_data`
    - `docker-compose run --rm freqtrade new-config --config user_data/config.json`
    - In `command:` section of "docker-compose.yml," need to switch to strategy you want to run via `--strategy <StrategyName>`
    - `docker-compose up -d`
4) Now view the UI at `localhost:8080`
5) Stop bot with `docker-compose down` in terminal


## Backteststing
0) In <freqtrade user>/<bot>/config.json
    - Be sure set to `"method": "StaticPairList", ` and pairs selected in the `pairs_whitelist`
1) In terminal:
    - `docker-compose up -d`
    - `docker exec -it freqtrade bash`
        - If this doesn't work, can double check name with `docker ps`
    - `freqtrade download-data`
        - To force refresh, may need to delete current files to overwrite them
    - `freqtrade backtesting --strategy <StrategyName> --timeframe <Xy> --timerange <YEARMoDa-YEARMoDa> --export=trades`
        - Note that timeframe and timerange are optional, both will revert to defaults
        - Export trades is to produce a csv as well

