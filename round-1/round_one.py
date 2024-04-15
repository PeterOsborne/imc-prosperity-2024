from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np

class Trader:
    
    
    
    def run(self, state: TradingState):
        result = {}
        position_limit = 20
        current_amethysts_position = state.position.get('AMETHYSTS', 0)
        current_star_fruit_position = state.position.get('STARFRUIT', 0)
        
        for product in state.order_depths:
            if product == "AMETHYSTS":
                buy_price = 9998
                sell_price = 10002
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []

                # print("Acceptable price : " + str(buy_price))
                # print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))            
                if current_amethysts_position > 20 or current_amethysts_position < -20:
                    print("BUST")
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    # print("Best ask: ", best_ask)
                    if int(best_ask) <= buy_price and current_amethysts_position - best_ask_amount <= position_limit:
                        # print("BUYING AMETHYSTS", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
                        current_amethysts_position -= best_ask_amount
                    
                    elif int(best_ask) <= buy_price and position_limit - current_amethysts_position <=  abs(best_ask_amount):
                        best_ask_amount = -1*(position_limit - current_amethysts_position)
                        # print("BUYING AMETHYSTS 2", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
                        current_amethysts_position -= best_ask_amount
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) >= sell_price and current_amethysts_position - best_bid_amount >= (-1 * position_limit):
                        # print("SELLING AMETHYSTS", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                        current_amethysts_position += best_bid_amount
                    elif int(best_bid) >= sell_price and abs(position_limit - current_amethysts_position) <=  abs(best_bid_amount):
                        best_bid_amount = -1*abs(position_limit - current_amethysts_position)
                        # print("SELLING AMETHYSTS 2", str(-best_bid_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_bid_amount))
                        current_amethysts_position -= best_bid_amount
                    
                
                result[product] = orders
            # if product == "STARFRUIT":
            #     order_depth: OrderDepth = state.order_depths[product]
            #     orders: List[Order] = []
            #     if state.timestamp > 5:
            #         # last_50_prices = list(order_depth.sell_orders.items())[:5]
            #         # past_prices = [float(price) for price, _ in last_5_prices]
            #         # average_price = sum(past_prices) / len(past_prices)
                    
            #         buy_price = 5000
            #         sell_price = 5050
            #         best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            #         best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            #         if best_ask < buy_price and current_star_fruit_position - best_ask_amount <= position_limit:
            #             orders.append(Order(product, best_ask, -best_ask_amount))
            #             current_star_fruit_position -= best_ask_amount
            #             print("buying")
            #         if best_bid > sell_price and current_star_fruit_position - best_bid_amount >= (-1 * position_limit):
            #             orders.append(Order(product, best_bid, -best_bid_amount))
            #             current_star_fruit_position -= best_bid_amount
            #             print("selling")
                        
            #     result[product] = orders
                            
    
        conversions = 1
        traderData = state.traderData
        return result, conversions, traderData