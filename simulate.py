'''
Simulates the stock market and how different subreddits portfolios would
have performed over given dates.

Usage examples
--------------
If using data from the GitHub, make sure to unzip the data. Make sure the
directory structure follows:
    ├── data
    │   ├── scored_reddit.csv
    │   ├── stock_data
    │   │   ├── <stocks>.csv
    │   │   ├── . . .
    └── simulate.py

If collecting your own data, run the scripts in the following order:
    $python collect_stock_data.py -p 5y
    $python clean_reddit_data.py
    $python sentiment_analyzer.py
    $python simulate.py


Arguments
---------
-d --debug : Enter debug mode
-v --verbose : Be verbose

Objects
-------
Market
    read_in_stocks() -> None
Trader
    get_open() -> float
Stock
    day_trade() -> None
    evaluate_portfolio() -> None
    write_portfolio_to_csv() -> None
'''
import time
import os
import datetime
import argparse
import ast

import pandas as pd

parser = argparse.ArgumentParser(description='simulate portfolios')
parser.add_argument('-d', '--debug', action='store_true',
    help='Enter debug mode')
parser.add_argument('-v', '--verbose', action='store_true', help='Be verbose')
args = parser.parse_args()


class Market():
    '''
    Simulates the stock market

    Attributes
    ----------
    self.traders : List<Trader>
        Each Trader object represents a subreddit that can buy/sell stocks
        based on sentiment

    self.start_date : datetime.date
        The first day of the simulation

    self.end_date : datetime.date
        The last day of the simulation

    self.stocks : dict
        A dictionary of the available stocks, each entry takes the form:
        {symbol : Stock} (see Stock object)

    Methods
    -------
    read_in_stocks(stock_data_dir -> str) -> None
    simulate() -> None
    '''
    def __init__(self, traders, stock_data_dir, start_date, end_date):
        self.traders = traders
        self.start_date = start_date
        self.end_date = end_date
        self.stocks = {}


    def read_in_stocks(self, stock_data_dir):
        '''
        Populates self.stocks by loading in the stock data

        Parameters
        ---------
        stock_data_dir : str
            Filepath to directory containing all the csv files for each stock
        '''
        for root, dirs, files in os.walk(stock_data_dir):
            for name in files:
                stock_name = name.strip('.csv')
                self.stocks[stock_name] = Stock(stock_name)


    def simulate(self):
        '''
        Simulates the stock market and the impacts on each trader's
        portfolios, when finished, writes each portfolio to a csv file
        '''
        self.read_in_stocks('data/stock_data')
        current_date = self.start_date
        while current_date <= self.end_date:
            current_date += datetime.timedelta(days=1)

            for trader in self.traders:
                if args.verbose and current_date.day == 1:
                    trader.day_trade(str(current_date), self.stocks, True)
                else:
                    trader.day_trade(str(current_date), self.stocks)
                trader.evaluate_portfolio(self.stocks, current_date)


        for trader in self.traders:
            trader.write_portfolio_to_csv()



class Stock():
    '''
    Represents a single stock

    Attributes
    ----------
    self.symbol : str
        The stock's NASDAQ symbol

    self.data : pandas.core.frame.DataFrame
        The stock's open price on each date

    Methods
    -------
    get_open(date -> str) -> float
    '''
    def __init__(self, stock_name):
        self.symbol = stock_name
        self.data = pd.read_csv(f'data/stock_data/{stock_name}.csv').loc[:, 'Date':'Open']


    def get_open(self, date):
        '''
        Gets the opening price of the stock on <date>

        Parameters
        ----------
        date : str
            The date of the opening price to be accessed

        Returns
        -------
        stock_open -> float
            The opening price of the stock on <date> (rounded to 2 decimal
            places)

        TODO
        ----
        If a stock's opening price cannot be found on a given date, this
        method currently simply retruns 0. Determine a better way to handle
        these situations
        '''
        date = str(date)
        stock_open = 0
        try:
            stock_open = round(float(self.data.loc[self.data['Date'] == date]['Open']), 2)
        except:
            if args.verbose and args.debug:
                print(f'WARNING: stock_open was unable to be parsed for '
                    f'{self.symbol} on {date}, returning 0. {stock_open}')

        return stock_open


