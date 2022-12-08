import time
import os
import datetime
import argparse

import pandas as pd
import numpy as np
import ast

parser = argparse.ArgumentParser(description='simulate portfolios')
parser.add_argument('-d', '--debug', action='store_true',
    help='Enter debug mode')
parser.add_argument('-v', '--verbose', action='store_true', help='Be verbose')
args = parser.parse_args()


def read_in_data(data):
    '''
    Reads in the data from a csv file

    Parameters
    ----------
    data : str
        The filepath to the csv file to be read in for analysis

    returns
    --------
    pandas.core.frame.DataFrame
        The data to be analyzed
    '''
    return pd.read_csv(data)


class Market():
    def __init__(self, traders, stock_data_dir, start_date, end_date):
        self.traders = traders
        self.start_date = start_date
        self.end_date = end_date
        self.stocks = {}


    def read_in_stocks(self, stock_data_dir):
        for root, dirs, files in os.walk(stock_data_dir):
            for name in files:
                stock_name = name.strip('.csv')
                #df = pd.read_csv(os.path.join(root, name))
                #self.stocks[name.strip('.csv')] = df.loc[:, 'Date':'Open']
                self.stocks[stock_name] = Stock(stock_name)


    def simulate(self):
        '''
        Simulates the stock market and the impacts on each trader's portfolios

        Parameters
        ----------
        traders : List<Trader>
            The traders participating in the simulation

        start_date : datetime.date
            The date for the simulation to begin

        end_date : datetime.date
            The date for the simulation to end
        '''
        self.read_in_stocks('data/stock_data')
        current_date = self.start_date
        while (current_date <= self.end_date):
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
    def __init__(self, stock_name):
        self.symbol = stock_name
        self.data = pd.read_csv(f'data/stock_data/{stock_name}.csv').loc[:, 'Date':'Open']


    def get_open(self, date):
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
    def __init__(self, subreddit, data):
        self.subreddit = subreddit
        self.data = data.loc[data['subreddit'] == subreddit]
        self.owned_stocks = {stock:0 for stock in self.data['stock']}
        self.cost_basis = 0
        self.dated_portfolio_values = {}

        if args.debug:
            self.data = self.data.head(10)
            print(f'{subreddit} trader initialized. Data:\n{self.data}')


    def day_trade(self, date, stocks, verbose=False):
        todays_posts = pd.DataFrame(self.data.loc[self.data['date'] == date])
        if verbose:
            print(f'{"-" * 50}\n Now day trading as r/{self.subreddit} on '\
                f'{date}\n{"-" * 50}')
        stock_buy_sell = {stock:0 for stock in todays_posts['stock']}
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
                if verbose:
                    print(f'{self.subreddit} sold {stock} for ${stock_open}')

        if verbose:
            print(f"r/{self.subreddit}'s portfolio on {date}:")
            for key, value in self.owned_stocks.items():
                if value != 0:
                    print(f'{key}: {value}', end=' ')
            print()


    def write_portfolio_to_csv(self):
       stocks = pd.DataFrame.from_dict(self.owned_stocks, orient='index')
       stocks.to_csv(f'results/{self.subreddit}_stocks.csv')

       p_value = pd.DataFrame.from_dict(self.dated_portfolio_values, orient='index')
       p_value = p_value[p_value['0'] > 0]
       p_value.to_csv(f'results/{self.subreddit}_p_value.csv')


    def evaluate_portfolio(self, stocks, date):
        if args.debug:
            print(f"Evaluating r/{self.subreddit}'s portfolio:\n"\
            f"{self.owned_stocks}")
        portfolio_value = 0
        for stock, quantity in self.owned_stocks.items():
            portfolio_value += stocks[stock].get_open(date) * quantity

        self.dated_portfolio_values[date] = portfolio_value
        if args.verbose:
            print(f"r/{self.subreddit}'s portfolio is worth ${portfolio_value} "\
                f"on {date}. They spent ${self.cost_basis} for a profit/loss of "\
                f"${portfolio_value - self.cost_basis}")


if __name__ == '__main__':
    start = time.time()
    data = read_in_data('data/scored_reddit.csv')


    wallstreetbets = Trader('wallstreetbets', data)
    investing = Trader('investing', data)
    stocks = Trader('stocks', data)

    start_date = datetime.date(2017, 1, 1)
    end_date = datetime.date(2021, 1, 27)
    market = Market([wallstreetbets, investing, stocks], 'data/stock_data', start_date, end_date)
    market.simulate()
    print(f'Took {time.time() - start} seconds to complete')
