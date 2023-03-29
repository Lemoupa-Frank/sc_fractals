import datetime

import MetaTrader5 as mt5

Difference = 0
symbol = "EURUSD"
# EURUSD USDCHF EURCAD  EURJPY GBPUSD AUDUSD USDJPY AMAZON
TIMEFRAME = mt5.TIMEFRAME_M5
Tradevolume = 0.01
BB_Deviation = 0
BB_SMA_PERIOD = 20
STANDARD_DEV_BB = 2
surplus = 0.050
if symbol == "EURUSD":
    Difference = 0.00022
if symbol == "USDCHF":
    Difference = 0.00022
if symbol == "EURCAD":
    Difference = 0.00022
if symbol == "EURJPY":
    Difference = 0.001
if symbol == "GBPUSD":
    Difference = 0.00022
if symbol == "AUDUSD":
    Difference = 0.00022
if symbol == "USDJPY":
    Difference = 0.022
if symbol == "AMAZON":
    Difference = 0.022
if symbol == "EURUSD":
    surplus = 0.00120
if symbol == "USDCHF":
    surplus = 0.000120
if symbol == "EURCAD":
    surplus = 0.00120
if symbol == "EURJPY":
    surplus = 0.0120
if symbol == "GBPUSD":
    surplus = 0.00120
if symbol == "AUDUSD":
    surplus = 0.00050
if symbol == "USDJPY":
    surplus = 0.0120
if symbol == "AMAZON":
    surplus = 0.050

Previous_Date_Day = datetime.datetime.today() - datetime.timedelta(days=20)

