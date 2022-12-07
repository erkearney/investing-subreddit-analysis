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
args = parser.parse_args()


def score_sentence(sentence):
    '''
    Uses VADER to determine whether the given sentence is positive, negative,
    or neutral

    Parameters
    ----------
    sentence : str
        The sentence to be analyzed

    Returns
    -------
    score: dict<str : float>
        The results of the sentiment analysis taking the form of
        {<sentiment} : <score>}
        (ex: {'neg': 0.0, 'neu': 1.0, 'pos': 0.0})
    '''
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(sentence)
    score.pop('compound') # VADER adds a compound score which we don't need
    return score


def analyze_data(data):
    '''
    Calls score_sentence on all sentences in data

    Paramters
    ---------
    data : str
        The file path to the csv file to be analyzed

    Attributes
    ----------
    scores : List<dict<sentiment, score>>
        List of scores for each sentence
        (ex: {"pos" : 0.0, "neu" : 1.0, "neg" : 0.0})

    Outputs
    -------
    pandas.core.frame.DataFrame -> csv file
        Dataframe with a new column, sentiment_score, written out to
        scored_reddit.csv
    '''
    data = pd.read_csv(data)
    if args.debug:
        data = data.head(1000)

    data_size = len(data)
    scores = [defaultdict()] * data_size
    for i in range(data_size):
        sentence = f'{data.loc[i, "title"]} {str(data.loc[i, "body"])}'
        scores[i] = score_sentence(sentence)

    data.assign(sentiment_score=scores).to_csv('data/scored_reddit.csv')


if __name__ == '__main__':
    analyze_data('data/clean_reddit.csv')
