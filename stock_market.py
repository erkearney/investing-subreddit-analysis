import argparse

import pandas as pd


parser = argparse.ArgumentParser(description='Analyze reddit data')
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


class Stock():
    def __init__(self, stock_name):
        self.data = read_in_data(f'data/stock_data/{stock_name}.csv')

if __name__ == '__main__':
    stock = Stock('AAPL')
    print(stock.data)
