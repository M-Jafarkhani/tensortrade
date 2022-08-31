"""Contains methods and classes to collect data from
https://www.cryptodatadownload.com.
"""

import ssl
import pandas as pd
import urllib.request
import json
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context


class CryptoDataDownload:
    """Provides methods for retrieving data on different cryptocurrencies from
    https://www.cryptodatadownload.com/cdd/.

    Attributes
    ----------
    url : str
        The url for collecting data from CryptoDataDownload.

    Methods
    -------
    fetch(exchange_name,base_symbol,quote_symbol,timeframe,include_all_volumes=False)
        Fetches data for different exchanges and cryptocurrency pairs.

    """

    def __init__(self) -> None:
        self.url = "https://www.cryptodatadownload.com/cdd/"

    def fetch_default(self,
                      exchange_name: str,
                      base_symbol: str,
                      quote_symbol: str,
                      timeframe: str,
                      include_all_volumes: bool = False) -> pd.DataFrame:
        """Fetches data from all exchanges that match the evaluation structure.

        Parameters
        ----------
        exchange_name : str
            The name of the exchange.
        base_symbol : str
            The base symbol fo the cryptocurrency pair.
        quote_symbol : str
            The quote symbol fo the cryptocurrency pair.
        timeframe : {"d", "h", "m"}
            The timeframe to collect data from.
        include_all_volumes : bool, optional
            Whether or not to include both base and quote volume.

        Returns
        -------
        `pd.DataFrame`
            A open, high, low, close and volume for the specified exchange and
            cryptocurrency pair.
        """

        filename = "{}_{}{}_{}.csv".format(exchange_name, quote_symbol, base_symbol, timeframe)
        base_vc = "Volume {}".format(base_symbol)
        new_base_vc = "volume_base"
        quote_vc = "Volume {}".format(quote_symbol)
        new_quote_vc = "volume_quote"

        df = pd.read_csv(self.url + filename, skiprows=1)
        df = df[::-1]
        df = df.drop(["symbol"], axis=1)
        df = df.rename({base_vc: new_base_vc, quote_vc: new_quote_vc, "Date": "date"}, axis=1)

        df["unix"] = df["unix"].astype(int)
        df["unix"] = df["unix"].apply(
            lambda x: int(x / 1000) if len(str(x)) == 13 else x
        )
        df["date"] = pd.to_datetime(df["unix"], unit="s")

        df = df.set_index("date")
        df.columns = [name.lower() for name in df.columns]
        df = df.reset_index()
        if not include_all_volumes:
            df = df.drop([new_quote_vc], axis=1)
            df = df.rename({new_base_vc: "volume"}, axis=1)
            return df
        return df

    def fetch_mofid(self,
                    base_symbol: str,
                    quote_symbol: str,
                    timeframe: str) -> pd.DataFrame:
        """Fetches data from all exchanges that match the evaluation structure.

        Parameters
        ----------
        exchange_name : str
            The name of the exchange.
        base_symbol : str
            The base symbol fo the cryptocurrency pair.
        quote_symbol : str
            The quote symbol fo the cryptocurrency pair.
        timeframe : {"d", "h", "m"}
            The timeframe to collect data from.
        include_all_volumes : bool, optional
            Whether or not to include both base and quote volume.

        Returns
        -------
        `pd.DataFrame`
            A open, high, low, close and volume for the specified exchange and
            cryptocurrency pair.
        """

        base_vc = "Volume {}".format(base_symbol)
        new_base_vc = "volume_base"
        quote_vc = "Volume {}".format(quote_symbol)
        new_quote_vc = "volume_quote"

        timeframe = '1'
        startEpoch = datetime(2022, 8, 24, 0, 0).strftime('%s')
        endEpoch = datetime(2022, 8, 24, 23, 59).strftime('%s')

        url = f'https://rlcchartapi.mofidonline.com/ChartData/history?symbol={base_symbol}&resolution={timeframe}&from={startEpoch}&to={endEpoch}'

        df = pd.DataFrame([],columns = ['date','open','high','low','close',f'{base_vc}','volume'])

        rawContent = urllib.request.urlopen(url).read().decode('utf-8')
        json_content = json.loads(rawContent)
        size = len(json_content['t'])
        for i in range(size):
            df = df.append({
                'date': datetime.fromtimestamp(int(json_content['t'][i])),
                'open': json_content['o'][i],
                'high': json_content['h'][i],
                'low': json_content['l'][i],
                'close': json_content['c'][i],
                f'{base_vc}': json_content['v'][i],
                'volume': json_content['v'][i],
            },ignore_index=True)

        df = df.rename({base_vc: new_base_vc, quote_vc: new_quote_vc, "Date": "date"}, axis=1)

        df["unix"] = df["unix"].astype(int)
        df["unix"] = df["unix"].apply(
            lambda x: int(x / 1000) if len(str(x)) == 13 else x
        )
        df["date"] = pd.to_datetime(df["unix"], unit="s")

        df = df.set_index("date")
        df.columns = [name.lower() for name in df.columns]
        df = df.reset_index()
        return df

    def fetch_gemini(self,
                     base_symbol: str,
                     quote_symbol: str,
                     timeframe: str) -> pd.DataFrame:
        """
        Fetches data from the gemini exchange.

        Parameters
        ----------
        base_symbol : str
            The base symbol fo the cryptocurrency pair.
        quote_symbol : str
            The quote symbol fo the cryptocurrency pair.
        timeframe : {"d", "h", "m"}
            The timeframe to collect data from.

        Returns
        -------
        `pd.DataFrame`
            A open, high, low, close and volume for the specified
            cryptocurrency pair.
        """
        if timeframe.endswith("h"):
            timeframe = timeframe[:-1] + "hr"
        filename = "{}_{}{}_{}.csv".format("gemini", quote_symbol, base_symbol, timeframe)
        df = pd.read_csv(self.url + filename, skiprows=1)
        df = df[::-1]
        df = df.drop(["Symbol", "Unix Timestamp"], axis=1)
        df.columns = [name.lower() for name in df.columns]
        df = df.set_index("date")
        df = df.reset_index()
        return df

    def fetch(self,
              exchange_name: str,
              base_symbol: str,
              quote_symbol: str,
              timeframe: str,
              include_all_volumes: bool = False) -> pd.DataFrame:
        """Fetches data for different exchanges and cryptocurrency pairs.

        Parameters
        ----------
        exchange_name : str
            The name of the exchange.
        base_symbol : str
            The base symbol fo the cryptocurrency pair.
        quote_symbol : str
            The quote symbol fo the cryptocurrency pair.
        timeframe : {"d", "h", "m"}
            The timeframe to collect data from.
        include_all_volumes : bool, optional
            Whether or not to include both base and quote volume.

        Returns
        -------
        `pd.DataFrame`
            A open, high, low, close and volume for the specified exchange and
            cryptocurrency pair.
        """
        if exchange_name.lower() == "gemini":
            return self.fetch_gemini(base_symbol, quote_symbol, timeframe)
        elif exchange_name.lower() == "mofid":
            return self.fetch_mofid(base_symbol, quote_symbol, timeframe)
        return self.fetch_default(exchange_name,
                                  base_symbol,
                                  quote_symbol,
                                  timeframe,
                                  include_all_volumes=include_all_volumes)
