from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
    
    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}
        
        position_limit = 20
        current_position = 0
        
        for product in state.order_depths:
            if product == "AMETHYSTS":
                buy_price = 9998
                sell_price = 10002
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                print("Acceptable price : " + str(buy_price))
                print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
        
                for order in orders:
                    current_position += order.amount
                
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    print("Best ask: ", best_ask)
                    if int(best_ask) <= buy_price and current_position - best_ask_amount >= -position_limit:
                        print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
                        current_position -= best_ask_amount
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    print("Best bid ", best_bid)
                    if int(best_bid) >= sell_price and current_position + best_bid_amount <= position_limit:
                        print("SELL", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                        current_position += best_bid_amount
                
                result[product] = orders

            # elif product == "STARFRUIT":
                

    
        traderData = "Test"
        conversions = 1
        return result, conversions, traderData
