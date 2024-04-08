class Trader:
    def __init__(self):
        self.position = 0  # Initial position
        self.target_buy_price = 10004  # Target buy price
        self.target_sell_price = 9996  # Target sell price

    def run(self, state):
        order_depths = state.order_depths
        AMETHYSTS_orders = []

        if 'AMETHYSTS' in order_depths:
            AMETHYSTS_depth = order_depths['AMETHYSTS']
            if len(AMETHYSTS_depth.sell_orders) > 0:
                best_ask_price = min(AMETHYSTS_depth.sell_orders.keys())
                best_ask_quantity = AMETHYSTS_depth.sell_orders[best_ask_price]
                if best_ask_price <= self.target_buy_price:
                    # Calculate quantity to buy based on position limits
                    max_buy_quantity = min(20 - self.position, best_ask_quantity)
                    if max_buy_quantity > 0:
                        AMETHYSTS_orders.append(Order('AMETHYSTS', best_ask_price, max_buy_quantity))

            if len(AMETHYSTS_depth.buy_orders) > 0:
                best_bid_price = max(AMETHYSTS_depth.buy_orders.keys())
                best_bid_quantity = abs(AMETHYSTS_depth.buy_orders[best_bid_price])  # Taking absolute value
                if best_bid_price >= self.target_sell_price:
                    # Calculate quantity to sell based on available position
                    max_sell_quantity = min(self.position, best_bid_quantity)
                    if max_sell_quantity > 0:
                        AMETHYSTS_orders.append(Order('AMETHYSTS', best_bid_price, -max_sell_quantity))

        return {'AMETHYSTS': AMETHYSTS_orders}, 0, None
