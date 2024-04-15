from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np


class Trader:
    POSITION_LIMIT = {'AMETHYSTS': 20, 'STARFRUIT': 20}
    
    def values_extract(self, order_dict, buy=0):
        tot_vol = 0
        best_val = -1
        mxvol = -1

        for ask, vol in order_dict.items():
            if(buy==0):
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
        obuy = self.list_to_dict(sorted(order_depth.buy_orders.items(), reverse=True))
        print(osell)
        sell_vol, best_sell_pr = self.values_extract(osell)
        buy_vol, best_buy_pr = self.values_extract(obuy, 1)
        cpos = position
        mx_with_buy = -1

        if position > 20 or position < -20:
            print("BUST")
            
        
        for ask, vol in osell.items():
            if ((ask < acc_bid) or ((position<0) and (ask == acc_bid))) and cpos < self.POSITION_LIMIT['AMETHYSTS']:
                mx_with_buy = max(mx_with_buy, ask)
                order_for = min(-vol, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
                cpos += order_for
                # assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))
        
        mprice_actual = (best_sell_pr + best_buy_pr)/2
        mprice_ours = (acc_bid+acc_ask)/2

        undercut_buy = best_buy_pr + 1
        undercut_sell = best_sell_pr - 1

        bid_pr = min(undercut_buy, acc_bid-1) # we will shift this by 1 to beat this price
        sell_pr = max(undercut_sell, acc_ask+1)

        if (cpos < self.POSITION_LIMIT['AMETHYSTS']) and (state.position.get(product, 0) < 0):
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(Order(product, min(undercut_buy + 1, acc_bid-1), num))
            cpos += num

        if (cpos < self.POSITION_LIMIT['AMETHYSTS']) and (state.position.get(product, 0) > 15):
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(Order(product, min(undercut_buy - 1, acc_bid-1), num))
            cpos += num

        if cpos < self.POSITION_LIMIT['AMETHYSTS']:
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(Order(product, bid_pr, num))
            cpos += num
        
        cpos = state.position.get(product, 0)
        
        for bid, vol in obuy.items():
            if ((bid > acc_ask) or ((position>0) and (bid == acc_ask))) and cpos > -self.POSITION_LIMIT['AMETHYSTS']:
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
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
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

        conversion_observation = state.observations.conversionObservations.get(product, 0)
        print(conversion_observation.sunlight)
        print(conversion_observation.humidity)
        print(conversion_observation.importTariff)
        if conversion_observation:
            if conversion_observation.sunlight > 4000 and conversion_observation.humidity > 88.5:
                print("sell sell sell")
                current_orchid_position += sell_orchid(order_depth, current_orchid_position, position_limit, product, orders)

            if conversion_observation.sunlight < 2000 and conversion_observation.humidity < 70 and conversion_observation.importTariff > -2.6:
                print("BUususus")
                current_orchid_position -= buy_orchid(order_depth, current_orchid_position, position_limit, product, orders)

            if conversion_observation.humidity > 95:
                print("SELL")
                current_orchid_position += sell_orchid(order_depth, current_orchid_position, position_limit, product, orders)

            if conversion_observation.sunlight > 4350:  # change this to 4350 upon submission
                print("SELLEEEEE")
                current_orchid_position += sell_orchid(order_depth, current_orchid_position, position_limit, product, orders)
        return orders, current_orchid_position



    def buy_orchid(order_depth, current_orchid_position, position_limit, product, orders):
        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            if current_orchid_position - best_ask_amount <= position_limit:
                orders.append(Order(product, best_ask, -best_ask_amount))
                return best_ask_amount
            elif position_limit - current_orchid_position <= abs(best_ask_amount):
                best_ask_amount = -1 * (position_limit - current_orchid_position)
                orders.append(Order(product, best_ask, -best_ask_amount))
                return best_ask_amount
        return 0  # Return 0 if there are no orders to execute


    def sell_orchid(order_depth, current_orchid_position, position_limit, product, orders):
        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if current_orchid_position - best_bid_amount >= (-1 * position_limit):
                orders.append(Order(product, best_bid, -best_bid_amount))
                return best_bid_amount
            elif abs(position_limit - current_orchid_position) <= abs(best_bid_amount):
                best_bid_amount = -1 * abs(position_limit - current_orchid_position)
                orders.append(Order(product, best_bid, -best_bid_amount))
                return -1 * (best_bid_amount)
        return 0  # Return 0 if there are no orders to execute


        
    def run(self, state: TradingState):
        result = {}
        current_amethysts_position = state.position.get('AMETHYSTS', 0)
        current_starfruit_position = state.position.get('STARFRUIT', 0)
        current_orchid_position = state.position.get('ORCHIDS', 0)
        orders: list[Order] = []
        acc_bid = {'AMETHYSTS' : 10000, 'STARFRUIT' : 5000} # we want to buy at slightly below
        acc_ask = {'AMETHYSTS' : 10000, 'STARFRUIT' : 5000} # we want to sell at slightly above
        
        for product in state.order_depths:
            if product == "AMETHYSTS":
                orders, current_amethysts_position = self.compute_amethysts_orders(state, product, acc_bid[product], acc_ask[product])
                result[product] = orders
            
            if product == "STARFRUIT":
                orders, current_starfruit_position = self.compute_starfruit_orders(state, product, acc_bid[product], acc_ask[product], current_starfruit_position)
                result[product] = orders
            
            if product == "ORCHIDS":
                orders, current_orchid_position = self.compute_orchid_orders(state, product, current_orchid_position)
                result[product] = orders

        conversions = 1
        traderData = state.traderData
        return result, conversions, traderData
    
    
from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np
# aaaaa

