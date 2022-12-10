import pandas as pd

import matplotlib.pyplot as plt

wallstreetbets = pd.read_csv('data/results/wallstreetbets_p_value.csv')
stocks = pd.read_csv('data/results/stocks_p_value.csv')
investing = pd.read_csv('data/results/investing_p_value.csv')

dates = wallstreetbets['Unnamed: 0']
df = pd.DataFrame()
df['date'] = dates
df['stocks'] = stocks['0']
df['investing'] = investing['0']
df['wallstreetbets'] = wallstreetbets['0']

plt.plot(df['date'], df['stocks'], label = 'r/stocks', linestyle='-')
plt.plot(df['date'], df['investing'], label = 'r/investing')
plt.plot(df['date'], df['wallstreetbets'], label = 'r/wallstreetbets')
plt.xlabel('date')
plt.ylabel('portfolio value')
plt.show()
