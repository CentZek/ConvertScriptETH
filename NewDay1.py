import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from ta.momentum import RSIIndicator
from ta.volume import MFIIndicator as MoneyFlowIndex

class ConvertBybitData:

    def __init__(self, user_input, period=14):
        self.url = "https://public.bybit.com/trading/ETHUSD/"
        self.start_year, self.start_month, self.start_day, self.num_days = user_input
        self.period = period

        self.links = self.get_links()
        self.df = pd.DataFrame()

    def get_links(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "lxml")
        links = [link.get("href") for link in soup.find_all("a") if link.get("href").endswith(".csv.gz")]

        start_date = datetime(self.start_year, self.start_month, self.start_day)
        return [link for link in links if datetime.strptime(link[6:16], "%Y-%m-%d") >= start_date]

    def preprocess_data(self, dataframe):
        dataframe['timestamp'] = dataframe['timestamp'].astype(int)
        dataframe.set_index('timestamp', inplace=True)

        ohlcv_data = dataframe.groupby(dataframe.index).agg({'price': ['last', 'max', 'min', 'first'], 'size': 'sum'})
        ohlcv_data.columns = ['open', 'high', 'low', 'close', 'volume']

        # Temporarily convert the index to a DatetimeIndex
        ohlcv_data.index = pd.to_datetime(ohlcv_data.index, unit='s')

        # Set the desired period value
        period = self.period

        # Resample the data to 1-minute
        ohlcv_1min = ohlcv_data.resample('1T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}).dropna()

        # Calculate RSI for 1-minute time frame
        rsi_1min = RSIIndicator(close=ohlcv_1min['close'], window=period).rsi()

        # Calculate MFI for 1-minute time frame
        mfi_1min = MoneyFlowIndex(
            high=ohlcv_1min['high'],
            low=ohlcv_1min['low'],
            close=ohlcv_1min['close'],
            volume=ohlcv_1min['volume'],
            window=period
        ).money_flow_index()

        # Interpolate 1-minute RSI and MFI back to the 1-second index
        rsi_interpolated = rsi_1min.reindex(ohlcv_data.index).interpolate(method='time').fillna(method='bfill')
        mfi_interpolated = mfi_1min.reindex(ohlcv_data.index).interpolate(method='time').fillna(method='bfill')

        ohlcv_data['RSI'] = rsi_interpolated
        ohlcv_data['MFI'] = mfi_interpolated

        # Calculate True Relative Strength (TRS) as the average of RSI and MFI values
        ohlcv_data['TRS'] = (ohlcv_data['RSI'] + ohlcv_data['MFI']) / 2

        # Convert the index back to Unix timestamps (Int64)
        ohlcv_data.index = ohlcv_data.index.astype(int) // 10**9

        return ohlcv_data
    
    def execute(self):
        for idx, link in enumerate(self.links[:self.num_days]):
            print(f"Processing {link} ({idx + 1}/{self.num_days})...")
            file_url = self.url + link

            column_names = ["timestamp", "symbol", "side", "size", "price", "tickDirection", "trdMatchID", "grossValue", "homeNotional", "foreignNotional"]
            tick_data = pd.read_csv(file_url, compression="gzip", skiprows=1, names=column_names)

            ohlcv_data = self.preprocess_data(tick_data)
            self.df = pd.concat([self.df, ohlcv_data], axis=0)
            
    def save_to_file(self):
        # Drop the RSI and MFI columns before saving the data to the output file
        self.df.drop(columns=['RSI', 'MFI'], inplace=True)

        start_date = self.links[0].replace(".csv.gz", "")
        end_date = self.links[self.num_days - 1].replace(".csv.gz", "")[6:]
        output_file = f'{start_date}_{end_date}_1s_OHLCV_TRS.csv'
        self.df.to_csv(output_file, index_label='time')
        print(f"Saved 1-second OHLCV data with 1-minute TRS to {output_file}")

def get_user_input():
    input_start_year = int(input("Enter the starting year (e.g., 2019): "))
    input_start_month = int(input("Enter the starting month (1-12): "))
    input_start_day = int(input("Enter the starting day (1-31): "))
    input_num_days = int(input("Enter the number of days to process (default 30): ") or 30)
    input_period = int(input("Enter the period for RSI and MFI (default 14): ") or 14)

    return input_start_year, input_start_month, input_start_day, input_num_days, input_period

if __name__ == "__main__":
    user_input = get_user_input()
    input_params, input_period = user_input[:-1], user_input[-1]
    converter = ConvertBybitData(input_params, input_period)
    converter.execute()
    converter.save_to_file()