'''
Uses the Valence Aware Dictionary and sEntiment Reasoner (VADER) project
(https://github.com/Holek/vader_sentiment) to determine whether a Reddit post
is positive or negative.
'''

import pandas as pd

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class Sentiment_Analyzer():
    def __init__(self, data):
        self.data = self.read_in_data(data)


    def read_in_data(self, data):
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


    def score_sentence(self, sentence):
        '''
        Uses VADER to determine whether the given sentence is positive, negative,
        or neutral

        Parameters
        ----------
        sentence : str
            The sentence to be analyzed

        Attributes
        ----------
        analyzer : vaderSentiment.SentimentIntensityAnalyzer
        (https://github.com/Holek/vader_sentiment)
            The VADER analyzer object

        score : dict<str : float>
            The results of the sentiment analysis taking the form of
            {<sentiment} : <score>}
            (ex: {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0})
        '''
        analyzer = SentimentIntensityAnalyzer()
        score = analyzer.polarity_scores(sentence)
        print(score)

        print(f'{sentence}: {str(score)}')


    def analyze_data(self):
        '''
        Calls self.score_sentence on all sentences in self.data

        Modifies
        --------
        self.scores
        '''
        # For debugging purposes, reduce the dataframe size to improve runtime
        self.data = self.data.head(10)

        for i in range(len(self.data)):
            #print(f'{self.data.loc[i, "title"]} {str(self.data.loc[i, "body"])}')
            sentence = self.data.loc[i, 'title'] + str(self.data.loc[i, 'body'])
            print(self.score_sentence(sentence))


if __name__ == '__main__':
    sentiment_analyzer = Sentiment_Analyzer('data/clean_reddit.csv')
    sentiment_analyzer.analyze_data()
