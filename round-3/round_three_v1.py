from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np
import jsonpickle
import pandas as pd


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
            print('yo')

        return orders, cpos

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
            data = pd.DataFrame(pd.read_json(data).set_index("timestamp"))
            if state.timestamp in list(data.index):
                return data
            data = pd.concat([data, new_row])
        else:
            data = new_row

        state.traderData[f"{product}_history"] = \
            data.reset_index().to_json()

        return data

    def pairwise(self, state, product1, product2):
        window1, window2 = (200, 2)

        order_depth_p1: OrderDepth = state.order_depths[product1]
        order_depth_p2: OrderDepth = state.order_depths[product2]

        prices_1 = self.get_recordProduct(state, product1)
        prices_2 = self.get_recordProduct(state, product2)

        # if prices_1 == None or prices_2 == None:
        #     return

        if len(prices_1) < window1 or len(prices_2) < window1:
            return

        best_bid_p1, best_bid_amount_p1 = list(
            order_depth_p1.buy_orders.items())[0]
        best_ask_p1, best_ask_amount_p1 = list(
            order_depth_p1.sell_orders.items())[0]

        best_bid_p2, best_bid_amount_p2 = list(
            order_depth_p2.buy_orders.items())[0]
        best_ask_p2, best_ask_amount_p2 = list(
            order_depth_p2.sell_orders.items())[0]

        S1 = prices_1.groupby('timestamp').agg("mean")
        S2 = prices_2.groupby('timestamp').agg("mean")

        ratios = S1/S2
        ma1 = ratios.rolling(window=window1, center=False).mean()
        ma2 = ratios.rolling(window=window2, center=False).mean()
        std = ratios.rolling(window=window2, center=False).std()
        zscore = (ma1 - ma2)/std

        orders: List[Order] = []

        # Sell short if the z-score is > 1
        if zscore.iloc[-1].item() < -1:
            # buy p2 and sell p1
            orders.append(Order(product2, best_ask_p2, -best_ask_amount_p2))
            orders.append(Order(product1, best_bid_p1, -best_bid_amount_p1))

            # money += S1.iloc[-1].item() - S2.iloc[-1].item() * ratios.iloc[-1].item()
            # countS1 -= 1
            # countS2 += ratios.iloc[i].item()

        # Buy long if the z-score is < -1
        elif zscore.iloc[-1].item() > 1:
            orders.append(Order(product1, best_ask_p1, -best_ask_amount_p1))
            orders.append(Order(product2, best_bid_p2, -best_bid_amount_p2))

            # money -= S1.iloc[-1].item() - S2.iloc[-1].item() * \
            #     ratios.iloc[-1].item()
            # countS1 += 1
            # countS2 -= ratios.iloc[-1].item()
            # print('Buying Ratio %s %s %s %s'%(money,ratios.iloc[-1].item(), countS1,countS2))

        # Clear positions if the z-score between -.5 and .5
        elif abs(zscore.iloc[-1].item()) < 0.75:
            p1_pos = state.position.get(product1, 0)
            p2_pos = state.position.get(product2, 0)

            for prod, pos, ask_bid in [(product1, p1_pos, (best_ask_p1, best_bid_p1)), (product2, p2_pos, (best_ask_p2, best_bid_p2))]:
                if (pos < 0):
                    orders.append(Order(prod, ask_bid[0], -pos))
                elif (pos > 0):
                    orders.append(Order(prod, ask_bid[1], -pos))

            # money += S1.iloc[-1].item() * countS1 + \
            #     S2.iloc[-1].item() * countS2
            # countS1 = 0
            # countS2 = 0

        print(orders)
        return orders

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

    def compute_orchid_orders(self, state, product, current_orchid_position):
        position_limit = 100
        order_depth: OrderDepth = state.order_depths[product]
        orders: List[Order] = []

        conversion_observation = state.observations.conversionObservations.get(
            product, 0)
        plain_value_observation = state.observations.plainValueObservations.get(
            product, 0)
        amethysts = state.observations.plainValueObservations.get(
            "AMETHYSTS", 0)

        if state.timestamp % 10000 == 0:
            print(str(conversion_observation.bidPrice) + ' | ')
            print(str(plain_value_observation) + ' | ')
            print(str(amethysts.bidPrice) + ' | ')
            print("===============================")

    def run(self, state: TradingState):
        # a = str(state.traderData)
        # assert False, a

        print("Current Trader Data: ", state.traderData)
        print(f"\n\n {type(state.traderData)}\n\n")

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

        for product in state.order_depths:
            if product == "AMETHYSTS" and False:
                orders, current_amethysts_position = self.compute_amethysts_orders(
                    state, product, acc_bid[product], acc_ask[product])
                result[product] = orders

            if product == "STARFRUIT" and False:
                orders, current_starfruit_position = self.compute_starfruit_orders(
                    state, product, acc_bid[product], acc_ask[product], current_starfruit_position)
                result[product] = orders

            if product == "ORCHIDS" and False:
                self.compute_orchid_orders(
                    state, product, current_orchid_position)
                result[product] = orders

            if product == "GIFT_BASKET" or product == "CHOCOLATE":
                orders = self.pairwise(state, "GIFT_BASKET", "CHOCOLATE")

        conversions = 1

        traderData = state.traderData
        return result, conversions, traderData
