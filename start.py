import MetaTrader5 as mt5


class start:

    @staticmethod
    def log(log, ser, passw):
        if not mt5.initialize(login=log, server=ser, password=passw):
            print("initialize() failed")
            mt5.shutdown()
        else:
            print("connected")
