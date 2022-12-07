'''
Uses the Valence Aware Dictionary and sEntiment Reasoner (VADER)[1] project
(https://github.com/Holek/vader_sentiment) to determine whether a Reddit post
is positive or negative.

[1] Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for
Sentiment Analysis of Social Media Text. Eighth International Conference on
Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.
'''

import argparse
from collections import defaultdict

import pandas as pd

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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


class SentimentAnalyzer():
    '''
    Attributes
    ----------
    analyzer : vaderSentiment.SentimentIntensityAnalyzer
    (https://github.com/Holek/vader_sentiment)
        The VADER analyzer object
    '''

    def __init__(self, data):
        self.data = read_in_data(data)
        self.analyzer = SentimentIntensityAnalyzer()


    def score_sentence(self, sentence):
        '''
        Uses VADER to determine whether the given sentence is positive, negative,
        or neutral

        Parameters
        ----------
        sentence : str
            The sentence to be analyzed

        Returns
        -------
        dict<str : float>
            The results of the sentiment analysis taking the form of
            {<sentiment} : <score>}
            (ex: {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0})
        '''
        return self.analyzer.polarity_scores(sentence)


    def analyze_data(self):
        '''
        Calls self.score_sentence on all sentences in self.data

        Modifies
        --------
        self.data : pandas.core.frame.DataFrame
            Appends a new column, sentiment_score to the data
        '''
        if args.debug:
            self.data = self.data.head(10)

        scores = [defaultdict()] * len(self.data)
        for i in range(len(self.data)):
            sentence = f'{self.data.loc[i, "title"]} {str(self.data.loc[i, "body"])}'
            scores[i] = self.score_sentence(sentence)

            if args.verbose:
                if i % 10 == 0:
                    print(f'{sentence} scored {scores[i]}')

        self.data = self.data.assign(sentiment_score=scores)


if __name__ == '__main__':
    sentiment_analyzer = SentimentAnalyzer('data/clean_reddit.csv')
    sentiment_analyzer.analyze_data()
