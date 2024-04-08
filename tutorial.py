from datamodel import OrderDepth, TradingState, Order
from typing import List

class Trader:
    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            if product == "AMETHYSTS":  # Assuming the product name is "AMETHYSTS"
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                buy_price = 9996
                sell_price = 10004
                position = sum(order.quantity for order in state.orders if order.product == product)

                # Check if the sell price is less than or equal to any buy orders
                for price, quantity in order_depth.buy_orders.items():
                    if sell_price <= price:
                        quantity_to_buy = min(quantity, 20 - position, 10)  # Buy at most 10 units or up to position limit
                        orders.append(Order(product, price, quantity_to_buy))
                        position += quantity_to_buy
                        print("BUY", quantity_to_buy, "AMETHYSTS at", price)
                        break  # Stop checking once a suitable buy order is found
                
                # Check if the buy price is greater than or equal to any sell orders
                for price, quantity in order_depth.sell_orders.items():
                    if price <= buy_price and position > -20:
                        quantity_to_sell = min(quantity, 20 + position, 10)  # Sell at most 10 units or up to position limit
                        orders.append(Order(product, price, -quantity_to_sell))
                        position -= quantity_to_sell
                        print("SELL", quantity_to_sell, "AMETHYSTS at", price)
                        break  # Stop checking once a suitable sell order is found
                
                result[product] = orders
        
        trader_data = ""  # No state data for this simple trader
        conversions = 0  # No conversion requests
        return result, conversions, trader_data
