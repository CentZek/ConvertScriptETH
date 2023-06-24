import pandas as pd
import numpy as np

# Load the data
df = pd.read_csv('time2.csv')

# Transaction cost
trans_cost = 0.00075

# TRS threshold
trs_threshold = 60

# Define the range of trailing entries and stop losses to test
trailing_entries = np.arange(1, 10, 1)  # change as needed
stop_losses = np.arange(10, 50, 5)  # change as needed

# Store the results
results = []

for entry in trailing_entries:
    for stop in stop_losses:
        # Initialize variables
        long_position = False
        entry_price = 0
        total_profit = 0
        profit_trades = 0
        loss_trades = 0
        
        for i in range(len(df)):
            # Check the TRS value
            if df.loc[i, 'TRS'] < trs_threshold and not long_position:
                # Enter a long position
                long_position = True
                entry_price = df.loc[i, 'close'] + entry
            elif long_position and (df.loc[i, 'close'] <= entry_price - stop):
                # Exit the position
                long_position = False
                
                # Calculate profit
                profit = entry_price - df.loc[i, 'close'] - 2 * entry * trans_cost
                total_profit += profit
                
                # Count profitable and loss trades
                if profit > 0:
                    profit_trades += 1
                else:
                    loss_trades += 1

        # Store the results for this combination
        results.append((entry, stop, total_profit, profit_trades, loss_trades))

# Sort the results by total profit and print the best combination
results.sort(key=lambda x: x[2], reverse=True)
best_combination = results[0]
print(f"Best combination: Trailing entry = {best_combination[0]}, Stop loss = {best_combination[1]}, Total profit = {best_combination[2]}, Profit trades = {best_combination[3]}, Loss trades = {best_combination[4]}")
