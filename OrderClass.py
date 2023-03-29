import MetaTrader5 as mt5
import VARS


class Order:
    def __init__(self, currency, lot, ordertype, deviation, magic, stl, tkp, price):
        self.tick = mt5.symbol_info_tick(VARS.symbol)
        self.currency = currency
        self.lot = lot
        self.ordertype = ordertype
        self.stl = stl
        self.tkp = tkp
        self.deviation = deviation
        self.magic = magic
        self.price = price

    def func_order(self):
        currency = self.currency
        ordertype = self.ordertype
        lot = self.lot
        stl = self.stl
        tkp = self.tkp
        deviation = self.deviation
        magic = self.magic
        price = self.price
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": currency,
            "volume": lot,
            "type": ordertype,
            "price": price,
            "sl": stl,
            "tp": tkp,
            "deviation": deviation,
            "magic": magic,  # unique order identifier
            "connect": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,  # validity of order
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        order = mt5.order_send(request)
        print(order)
        position = order.deal
        if order.deal != 0:
            print("Order:", order.deal, " has been place")
        else:
            print("An error occurred")
            print(mt5.last_error())
        return position


class Cl_Order:
    def __init__(self, currency, lot, ordertype, mag, pos):
        self.tick = mt5.symbol_info_tick(VARS.symbol)
        self.pos = pos
        tick = self.tick
        self.currency = currency
        self.lot = lot
        self.ordertype = ordertype
        self.magic = mag
        self.order_dic = {"buy": 0, "sell": 1}
        self.price_dic = {"buy": tick.ask, "sell": tick.bid}

    def cl_order(self, currency, lot, ordertype, mag, pos):
        tick = mt5.symbol_info_tick(currency)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": currency,
            "volume": lot,  # lot size of position in question
            "type": self.order_dic[ordertype],  # opposite of position in question
            "position": pos,
            "price": tick.ask if ordertype == "buy" else tick.bid,
            "magic": mag,
            "type_time": mt5.ORDER_TIME_GTC,  # validity of order
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        order = mt5.order_send(request)
        print(order)
        if order.deal != 0:
            print("Order has been ", order.deal, "closed")

        else:
            print("Order:", order.deal, " couldn't be closed")
            print(mt5.last_error())
        return order.deal


def limit_order(volume, ordertype, currency, mag, price, stl, tkp, ):
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": currency,
        "volume": volume,
        "type": ordertype,
        "price": price,
        "sl": stl,
        "tp": tkp,
        "deviation": 20,
        "magic": mag,  # unique order identifier
        "connect": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,  # validity of order
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    order = mt5.order_send(request)
    return order.deal


