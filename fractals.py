import winsound
from time import sleep

import numpy as np
import pandas as pd
import MetaTrader5 as mt5

import OrderClass
from start import start

pd.options.display.max_rows = None
pd.options.display.max_columns = None


def ACDC_BT(stock_array, timeframe):
    # back test function  additionally lot size and deposit could be included to see if account blows
    # start.log(5005468062, "MetaQuotes-Demo", "1tlbstiz")
    # start.log(5005468062, "MetaQuotes-Demo", "1tlbstiz")
    a = True
    sleep_bool = False
    while a:
        start.log(25122527, "FBS-Real", "nlF74jTo")
        if sleep_bool:
            sleep(3600)
            sleep_bool = False
        TP = 500
        hld = 1  # will be multiplied with point to get spead and access ask and bid price
        xt: int  # test x, ensures all symbols are looped through
        for xt in range(len(stock_array)):
            it = 0  # ensures values for each stock
            print(stock_array[xt])
            ohlc_data = mt5.copy_rates_from_pos(stock_array[xt], timeframe, 0, 6)
            BARS_DATA = pd.DataFrame(ohlc_data)
            candle_decimal = mt5.symbol_info(stock_array[xt]).digits
            candle = mt5.symbol_info_tick(str_list[xt])
            points = 10 ** (-candle_decimal)
            points1 = 10 ** candle_decimal  # points for dynamic stop loss using price high and lows, this will convert the pip movement to intergers
            high_low_diff = hld * points
            profit_v = TP * points  # ensures profit pips corresponds to desired TP for every symbol
            BARS_DATA["time"] = pd.to_datetime(BARS_DATA["time"], unit='s')
            conditions_type = [BARS_DATA["open"] > BARS_DATA["close"], BARS_DATA["open"] < BARS_DATA["close"]]
            choices = ["Bear", "Bull"]
            BARS_DATA["candle"] = np.select(conditions_type, choices, default="Doji")
            BARS_DATA["size"] = BARS_DATA["high"] - BARS_DATA["low"]
            # print(stock_array[xt])
            # print(BARS_DATA)
            while it < len(BARS_DATA):  # loop ends before the last 2 rows so buy or sell condition doesnt meet null
                if BARS_DATA.loc[2, "low"] < BARS_DATA.loc[1, "low"] < BARS_DATA.loc[0, "low"] \
                        and BARS_DATA.loc[2, "low"] < BARS_DATA.loc[3, "low"] < \
                        BARS_DATA.loc[4, "low"] and BARS_DATA.loc[2, "high"] < BARS_DATA.loc[1, "high"] < \
                        BARS_DATA.loc[
                            0, "high"] \
                        and BARS_DATA.loc[2, "high"] < BARS_DATA.loc[3, "high"] < \
                        BARS_DATA.loc[4, "high"]:  # last part this strategy can be modified
                    buy_time = BARS_DATA.loc[5, "time"]
                    # Buy time will depend on condition to buy(could be a 1 or more candle condition)
                    price = BARS_DATA.loc[5, "open"] + high_low_diff  # better to get the ask price at that time of Buy
                    profit = candle.ask + profit_v
                    loss = BARS_DATA.loc[2, "low"]
                    SL = BARS_DATA.loc[2, "low"] - BARS_DATA.loc[5, "open"]
                    SL = SL * points1
                    if SL * -1 > 200:
                        loss = candle.ask - 200 * points
                    order_obj = OrderClass.Order(stock_array[xt], 0.09, mt5.ORDER_TYPE_BUY, 20, 10, loss, profit,
                                                 candle.ask)
                    pos = order_obj.func_order()
                    if pos != 0:
                        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                        print(
                            f"{'STOCK:'} {stock_array[xt]} {' Order:Sell '} {buy_time} {'TakeProfit:'} {profit} {' StopLoss:'} {loss} {' Price:'} {price}")
                        sleep_bool = True
                elif BARS_DATA.loc[2, 'high'] > BARS_DATA.loc[1, 'high'] > BARS_DATA.loc[0, 'high'] \
                        and BARS_DATA.loc[2, 'high'] > BARS_DATA.loc[3, 'high'] > \
                        BARS_DATA.loc[4, 'high'] and BARS_DATA.loc[2, 'low'] > BARS_DATA.loc[1, 'low'] > \
                        BARS_DATA.loc[
                            0, 'low'] \
                        and BARS_DATA.loc[2, 'low'] > BARS_DATA.loc[3, 'low'] > \
                        BARS_DATA.loc[4, 'low']:
                    print("Sell Signal")
                    sell_time = BARS_DATA.loc[5, "time"]  # Time the sell occurred according to your condition
                    price = BARS_DATA.loc[5, "open"] - high_low_diff  # Approximated price of execution from spread
                    profit = candle.bid - profit_v  # take profit price with spread approximation
                    loss = BARS_DATA.loc[2, "high"]
                    SL = BARS_DATA.loc[5, "open"] - BARS_DATA.loc[it, "high"]  # calculations of pips to be lost
                    SL = SL * points1  # calculation of pips to be loss
                    if SL * -1 > 200:
                        loss = candle.bid + 200 * points
                    order_obj = OrderClass.Order(stock_array[xt], 0.09, mt5.ORDER_TYPE_SELL, 20, 10, loss, profit,
                                                 candle.bid)
                    pos = order_obj.func_order()
                    if pos != 0:
                        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                        print(
                            f"{'STOCK:'} {stock_array[xt]} {' Order:Sell '} {sell_time} {'TakeProfit:'} {profit} {' StopLoss:'} {loss} {' Price:'} {price}")
                        sleep_bool = True

                it = len(BARS_DATA)


str_list = ["EURUSD", "USDCAD", "GBPUSD", "USDJPY", "AUDJPY",
            "USDCHF", "AUDUSD", "GBPAUD",
            "AUDCAD", "AUDCHF", "CADCHF", "CHFJPY", "EURCAD",
            "EURJPY", "EURNZD", "EURAUD", "CADJPY", "GBPCAD"]

ACDC_BT(str_list, mt5.TIMEFRAME_H1)
# Back testing this strategy this strategy for ["EURUSD", "USDCAD", "GBPUSD", "USDJPY"] gave me a net huge profit for 2020 in H1 frame
# Net lost for the month of march 2020 due to GBPUSD[4044] the rest far lower gain than usual
# GBPUSD and EURUSD lost for the 4th month but still had a net gain
# GBPUSD lost in the 5th month but there was still a net large profit
# EURUSD lost for the 7th month still had a net gain
# USDCAD lost on the 11 but still a huge net gain
# Very small lost GBPUSD for december still a huge net gain
# After filtering out worst fractals adjust profit loss ratio to be the best that is lowest lost
# think about restricting v shape of fractals just to high or lows not both
# ACDC_BT("2023-02-01 00:00:00", "2023-03-03 00:00:00", str_list, mt5.TIMEFRAME_H1)
# closing position with loss of 500 if dynamic stop loss might result to greater than 500 looks better
# You will need to intensely back test for the different tweaks and try to get the highest loss streak and best profit 
# if price minus peak is greater than 500pip close trade at 500 pip


# For buy use the ask price as specified by metatrader 5
# Rather create a bool for sleep make since all present pairs open and close and similar times, sleep only after the last pair
# Pair in the array has been checked to avoid missing a position due to sleep-----------
