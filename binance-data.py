import os
import requests
import json
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import websocket

class Binance:

    def __init__(self, api_key:str, api_secret:str) -> None:
        self.base_urls=["https://api.binance.com","https://api1.binance.com","https://api2.binance.com","https://api3.binance.com"]
        self.api_key = api_key
        self.api_secret=api_secret
        self.base_url=""
        self.base_websocket="wss://stream.binance.com:9443/ws/"
        self.ticker_dataframe = pd.DataFrame()
        self.kline = pd.DataFrame()

        def connect():
            '''
            Check if binance API services are avaliable and set self.base_url API endpoint
            '''
            for url in self.base_urls:
                response_status = requests.get(url).status_code
                if response_status == 200:
                    self.base_url = url
                    print("ENDPOINT --> "+url)
                    break
        
        connect()
      

    def generate_df(self, data:list)->pd.DataFrame:
        df = pd.DataFrame(data,
        columns=[
            'date','open price', 'high price', 'low price', 'close price', 'volume', 'candle close time', 'quote asset volume', 
            'number of trades', 'taker buy base asset volume', 'taker buy quote asset volume', 'ignore'
        ])
        df.drop(columns=df.columns[5:].values,inplace=True, axis=1)
        df['date'] = df['date'].map(lambda x: datetime.datetime.fromtimestamp(x/1000).strftime('%Y-%m-%d %H:%M:%S'))
        df[df.columns[1:].values]=df[df.columns[1:].values].apply(pd.to_numeric)
        print("Generated DF")
        print("-"*10)
        print(df.info())
        print("-"*10)
        self.ticker_dataframe = df

    def get_initial_kline_data(self, ticker:str, interval:str="15m", time_start:str=None, time_end:str=None, limit:int=None)->list:
        '''
        Generate the kline for ONE symbol(ticker) between a start_time and start_end, with a time interval for each kline.
            ticker: trading symbol for example 
            interval: 1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1D,3D,1S,1M
        '''
        self.add_url=self.base_url+"/api/v3/klines"
        params = {
            'symbol': ticker,
            'interval':interval,
            **({'startTime':time_start} if time_start is not None else {}),
            **({'endTime':time_end} if time_end is not None else {}),
            **({'limit':limit} if limit is not None else {})
        }
        response = requests.get(self.add_url, params=params)

        self.generate_df(response.json())


    def get_exhange_info(self)->json:
        self.add_url="/api/v3/exchangeInfo"
        response = requests.get(self.base_url+self.add_url)
        return response.json()

    def __long_positino(self, ticker:str, amount:int):
        '''
            Funcion para establecer 
        '''
        pass

    def __short_position(self, ticker:str, amount:int):
        pass

    def __generate_klines(self):
        date_time = self.kline['date'].iloc[-1]
        open_price=self.kline['open price'].iloc[0]
        close_price=self.kline['close price'].iloc[self.kline.shape[0]]
        high_price=self.kline['high price'].max()
        low_price=self.kline['low price'].min()
        new_list=[date_time, open_price, high_price, low_price, close_price]
        print(new_list)
        self.kline = self.kline.iloc[0:0]
        self.ticker_dataframe.loc[self.ticker_dataframe.shape[0]] = new_list  


    def connect_webhook(self, ticker:str, interval:str="3m"):
        socket = self.base_websocket+ticker+"@kline_"+interval
        print("STARTING WEBSOCKET -->", socket)

        def on_message(wsapp, message):  
            json_message = json.loads(message)
            handle_trades(json_message)

        def on_error(wsapp:websocket.WebSocketApp, error):
            print("ERROR: ",error)
            wsapp.close()

        def handle_trades(json_message):
            date_time = datetime.datetime.fromtimestamp(json_message['E']/1000).strftime('%Y-%m-%d %H:%M:%S')
            open_price = float(json_message['k']['o'])
            close_price = float(json_message['k']['c'])
            high_price = float(json_message['k']['h'])
            low_price = float(json_message['k']['l'])
            new_list=[date_time, open_price, high_price, low_price, close_price]
            print(date_time, str(json_message['k']['x']))
            if json_message['k']['x'] == True:
                #Calculate kline and close kline
                print(True)

        wsapp = websocket.WebSocketApp(socket, on_message=on_message, on_error=on_error)
        wsapp.run_forever()
        

if __name__=="__main__":
    client = Binance("test", "test")
    ticker = "ADABNB"
    client.get_initial_kline_data("SOLBUSD", "1m")
    client.connect_webhook("solbusd", "1m")

    ema_s = 7
    ema_l = 25
'''
    df['ema_s']=df['close price'].ewm(span=ema_s, min_periods=ema_s).mean()
    df['ema_l']=df['close price'].ewm(span=ema_l, min_periods=ema_l).mean()
    #print(df['ema_l'].iloc[-1])
    df.plot(figsize=(12,9), title='EUR/USD -- SMA{}|SMA{}'.format(ema_s, ema_l), fontsize=12, secondary_y="position")
    plt.legend(fontsize=12)
    plt.show()
'''