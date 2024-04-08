from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

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
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    # print("Best ask: ", best_ask)
                    if int(best_ask) <= buy_price:
                        print("BUYING AMETHYSTS", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
                        current_amethysts_position -= best_ask_amount
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) >= sell_price:
                        print("SELLING AMETHYSTS", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                        current_amethysts_position += best_bid_amount
                
                result[product] = orders
            if product == "STARFRUIT":
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
                        if current_star_fruit_position + best_bid_amount <= position_limit:
                            print("BUYING STARFRUIT")
                            orders.append(Order(product, best_bid, -best_bid_amount))
                            current_star_fruit_position += best_bid_amount
                    if best_ask > average_price + 2:
                        if current_star_fruit_position - best_ask_amount >= -position_limit:
                            print("SELLING STARFRUIT")
                            orders.append(Order(product, best_ask, -best_ask_amount))
                            current_star_fruit_position -= best_ask_amount
                result[product] = orders
                            
    
        conversions = 1
        traderData = "Hey"
        return result, conversions, traderData
    
    
    

def main():
    print("we begin")


if '__name__' == __main__:
    main()
