import argparse
import pandas as pd
import yfinance as yf

parser = argparse.ArgumentParser(description='Download Yahoo Finance stock data')
parser.add_argument('-s', '--start',
    help='Date to start collecting data (YYYY-MM-DD ex: 2017-01-01)')
parser.add_argument('-e', '--end',
    help='Date to end collecting data (YYYY-MM-DD ex: 2017-04-30)')
parser.add_argument('-p', '--period',
    help='How far back to collect data, use instead of start and end '\
        '(options: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max), default:1mo')
parser.add_argument('-v', '--verbose', action='store_true', help='Be verbose')
args = parser.parse_args()
global VERBOSE


def validate_args():
    if (args.start and not args.end):
        parser.error('ERROR: You must specify an end date with --end, '\
            'or use --period.')
    elif (args.end and not args.start):
        parser.error('ERROR: You must specify a start date with --start, '\
            'or use --period.')
    elif (args.start and args.end):
        if (args.start > args.end):
            parser.error(f'ERROR: '\
                'Your start date: {args.start} is after your end date: {args.end}')
        else:
            date_range = (args.start, args.end)
    elif (args.period):
        if args.period not in ['1d', '5d', '1mo', '3mo', '6mo', '1y', '5y', '10y', 'ytd', 'max']:
            parser.error('ERROR: period must be '\
                f'1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max, got {args.period}.')
        date_range = args.period
    else:
        date_range = '1mo' # DEFAULT

    return date_range


def collect_symbols(offset=None):
    data = pd.read_csv('https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt', sep='|')
    data_clean = data[data['Test Issue'] == 'N']
    symbols = data_clean['NASDAQ Symbol'].tolist()
    names = data_clean['Security Name'].tolist()
    with open('data/symbols_names.csv', 'w') as f:
        for pair in zip(symbols, names):
            f.write(f'{pair[0]}, {pair[1]}\n')

    if offset:
        symbols = symbols[offset::]

    if VERBOSE:
        print(f'Total number of symbols: {len(symbols)}')

    return symbols


def collect_data(symbols, date_range):
    if (type(date_range) == tuple):
        start, end = date_range
        if VERBOSE:
            print(f'Collecting data from {start} to {end}')
        for symbol in symbols:
            try:
                data = yf.download(symbol, start=start, end=end)

                data.to_csv(f'data/stock_data/{symbol}.csv')
            except:
                print(f'Symbol {symbol} appears to be broken, ignoring')
                continue
    else:
        if VERBOSE:
            print(f'Collecting data over a period of {date_range}')
        for symbol in symbols:
            try:
                data = yf.download(symbol, period=date_range)

                data.to_csv(f'data/stock_data/{symbol}.csv')
            except:
                print(f'Symbol: {symbol} appears to be broken, ignoring')
                continue


if __name__ == '__main__':
    VERBOSE = args.verbose

    date_range = validate_args()

    symbols = collect_symbols()
    #collect_data(symbols, date_range)
