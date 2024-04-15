from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np
# aaaaa


class Trader:
    def run(self, state: TradingState):
        result = {}
        position_limit = 100
        current_orchid_position = state.position.get('ORCHIDS', 0)
        print("hisihsssishhs")

        for product in state.order_depths:
            if product == "ORCHIDS":
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []

                conversion_observation = state.observations.conversionObservations.get(
                    product)
                print(conversion_observation.sunlight)
                print(conversion_observation.humidity)
                print(conversion_observation.importTariff)
                if conversion_observation:
                    if conversion_observation.sunlight > 4000 and conversion_observation.humidity > 88.5:
                        print("sell sell sell")
                        current_orchid_position += sell_orchid(
                            order_depth, current_orchid_position, position_limit, product, orders)

                    if conversion_observation.sunlight < 2000 and conversion_observation.humidity < 70 and conversion_observation.importTariff > -2.6:
                        print("BUususus")
                        current_orchid_position -= buy_orchid(
                            order_depth, current_orchid_position, position_limit, product, orders)

                    if conversion_observation.humidity > 95:
                        print("SELL")
                        current_orchid_position += sell_orchid(
                            order_depth, current_orchid_position, position_limit, product, orders)

                    # change this to 4350 upon submission (although wghen it is 100 it makes a ton of money)
                    if conversion_observation.sunlight > 100:
                        print("SELLEEEEE")
                        current_orchid_position += sell_orchid(
                            order_depth, current_orchid_position, position_limit, product, orders)

                result[product] = orders
        conversions = 1
        traderData = state.traderData
        return result, conversions, traderData


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
            best_bid_amount = -1 * \
                abs(position_limit - current_orchid_position)
            orders.append(Order(product, best_bid, -best_bid_amount))
            return -1 * (best_bid_amount)
    return 0  # Return 0 if there are no orders to execute
