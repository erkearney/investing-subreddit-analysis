'''
Combines stock market data and reddit post data into a new file, written to
clean_reddit.csv. The new file takes the form of:

  stock                          title   body       subreddit   score                 date
0   GME  GME YOLO update — Jan 28 2021  empty  wallstreetbets  230844  2021-01-29 08:06:23

Methods
-------
read_stock_data(symbols_names)
clean_reddit_data(reddit_data)
'''
import argparse
import re

import pandas as pd

import nltk

parser = argparse.ArgumentParser(description='Clean reddit data')
parser.add_argument('-d', '--debug', action='store_true',
    help='Enter debug mode')
parser.add_argument('-v', '--verbose', action='store_true', help='Be verbose')
args = parser.parse_args()

def read_stock_data(symbols_names):
    '''
    Reads in and cleans up stock data

    Returns
    -------
    stocks : dict<symbol, name>
        Contains the NASDAQ symbol and the company name of the securities from
        the dataset
    '''
    stocks = {}
    with open (symbols_names) as f:
        for line in f:
            pair = line.replace('\n', '').split(',')
            stocks[pair[0]] = pair[1]

    return stocks


def read_reddit_data(reddit_data):
    '''
    Reads the reddit data into a pandas dataframe

    Returns
    -------
    pandas.core.frame.DataFrame
    '''
    return pd.read_csv(reddit_data)


def clean_reddit_data(reddit_df, stocks):
    '''
    Perform general data pre-processing, including removing all posts/comments
    that make no mention of a security in the stocks list. Merge the stock
    data and reddit data into a new dataframe, and write that dataframe out

    Parameters
    ----------
    reddit_df : pandas.core.frame.DataFrame
        returned from read_reddit_data()

    stocks : pandas.core.frame.DataFrame
        returned from read_stock_data

    Returns
    ----------
    clean_data : pandas.core.frame.DataFrame
    '''
    #nltk.download('stopwords')
    if args.debug:
        reddit_df = reddit_df.head(10)
    reddit_df = reddit_df.fillna('empty')

    clean_data = []
    stops = set(nltk.corpus.stopwords.words('english'))
    for i in range(len(reddit_df)):
        text = re.sub(r'[^\w\s]', '', f'{reddit_df.loc[i, "title"]} '\
            f'{str(reddit_df.loc[i, "body"])}').split(' ')
        text = [word for word in text if word not in stops]
        for key in stocks.keys():
            if key in text:
                clean_data.append(
                    {
                        'stock' : key,
                        'title' : reddit_df.loc[i, 'title'],
                        'body' : reddit_df.loc[i, 'body'],
                        'subreddit' : reddit_df.loc[i, 'subreddit'],
                        'score' : reddit_df.loc[i, 'score'],
                        'date' : reddit_df.loc[i, 'date'].split(' ')[0]
                        # Strip time from date column ^
                    }
                )


    clean_data = pd.DataFrame(clean_data)
    clean_data.to_csv('data/clean_reddit.csv')

    if args.verbose:
        print(f'cleaned data:\n {clean_data}')

    return clean_data


if __name__ == '__main__':
    stocks = read_stock_data('data/symbols_names.csv')
    reddit_df = read_reddit_data('data/reddit.csv')
    clean_reddit_data(reddit_df, stocks)
