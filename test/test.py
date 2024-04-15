import os
from datamodel import Listing, OrderDepth, Trade, TradingState
import pandas as pd
import math

import sys
sys.path.append('../round-1')
from round_one import Trader


def main(products, position_limit, traderData):
    position = {}
    performance = []
    for product in products:
        position[product] = 0
        1
    round_dir = "round-" + input("which round? ")
    file_path = os.path.join('..', round_dir, 'data')
    price_files = [file for file in os.listdir(file_path) if file.startswith('prices')]
    price_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    trades_files = [file for file in os.listdir(file_path) if file.startswith('trades')]
    trades_files.sort(key=lambda x: int(x.split('_')[-2].split('.')[0]))
    seashells = 0
    final_price_am = 0
    final_price_st = 0

    
    
    for price_file, trades_file in zip(price_files, trades_files):
        print("\n\n")
        print("looking at file", price_file)
        data = pd.read_csv(os.path.join(file_path, price_file), encoding='cp1252', delimiter=';')
        dataTrades = pd.read_csv(os.path.join(file_path, trades_file), encoding='cp1252', delimiter=';')
        timestamps = data['timestamp'].unique()
        conversions = {}
        for timestamp in timestamps:
            trader_instance, trader_state, final_price_am, final_price_st = create_round(data, dataTrades, position, products, timestamp, conversions, traderData)
            result, conversions, traderData = Trader.run(trader_instance, trader_state)
            for product, orders in result.items():
                print(orders)
                for order in orders:
                    seashells += order.price*(-1 * order.quantity)
                    position[order.symbol] += order.quantity
        print()
        print(seashells + position["AMETHYSTS"] * final_price_am + position["STARFRUIT"] * final_price_st)
        performance.append(seashells)
    
    for i in range(len(performance)):
        print(f'Round {i}: {performance[i]}')

    for i in range(len(products)):
        print(f'Position of {products[i]} is: {position[products[i]]}')
    return seashells

    
def create_round(data, dataTrades, position, products, timestamp, conversions, traderData):
    new_data = data[data['timestamp'] == timestamp]
    new_trades = dataTrades[dataTrades['timestamp'] == timestamp]
    product = new_trades['symbol']
    # if timestamp == 100:
        # print(" ")
        # print("===========================================")
        # print(new_trades)
        # print("===========================================")
    listings = {}
    order_depths = {}
    own_trades = {}
    market_trades = {}
    for product in products:
        market_trades[product] = []
    final_price_am = 0
    final_price_st = 0
    
    for i in range(len(new_trades)):
        trade = new_trades.iloc[i]
        product = trade['symbol']
        market_trades[product].append({
            'symbol': product,
            'price': trade['price'],
            'quantity': trade['quantity'],
            'buyer': trade['buyer'],
            'seller': trade['seller'],
            'timestamp': trade['timestamp']
        })
        if trade['symbol'] == 'AMETHYSTS':
            final_price_am = trade['price']
        elif trade['symbol'] == 'STARFISH':
            final_price_st = trade['price']
    for i in range(len(new_data)):
        listing = new_data.iloc[i]
        product = listing['product']
        listings[product] = Listing(
            symbol=product,
            product=product,
            denomination="SEASHELLS"
        )
        buy_orders = {}
        sell_orders = {}
        bids = {}
        asks = {}
        for column_name, column_value in listing.items():
            if column_name.startswith('bid_price_'):
                volume_column = 'bid_volume_' + column_name.split('_')[-1]
                if not math.isnan(column_value) and not math.isnan(listing[volume_column]):
                    bids[int(column_value)] = int(listing[volume_column])
            elif column_name.startswith('ask_price'):
                volume_column = 'ask_volume_' + column_name.split('_')[-1]
                if not math.isnan(column_value) and not math.isnan(listing[volume_column]):
                    asks[int(column_value)] = -1 * int(listing[volume_column])
        # if timestamp == 100:
            # print("bids", bids)
            # print("asks", asks)
        # Create the OrderDepth object and assign buy_orders and sell_orders
        order_depths[product] = OrderDepth(
            buy_orders=bids,
            sell_orders=asks
        )
        trader_state = TradingState(
            traderData,
            timestamp,
            listings,
            order_depths,
            own_trades,
            market_trades,
            position,
            conversions
        )
    
    return Trader(), trader_state, final_price_am, final_price_st




# timestamp = 1100

# listings = {
# 	"PRODUCT1": Listing(
# 		symbol="PRODUCT1", 
# 		product="PRODUCT1", 
# 		denomination="SEASHELLS"
# 	),22
# 	"PRODUCT2": Listing(
# 		symbol="PRODUCT2", 
# 		product="PRODUCT2", 
# 		denomination="SEASHELLS"
# 	),
# }

# order_depths = {
# 	"PRODUCT1": OrderDepth(
# 		buy_orders={10: 7, 9: 5},
# 		sell_orders={12: -5, 13: -3}
# 	),
# 	"PRODUCT2": OrderDepth(
# 		buy_orders={142: 3, 141: 5},
# 		sell_orders={144: -5, 145: -8}
# 	),	
# }

# own_trades = {
# 	"PRODUCT1": [
# 		Trade(
# 			symbol="PRODUCT1",
# 			price=11,
# 			quantity=4,
# 			buyer="SUBMISSION",
# 			seller="",
# 			timestamp=1000
# 		),
# 		Trade(
# 			symbol="PRODUCT1",
# 			price=12,
# 			quantity=3,
# 			buyer="SUBMISSION",
# 			seller="",
# 			timestamp=1000
# 		)
# 	],
# 	"PRODUCT2": [
# 		Trade(
# 			symbol="PRODUCT2",
# 			price=143,
# 			quantity=2,
# 			buyer="",
# 			seller="SUBMISSION",
# 			timestamp=1000
# 		),
# 	]
# }

# market_trades = {
# 	"PRODUCT1": [],
# 	"PRODUCT2": []
# }

# position = {
# 	"PRODUCT1": 10,
# 	"PRODUCT2": -7
# }

# observations = {}

# traderData = ""

# state = TradingState(
# 	traderData,
# 	timestamp,
#     listings,
# 	order_depths,
# 	own_trades,
# 	market_trades,
# 	position,
# 	observations
# )


main(["AMETHYSTS", "STARFRUIT"], 20, "hey")
