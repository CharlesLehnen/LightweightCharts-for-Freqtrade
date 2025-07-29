from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class SimpleVisualRSI(IStrategy):
    """
    Easiest visualization strategy:
    Buy when RSI < 30, Sell when RSI > 70.
    No stoploss, no ROI, no trailing stop.
    """

    timeframe = '5m'
    stoploss = -0.99                # No stoploss
    minimal_roi = {}            # No ROI

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['rsi'] < 30),
            'enter_long'
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['rsi'] > 70),
            'exit_long'
        ] = 1
        return dataframe
