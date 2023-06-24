import pandas as pd
import matplotlib.pyplot as plt

# Read data from CSV file
df = pd.read_csv("time1.csv", index_col="time", parse_dates=True)

# Create a figure with 2 subplots (price chart and TRS oscillator)
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.1})

# Plot closing prices line chart on the first subplot (ax1)
ax1.plot(df.index, df['close'], label="Close", color="blue", linewidth=1)
ax1.set_title("Price Chart")
ax1.set_ylabel("Price")

# Plot the TRS oscillator on the second subplot (ax2)
ax2.plot(df.index, df['TRS'], label="TRS", color="blue", linewidth=1)
ax2.set_title("TRS Oscillator")
ax2.set_ylabel("TRS")
ax2.axhline(70, color="red", linestyle="--", alpha=0.5)
ax2.axhline(30, color="red", linestyle="--", alpha=0.5)

# Set x-axis label and format
fig.autofmt_xdate()
plt.xlabel("Time")

# Show the plot
plt.show()
