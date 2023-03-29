from datetime import datetime

import numpy as np
import pandas as pd
import MetaTrader5 as mt5

from start import start

pd.options.display.max_rows = None
pd.options.display.max_columns = None


# most updated fractal backtest

def ACDC_BT(starttime, endtime, stock_array, timeframe):
    # back test function  additionally lot size and deposit could be included to see if account blows
    Test_data = pd.DataFrame(columns=["Signal", "OTime", "Price", "TP", "SL", "CTime", "Pips"])
    start.log(25122527, "FBS-Real", "nlF74jTo")
    starttime = datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
    endtime = datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')
    TP = 500
    SL = -100
    hld = 1  # will be multiplied with point to get spead and access ask and bid price
    xt: int  # test x, ensures all symbols are looped through
    for xt in range(len(stock_array)):
        it = 3  # test it, ensures data set is looped through
        test_index = 0  # test index ensure Test_data of next buy or sell does not  over write previous data
        print(stock_array[xt])
        ohlc_data = mt5.copy_rates_range(stock_array[xt], timeframe, starttime, endtime)
        BARS_DATA = pd.DataFrame(ohlc_data)
        candle_decimal = mt5.symbol_info(stock_array[xt]).digits
        points = 10 ** (-candle_decimal)
        points1 = 10 ** candle_decimal  # points for dynamic stop loss using price high and lows, this will convert the pip movement to intergers
        high_low_diff = hld * points
        profit_v = TP * points  # ensures profit pips corresponds to desired TP for every symbol
        loss_v = (-SL) * points  # ensures loss pips corresponds to desired TP for every symbol
        BARS_DATA["time"] = pd.to_datetime(BARS_DATA["time"], unit='s')
        conditions_type = [BARS_DATA["open"] > BARS_DATA["close"], BARS_DATA["open"] < BARS_DATA["close"]]
        choices = ["Bear", "Bull"]
        BARS_DATA["candle"] = np.select(conditions_type, choices, default="Doji")
        BARS_DATA["size"] = BARS_DATA["high"] - BARS_DATA["low"]
        # print(BARS_DATA)
        while it < len(BARS_DATA) - 6:  # loop ends before the last 2 rows so buy or sell condition doesnt meet null
            if BARS_DATA.loc[it, "low"] < BARS_DATA.loc[it - 1, "low"] < BARS_DATA.loc[it - 2, "low"] \
                    and BARS_DATA.loc[it, "low"] < BARS_DATA.loc[it + 1, "low"] < \
                    BARS_DATA.loc[it + 2, "low"] and BARS_DATA.loc[it, "high"] < BARS_DATA.loc[it - 1, "high"] < \
                    BARS_DATA.loc[
                        it - 2, "high"] \
                    and BARS_DATA.loc[it, "high"] < BARS_DATA.loc[it + 1, "high"] < \
                    BARS_DATA.loc[it + 2, "high"]:  # last part this strategy can be modified
                buy_time = BARS_DATA.loc[
                    it + 3, "time"]  # Buy time will depend on condition to buy(could be a 1 or more candle condition)
                price = BARS_DATA.loc[it + 3, "open"] + high_low_diff  # better to get the ask price at that time of Buy
                profit = price + high_low_diff + profit_v
                # loss = price - loss_v
                loss = BARS_DATA.loc[it, "low"]
                SL = BARS_DATA.loc[it, "low"] - BARS_DATA.loc[it + 3, "open"]
                SL = SL * points1
                if SL * -1 > 200:
                    SL = -200
                # new data frame starting from buy_time above and ending normal end time
                test_data = mt5.copy_rates_range(stock_array[xt], mt5.TIMEFRAME_M1, buy_time,
                                                 endtime)  # you might have to change endtime to nox ensuring all orders close
                Tt_BARS = pd.DataFrame(test_data)
                # print(buy_time)
                Tt_BARS["time"] = pd.to_datetime(Tt_BARS["time"], unit='s')
                buy = True  # conditions were met for a buy
                buy_index = 0  # index used to loop through the "while buy:" to meet first candle satisfying TP or SL
                yt = 0
                # print("SIGNAL " + stock_array[xt])
                while buy:  # make sure len returns what is needed and you can use or here
                    if Tt_BARS.loc[buy_index, "high"] > profit:  # For  a good position
                        gain = TP + hld  # if next candle high is greater than target profit then objective has been reached update Test_data
                        buy = False  # Buy test is complete set false for next buy test
                        Test_data.loc[test_index, "Signal"] = "Buy"
                        Test_data.loc[test_index, "OTime"] = buy_time
                        Test_data.loc[test_index, "CTime"] = Tt_BARS.loc[buy_index, "time"]  # TP take time
                        Test_data.loc[test_index, "Price"] = price
                        Test_data.loc[test_index, "TP"] = profit
                        Test_data.loc[test_index, "SL"] = loss
                        Test_data.loc[test_index, "Pips"] = gain
                        test_index = test_index + 1
                    elif Tt_BARS.loc[buy_index, "low"] < loss:  # for a bad position
                        gain = SL  # Position caused a drop in gain
                        buy = False  # implying this buy test is done
                        Test_data.loc[test_index, "Signal"] = "Buy"
                        Test_data.loc[test_index, "OTime"] = buy_time
                        Test_data.loc[test_index, "CTime"] = Tt_BARS.loc[buy_index, "time"]  # Time the position closed
                        Test_data.loc[test_index, "Price"] = price
                        Test_data.loc[test_index, "TP"] = profit
                        Test_data.loc[test_index, "SL"] = loss
                        Test_data.loc[test_index, "Pips"] = gain
                        test_index = test_index + 1
                    elif buy_index + 1 == len(Tt_BARS):
                        gain = 0
                        Test_data.loc[test_index, "Signal"] = "Buy"
                        Test_data.loc[test_index, "OTime"] = buy_time
                        Test_data.loc[test_index, "CTime"] = Tt_BARS.loc[buy_index, "time"]  # Time the position closed
                        Test_data.loc[test_index, "Price"] = price
                        Test_data.loc[test_index, "TP"] = profit
                        Test_data.loc[test_index, "SL"] = loss
                        Test_data.loc[test_index, "Pips"] = gain  # if order is still ongoing till limit of Data
                        test_index = test_index + 1
                        buy = False
                    buy_index = buy_index + 1  # Next row in Tt_BARS which is a subset of BARS_DATA
                    yt = yt + 1  # if end reaches with no gain place gain is zero might no be needed here
            elif BARS_DATA.loc[it, 'high'] > BARS_DATA.loc[it - 1, 'high'] > BARS_DATA.loc[it - 2, 'high'] \
                    and BARS_DATA.loc[it, 'high'] > BARS_DATA.loc[it + 1, 'high'] > \
                    BARS_DATA.loc[it + 2, 'high'] and BARS_DATA.loc[it, 'low'] > BARS_DATA.loc[it - 1, 'low'] > \
                    BARS_DATA.loc[
                        it - 2, 'low'] \
                    and BARS_DATA.loc[it, 'low'] > BARS_DATA.loc[it + 1, 'low'] > \
                    BARS_DATA.loc[it + 2, 'low']:
                # last part this strategy can be modified
                sell_time = BARS_DATA.loc[it + 3, "time"]  # Time the sell occurred according to your condition
                price = BARS_DATA.loc[it + 3, "open"] - high_low_diff  # Approximation from spread
                profit = price - high_low_diff - profit_v  # take profit price with spread approximation
                # loss = price + loss_v  # stop loss price
                loss = BARS_DATA.loc[it, "high"]
                SL = BARS_DATA.loc[it + 3, "open"] - BARS_DATA.loc[it, "high"]
                SL = SL * points1
                if SL * -1 > 200:
                    SL = -200
                # new dataframe starting from sell_time
                test_data = mt5.copy_rates_range(stock_array[xt], mt5.TIMEFRAME_M1, sell_time, endtime)
                Tt_BARS = pd.DataFrame(test_data)
                Tt_BARS["time"] = pd.to_datetime(Tt_BARS["time"], unit='s')
                sell = True
                sell_index = 0  # loops through subset of data frame to find target profit or target loss
                yt = 0
                while sell:  # make sure len returns what is needed and you can use or here
                    if Tt_BARS.loc[sell_index, "low"] < profit:
                        gain = TP + hld
                        sell = False
                        Test_data.loc[test_index, "Signal"] = "Sell"
                        Test_data.loc[test_index, "OTime"] = sell_time
                        Test_data.loc[test_index, "CTime"] = Tt_BARS.loc[sell_index, "time"]  # TP time
                        Test_data.loc[test_index, "Price"] = price
                        Test_data.loc[test_index, "TP"] = profit
                        Test_data.loc[test_index, "SL"] = loss
                        Test_data.loc[test_index, "Pips"] = gain
                        test_index = test_index + 1
                    elif Tt_BARS.loc[sell_index, "high"] > loss:
                        gain = SL
                        sell = False
                        Test_data.loc[test_index, "Signal"] = "Sell"
                        Test_data.loc[test_index, "OTime"] = sell_time
                        Test_data.loc[test_index, "CTime"] = Tt_BARS.loc[sell_index, "time"]  # SL time
                        Test_data.loc[test_index, "Price"] = price
                        Test_data.loc[test_index, "TP"] = profit
                        Test_data.loc[test_index, "SL"] = loss
                        Test_data.loc[test_index, "Pips"] = gain
                        test_index = test_index + 1
                    elif sell_index + 1 == len(Tt_BARS):
                        gain = 0
                        Test_data.loc[test_index, "Signal"] = "Sell"
                        Test_data.loc[test_index, "OTime"] = sell_time
                        Test_data.loc[test_index, "CTime"] = Tt_BARS.loc[sell_index, "time"]  # SL time
                        Test_data.loc[test_index, "Price"] = price
                        Test_data.loc[test_index, "TP"] = profit
                        Test_data.loc[test_index, "SL"] = loss
                        Test_data.loc[test_index, "Pips"] = gain  # if order is still ongoing
                        test_index = test_index + 1
                        sell = False
                    sell_index = sell_index + 1
                    yt = yt + 1  # if end reaches with no gain place gain is zero might no be needed here
            it = it + 1
        print(Test_data["Pips"].sum(), len(Test_data))
        #print(Test_data)
        print(
            f"{'For:'} {stock_array[xt]} {' from:'} {starttime} {' to'} {endtime} {' Profit'} {Test_data['Pips'].sum()} {' TP/SL ratio'} {TP} {SL} {hld} ")


str_list = ["EURUSD", "USDCAD", "GBPUSD", "USDJPY", "AUDJPY",
            "USDCHF", "AUDUSD", "GBPAUD",
            "AUDCAD", "AUDCHF", "CADCHF", "CHFJPY", "EURCAD",
            "EURJPY", "EURNZD", "EURAUD", "CADJPY", "GBPCAD"]
ACDC_BT("2023-03-07 00:00:00", "2023-03-14 00:00:00", str_list, mt5.TIMEFRAME_H1)
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
