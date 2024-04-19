from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np
import jsonpickle
import pandas as pd

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class Trader:
    POSITION_LIMIT = {'AMETHYSTS': 20, 'STARFRUIT': 20}

    def values_extract(self, order_dict, buy=0):
        tot_vol = 0
        best_val = -1
        mxvol = -1

        for ask, vol in order_dict.items():
            if (buy == 0):
                vol *= -1
            tot_vol += vol
            if tot_vol > mxvol:
                mxvol = vol
                best_val = ask

        return tot_vol, best_val

    def list_to_dict(self, my_list):
        my_dict = {}
        for key, value in my_list:
            my_dict[key] = value
        return my_dict

    def compute_amethysts_orders(self, state, product, acc_bid, acc_ask):
        position = state.position.get("AMETHYSTS", 0)
        orders: list[Order] = []
        order_depth: OrderDepth = state.order_depths[product]

        osell = self.list_to_dict(sorted(order_depth.sell_orders.items()))
        obuy = self.list_to_dict(
            sorted(order_depth.buy_orders.items(), reverse=True))
        sell_vol, best_sell_pr = self.values_extract(osell)
        buy_vol, best_buy_pr = self.values_extract(obuy, 1)
        cpos = position
        mx_with_buy = -1

        if position > 20 or position < -20:
            print("BUST")

        for ask, vol in osell.items():
            if ((ask < acc_bid) or ((position < 0) and (ask == acc_bid))) and cpos < self.POSITION_LIMIT['AMETHYSTS']:
                mx_with_buy = max(mx_with_buy, ask)
                order_for = min(-vol, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
                cpos += order_for
                # assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))

        mprice_actual = (best_sell_pr + best_buy_pr)/2
        mprice_ours = (acc_bid+acc_ask)/2

        undercut_buy = best_buy_pr + 1
        undercut_sell = best_sell_pr - 1

        # we will shift this by 1 to beat this price
        bid_pr = min(undercut_buy, acc_bid-1)
        sell_pr = max(undercut_sell, acc_ask+1)

        if (cpos < self.POSITION_LIMIT['AMETHYSTS']) and (state.position.get(product, 0) < 0):
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(
                Order(product, min(undercut_buy + 1, acc_bid-1), num))
            cpos += num

        if (cpos < self.POSITION_LIMIT['AMETHYSTS']) and (state.position.get(product, 0) > 15):
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(
                Order(product, min(undercut_buy - 1, acc_bid-1), num))
            cpos += num

        if cpos < self.POSITION_LIMIT['AMETHYSTS']:
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(Order(product, bid_pr, num))
            cpos += num

        cpos = state.position.get(product, 0)

        for bid, vol in obuy.items():
            if ((bid > acc_ask) or ((position > 0) and (bid == acc_ask))) and cpos > -self.POSITION_LIMIT['AMETHYSTS']:
                order_for = max(-vol, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
                # order_for is a negative number denoting how much we will sell
                cpos += order_for
                # assert(order_for <= 0)
                orders.append(Order(product, bid, order_for))

        if (cpos > -self.POSITION_LIMIT['AMETHYSTS']) and (state.position.get(product, 0) > 0):
            num = max(-40, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
            orders.append(Order(product, max(undercut_sell-1, acc_ask+1), num))
            cpos += num

        if (cpos > -self.POSITION_LIMIT['AMETHYSTS']) and (state.position.get(product, 0) < -15):
            num = max(-40, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
            orders.append(Order(product, max(undercut_sell+1, acc_ask+1), num))
            cpos += num

        if cpos > -self.POSITION_LIMIT['AMETHYSTS']:
            num = max(-40, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
            orders.append(Order(product, sell_pr, num))
            cpos += num
            # print('yo')

        return orders, cpos

    def compute_starfruit_orders(self, state, product, acc_bid, acc_ask, current_starfruit_position):
        position_limit = 20
        order_depth: OrderDepth = state.order_depths[product]
        orders: List[Order] = []
        if state.timestamp > 5:
            last_5_prices = list(order_depth.sell_orders.items())[:5]
            past_prices = [float(price) for price, _ in last_5_prices]
            average_price = sum(past_prices) / len(past_prices)
            # print("The average price is ", average_price)
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            best_ask, best_ask_amount = list(
                order_depth.sell_orders.items())[0]
            if best_bid < average_price - 2:
                if current_starfruit_position + best_bid_amount <= position_limit:
                    print("BUYING STARFRUIT")
                    orders.append(Order(product, best_bid, -best_bid_amount))
                    current_starfruit_position += best_bid_amount
            if best_ask > average_price + 2:
                if current_starfruit_position - best_ask_amount >= -position_limit:
                    print("SELLING STARFRUIT")
                    orders.append(Order(product, best_ask, -best_ask_amount))
                    current_starfruit_position -= best_ask_amount
        return orders, current_starfruit_position

    # def compute_orchid_orders(self, state, product, current_orchid_position):
    #     position_limit = 100
    #     order_depth: OrderDepth = state.order_depths[product]
    #     orders: List[Order] = []

    #     conversion_observation = state.observations.conversionObservations.get(product, 0)
    #     plain_value_observation = state.observations.plainValueObservations.get(product, 0)
    #     amethysts = state.observations.plainValueObservations.get("AMETHYSTS", 0)

    #     if state.timestamp % 10000 == 0:
    #         print(str(conversion_observation.bidPrice) + ' | ')
    #         print(str(plain_value_observation) + ' | ')
    #         print(str(amethysts.bidPrice) + ' | ')
    #         print("===============================")

    def get_recordProduct(self, state, product):
        order_depth_p = state.order_depths[product]
        # state.traderData.get(f"{product}_history", None)

        best_sell = min(order_depth_p.sell_orders.keys())
        best_buy = max(order_depth_p.buy_orders.keys())

        mid_price = (best_sell + best_buy)/2

        new_row = pd.DataFrame(
            {'timestamp': [state.timestamp], 'mid_price': [mid_price]}).set_index('timestamp')

        data = state.traderData.get(f"{product}_history", None)

        if data != None:
            data = pd.DataFrame(pd.read_json(
                data).set_index("timestamp")).tail(self.save_length)
            if state.timestamp in list(data.index):
                return data
            data = pd.concat([data, new_row])
        else:
            data = new_row

        state.traderData[f"{product}_history"] = data.reset_index().to_json()
        return data

    def gift_basket(self, state, gift, choc, berries, roses):
        items = ("GIFT_BASKET", "CHOCOLATE", "STRAWBERRIES", "ROSES")

        window1, window2 = self.windows
        orders: List[Order] = []

        order_depths: List[OrderDepth] = []
        for item in items:
            order_depths.append(state.order_depths[item])

        gift, summed = gift, choc*6 + roses*3 + berries

        if len(gift) < window1 or len(summed) < window1:
            print(len(gift), len(summed), "not enough data yet")
            return orders

        best_bid_gift, best_bid_amount_gift = list(
            order_depths[0].buy_orders.items())[0]
        best_ask_gift, best_ask_amount_gift = list(
            order_depths[0].sell_orders.items())[0]

        gift = gift.groupby('timestamp').agg("mean")
        summed = summed.groupby('timestamp').agg("mean")

        ratios = gift/summed
        ma1 = ratios.rolling(window=window1, center=False).mean()
        ma2 = ratios.rolling(window=window2, center=False).mean()
        std = ratios.rolling(window=window2, center=False).std()
        zscore = (ma1 - ma2)/std

        if zscore.iloc[-1].item() < -1:

            orders.append(
                Order(items[0], best_bid_gift, max(-10, -best_bid_amount_gift)))

        # Buy long if the z-score is < -1
        elif zscore.iloc[-1].item() > 1:
            orders.append(
                Order(items[0], best_ask_gift, min(10, -best_ask_amount_gift)))

        # Clear positions if the z-score between -.5 and .5
        elif abs(zscore.iloc[-1].item()) < 0.5:
            p1_pos = state.position.get(items[0], 0)

            for prod, pos, ask_bid in [(items[0], p1_pos, (best_ask_gift, best_bid_gift))]:
                if (pos < 0):
                    orders.append(Order(prod, ask_bid[0], -pos))
                elif (pos > 0):
                    orders.append(Order(prod, ask_bid[1], -pos))

        print(orders)
        return orders

    def run(self, state: TradingState):
        # Params
        self.save_length = 70
        self.windows = (60, 3)
        self.pair_freq = 5  # once every

        if state.traderData == "":
            state.traderData = {}
        elif type(state.traderData) == str:
            state.traderData = jsonpickle.decode(state.traderData)

        result = {}

        current_amethysts_position = state.position.get('AMETHYSTS', 0)
        current_starfruit_position = state.position.get('STARFRUIT', 0)

        current_orchid_position = state.position.get('STRAWBERRIES', 0)
        current_orchid_position = state.position.get('CHOCOLATE', 0)
        current_orchid_position = state.position.get('ROSES', 0)
        current_orchid_position = state.position.get('GIFT_BASKET', 0)

        orders: list[Order] = []
        # we want to buy at slightly below
        acc_bid = {'AMETHYSTS': 10000, 'STARFRUIT': 5000}
        # we want to sell at slightly above
        acc_ask = {'AMETHYSTS': 10000, 'STARFRUIT': 5000}

        items = ("GIFT_BASKET", "CHOCOLATE", "STRAWBERRIES", "ROSES")
        for product in state.order_depths:
            if product == "AMETHYSTS" and False:
                orders, current_amethysts_position = self.compute_amethysts_orders(
                    state, product, acc_bid[product], acc_ask[product])
                result[product] = orders

            if product == "STARFRUIT" and False:
                orders, current_starfruit_position = self.compute_starfruit_orders(
                    state, product, acc_bid[product], acc_ask[product], current_starfruit_position)
                result[product] = orders

            # if product == "ORCHIDS" and False:
            #     self.compute_orchid_orders(
            #         state, product, current_orchid_position)
            #     result[product] = orders

            if (product in items) and (state.timestamp % (100*self.pair_freq) == 0):

                dfs = []
                for item in items:
                    dfs.append(self.get_recordProduct(state, item))

                orders = self.gift_basket(state, *dfs)

                for order in orders:
                    result[order.symbol] = [order]
                # result[product] = orders

        conversions = 1

        traderData = jsonpickle.encode(state.traderData)
        return result, conversions, traderData
