# Lightweight-Charts for Freqtrade Guide

&nbsp;&nbsp;&nbsp;[Freqtrade](https://github.com/freqtrade/freqtrade) is an open-source cryptocurrency bot managment system, complete with capabilities for backtesting and deployment. 

&nbsp;&nbsp;&nbsp;[TradingView](https://www.tradingview.com/pricing/?share_your_love=talker91) is a powerful commercial charting platform that is widely used in the trading community. They provide [Lightweight-Charts](https://www.tradingview.com/lightweight-charts/), an open-source Javascript based library based on for creating financial charts in web applications.

&nbsp;&nbsp;&nbsp;Compared to TradingView/Lightweight-Charts, Freqtrade's built-in plotting capabilities are limited. These [Plotly](https://plotly.com/) based charts do not providethe same level of interactivity or visual appeal.

&nbsp;&nbsp;&nbsp;I was inspired by the [Lightweight-Charts-Python](https://github.com/louisnw01/lightweight-charts-python) library and [this PartTimeLarry video](https://www.youtube.com/watch?v=TlhDI3PforA) to create a solution that allows Freqtrade users to visualize their trading strategies using Lightweight-Charts. This requires a Javascript script to be run inside of the Freqtrade Docker container. 

The result is an interactive chart that look like this:

![RSI example plot](images/RSI_example.gif?raw=true)


&nbsp;&nbsp;&nbsp;If this is your first time setting up Freqtrade, see the [Initialization section](#initialization) below and refer to the [Freqtrade Quickstart Guide](https://www.freqtrade.io/en/latest/quickstart/).

&nbsp;&nbsp;&nbsp;If Freqtrade is already set up, you can skip to the [Lightweight-Charts Plotting section](#lightweight-charts-plotting) section.

### Quick Start

1) Run [`code/main.py`](code/main.py) and follow prompts

2) Open [`code/lightweight-charts.html`](code/lightweight-charts.html) in browser. Personally, I use LiveServer VSCode extension. Use the file pickers to select the newly generated files in:
    - `bots/<bot>/user_data/data/<exchange>/<Pair_Timeframe.csv>`
    - `bots/<bot>/user_data/data/indicator_data_<StrategyName>.csv`
    - `bots/<bot>/user_data/<exchange>/backtest_results/<desired_backtest_results>/<desired_backtest_results.json>`



---


## Initialization
*This is a guide to how I set-up Freqtrader on Windows. There are many other ways to do so.*

1) Install Docker Desktop (this may require you to update WSL too)
2) Open Docker Desktop
2) In Anaconda prompt:
    - cd to Git repo folder
    - `conda create -n <env name> python=3.10` 
    - `conda activate <env name>`
    - `conda install pandas matplotlib numpy jupyter pyarrow`
    - `pip install freqtrade ccxt`

3) [In terminal:](https://www.freqtrade.io/en/2020.11/docker_quickstart/)
    - `mkdir bots/<bot>`
    - `cd bots/<bot>`
    - `curl https://raw.githubusercontent.com/freqtrade/freqtrade/stable/docker-compose.yml -o docker-compose.yml`
    - `docker-compose pull`
    - `docker-compose run --rm freqtrade create-userdir --userdir user_data`
    - `docker-compose run --rm freqtrade new-config --config user_data/config.json`
    - In `command:` section of "docker-compose.yml," need to switch to strategy you want to run via `--strategy <StrategyName>`

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

