from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np
import math

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
            print('yo')

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
        position = state.position.get("ORCHIDS", 0)
        orders: list[Order] = []
        order_depth: OrderDepth = state.order_depths[product]
        
        osell = self.list_to_dict(sorted(order_depth.sell_orders.items()))
        obuy = self.list_to_dict(sorted(order_depth.buy_orders.items(), reverse=True))
        
        first_osell = list(osell.items())[0]
        last_osell = list(osell.items())[-1]
        first_obuy = list(obuy.items())[0]
        last_obuy = list(obuy.items())[-1]
        
        first_price_osell, first_position_osell = first_osell
        last_price_osell, last_position_osell = last_osell
        first_price_obuy, first_position_obuy = first_obuy
        last_price_obuy, last_position_obuy = last_obuy
        
        # vol = min(-1 * first_position_osell, -1 * last_position_osell, position_limit + position)
        # if vol + position < position_limit:
        #     orders.append(Order(product, first_price_osell, vol))
        #     orders.append(Order(product, last_price_osell, -1*vol))
        #     print(first_price_osell, last_price_osell)
        #     print(f'Bought orchids for {first_price_osell} and sold {-1 * vol} for {last_price_osell}')
        
        # vol = max(-1 * first_position_obuy, -1 * last_position_obuy, -1 * position_limit - position)
        # if position + vol > (-1 * position_limit):
        #     print(first_price_obuy, last_price_obuy)
        #     orders.append(Order(product, first_price_obuy, vol))
        #     orders.append(Order(product, last_price_obuy, -1*vol))
        #     print(f'Sold orchids for {first_price_obuy} and bought {-1 * vol} for {last_position_obuy}')
        

        conversion_observation = state.observations.conversionObservations.get(product, 0)
        print(conversion_observation.bidPrice, conversion_observation.askPrice)
        conversion_bid = conversion_observation.bidPrice
        conversion_ask = conversion_observation.askPrice
        conversion_import_tariff = conversion_observation.importTariff
        conversion_export_tariff = conversion_observation.exportTariff
        conversion_transport_fees = conversion_observation.transportFees
        conversions = 0
        average_price = round((conversion_bid + conversion_ask)/2)
        
        print(conversion_import_tariff, conversion_export_tariff, conversion_transport_fees)
        if position < 0:
            vol = min(first_position_obuy, abs(position))
            conversions = vol
            orders.append(Order(product, math.ceil(first_price_obuy + conversion_transport_fees + 2), -1 * vol))
            print("BUY CONVERSION")
        else:
            # if first_price_osell - average_price > average_price - first_price_obuy: #if it is better to sell because people are buying at higher prices
            orders.append(Order(product, math.ceil(first_price_obuy + conversion_transport_fees + 1), -1 * first_position_obuy))
            print("ORDER DIDN'T GO THROUGH")
            # else:
            #     orders.append(Order(product, math.ceil(first_price_osell + conversion_transport_fees), -1 * first_position_osell))
        # elif position > 0:
        #     vol = min(abs(first_position_osell), position)
        #     conversions = -1 * vol
        #     orders.append(Order(product, math.ceil(first_price_osell - conversion_transport_fees - conversion_export_tariff), vol))
        #     print("SELL CONVERSION")

        
        print(f'buy for less than {conversion_bid - abs(conversion_import_tariff) - abs(conversion_transport_fees)}')
        
        if state.timestamp == 99900:
            print(f'my position is {position}, converting {-1 * position}')
            return orders, -1 * position
        
        print(f'CONVERTING {conversions} ORCHIDS')
        return orders, conversions

    def run(self, state: TradingState):
        result = {}
        current_amethysts_position = state.position.get('AMETHYSTS', 0)
        current_starfruit_position = state.position.get('STARFRUIT', 0)
        current_orchid_position = state.position.get('ORCHIDS', 0)
        orders: list[Order] = []
        acc_bid = {'AMETHYSTS' : 10000, 'STARFRUIT' : 5000} # we want to buy at slightly below
        acc_ask = {'AMETHYSTS' : 10000, 'STARFRUIT' : 5000} # we want to sell at slightly above
        conversions = 0
        
        for product in state.order_depths:
            # if product == "AMETHYSTS":
            #     orders, current_amethysts_position = self.compute_amethysts_orders(state, product, acc_bid[product], acc_ask[product])
            #     result[product] = orders
            
            # if product == "STARFRUIT":
            #     orders, current_starfruit_position = self.compute_starfruit_orders(state, product, acc_bid[product], acc_ask[product], current_starfruit_position)
            #     result[product] = orders
            
            if product == "ORCHIDS":
                orders, conversions = self.compute_orchid_orders(state, product, current_orchid_position)
                result[product] = orders

        traderData = state.traderData
        return result, conversions, traderData