class Trader():
    '''
    Represents a subreddit, has the ability to buy/sell stocks based on
    that subreddit's sentiment

    Attributes
    ----------
    self.subreddit : str
        The subreddit name (ex: investing)

    self.data : pandas.core.frame.DataFrame
        All the scored comments from the subreddit

    self.owned_stocks : dict{<str>, <int>}
        A dictionary containing the name of stocks this Trader has bought as
        the keys, as well as the quantity bought as the values.

    self.cost_basis : float
       How much money this Trader has spent buying stocks

    self.data_portfolio_values : dict{<str>, <float>}
        A dictionary containing dates as the keys and how much this Trader's
        portfolio was worth on those dates as the values

    Methods
    -------
    day_trade(date -> str, stocks -> List<Stock>, verbose -> bool) -> None
    evaluate_portfolio(stocks -> List<Stock>, date -> str) -> None
    write_portfolio_to_csv() -> None
    '''
    def __init__(self, subreddit, data):
        self.subreddit = subreddit
        self.data = data.loc[data['subreddit'] == subreddit]
        self.owned_stocks = {stock:0 for stock in self.data['stock']}
        self.cost_basis = 0.0
        self.dated_portfolio_values = {}

        if args.debug:
            self.data = self.data.head(10)
            print(f'{subreddit} trader initialized. Data:\n{self.data}')


    def day_trade(self, date, stocks, verbose=False):
        '''
        Simulate buying/selling <stocks> on <date>

        TODO
        ----
        At the moment, Trader can only buy/sell a single share of a given
        stock per day. It would probably be better if it could, for example,
        buy a ton of shares of a single stock if the sentiment towrads that
        stock were extremely positive.

        Parameters
        ----------
        date : str
            The date the simulated trading to take place on

        stocks : List<Stock>
            List containing stocks and their historical opening prices

        Modifies
        --------
        self.owned_stocks
        self.cost_basis

        Notes
        -----
        Occassionaly in the data there will be multiple posts/comments
        discussing the same stock, and those sentiments may diverge. In these
        situations, the sentiment that received the most 'upvotes' from users
        will be the one acted upon. For example, if there are two comments for
        GME, one with a positive sentiment and 10,000 upvotes, and another
        with a negative sentiment with 7,000 upvotes, the Trader will elect to
        BUY a share of GME
        '''
        todays_posts = pd.DataFrame(self.data.loc[self.data['date'] == date])
        stock_buy_sell = {stock:0 for stock in todays_posts['stock']}
        if verbose:
            print(f'{"-" * 50}\n Now day trading as r/{self.subreddit} on '\
                f'{date}\n{"-" * 50}')

        for _, row in todays_posts.iterrows():
            name = row['stock']
            score = ast.literal_eval(row['sentiment_score'])
            upvotes = row['score']
            if score['pos'] > score['neg']:
                stock_buy_sell[name] += upvotes
            else:
                stock_buy_sell[name] -= upvotes

        for stock, buyscore in stock_buy_sell.items():
            stock_data = stocks[stock]
            stock_open = stock_data.get_open(date)

            if buyscore > 0:
                self.owned_stocks[stock] += 1
                self.cost_basis += stock_open

                if verbose:
                    print(f'{self.subreddit} bought {stock} for ${stock_open}')
            elif buyscore < 0 and self.owned_stocks[stock] > 0:
                self.owned_stocks[stock] -= 1
                self.cost_basis -= stock_open
                if verbose:
                    print(f'{self.subreddit} sold {stock} for ${stock_open}')

        if verbose:
            print(f"r/{self.subreddit}'s portfolio on {date}:")
            for key, value in self.owned_stocks.items():
                if value != 0:
                    print(f'{key}: {value}', end=' ')
            print()


    def evaluate_portfolio(self, stocks, date):
        '''
        Determines the dollar value of Trader's portfolio on <date>

        Parameters
        ----------
        stocks : List<Stock>
            List containing stocks and their historical opening prices

        date : str
            The date to evaluate the simulated portfolio

        Modifies
        --------
        self.dated_portfolio_values
        '''
        if args.debug:
            print(f"Evaluating r/{self.subreddit}'s portfolio:\n"\
            f"{self.owned_stocks}")
        portfolio_value = 0
        for stock, quantity in self.owned_stocks.items():
            portfolio_value += round(stocks[stock].get_open(date) * quantity, 2)

        self.dated_portfolio_values[date] = portfolio_value
        if args.verbose:
            print(f"r/{self.subreddit}'s portfolio is worth ${portfolio_value} "\
                f"on {date}. They spent ${self.cost_basis} for a profit/loss of "\
                f"${portfolio_value - self.cost_basis}")


    def write_portfolio_to_csv(self):
        '''
        Writes self.owned_stocks and self.date_portfolio_values to a csv file
        in the data/results/ directory; those files will be named
        <subreddit>_stocks.csv and <subreddit>_p_value.csv respectively
        '''
        stocks = pd.DataFrame.from_dict(self.owned_stocks, orient='index')
        stocks.to_csv(f'data/results/{self.subreddit}_stocks.csv')

        p_value = pd.DataFrame.from_dict(self.dated_portfolio_values, orient='index')
        p_value.to_csv(f'data/results/{self.subreddit}_p_value.csv')


if __name__ == '__main__':
    start = time.time()
    data = pd.read_csv('data/scored_reddit.csv')
    if not os.path.exists('data/results'):
        if args.verbose:
            print('results data directory not found, creating a new one')
        os.mkdir('data/results')


    wallstreetbets = Trader('wallstreetbets', data)
    investing = Trader('investing', data)
    stocks = Trader('stocks', data)

    start_date = datetime.date(2017, 1, 27)
    end_date = datetime.date(2021, 1, 27)
    market = Market([wallstreetbets, investing, stocks], 'data/stock_data', start_date, end_date)
    market.simulate()
    if args.verbose:
        print(f'Took {time.time() - start} seconds to complete')
