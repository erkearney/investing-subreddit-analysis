import os
import re

import pandas as pd

def read_stock_data(symbols_names):
    stocks = {}
    with open (symbols_names) as f:
        for line in f:
            pair = line.replace('\n', '').split(',')
            stocks[pair[0]] = pair[1]

    return stocks


def read_reddit_data(reddit_data):
    return pd.read_csv(reddit_data)


def clean_reddit_data(reddit_df, stocks):
    '''
    Remove all posts/comments that make no mention of a security in the stocks
    list.
    '''
    # For debugging purposes, reduce the dataframe size to improve runtime
    #reddit_df = reddit_df.head(100)

    print(reddit_df)
    stocks_id = {}
    for i in range(len(reddit_df)):
        remove = True
        text = re.sub(r'[^\w\s]', '', f'{reddit_df.loc[i, "title"]} {str(reddit_df.loc[i, "body"])}').split(' ')
        for key, value in stocks.items():
            if (key in text):
                stocks_id[key] = reddit_df.loc[i, "title"]
                remove = False
                continue

        if remove:
            reddit_df = reddit_df.drop(index=i)




    reddit_df['Stock'] = stocks_id
    print(reddit_df)
    reddit_df.to_csv('data/clean_reddit.csv')


if __name__ == '__main__':
    stocks = read_stock_data('data/symbols_names.csv')
    reddit_df = read_reddit_data('data/reddit.csv')
    clean_reddit_data(reddit_df, stocks)
