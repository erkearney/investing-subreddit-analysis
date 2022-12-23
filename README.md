# Investing Subreddit Analysis
### This is a small project to analyze the sentiments and performance of investing related subreddits, this served as final project for CS-542 - Natural Language Processing, at Colorado State University.

Installation and Use:
- Run the following commands
    
    ```
    git clone https://github.com/erkearney/investing-subreddit-analysis
    pip install requirements.txt
    cd investing-subreddit-analysis
    python3 collect_stock_data.py -s 2019-04-27 -e 2021-01-27
    ```

- Donwnloading the historic stock data will take quite a while, so download the [Reddit comment data](https://www.kaggle.com/datasets/yorkehead/stock-market-subreddits), put it into the data folder, and go get some coffee. Once the download has finished run the following commands:

    ```
    python3 clean_reddit_data.py
    python3 sentiment_analyzer.py
    python3 compare_results.py
    ```

### Errors
While developing this project, it became clear that there are many errors
currently embedded within it. Resolving these errors will require a great
deal of time and effort, and I do have to turn in \textbf{something}. I
hope to continue work on this as a personal project after class ends. Here
are the errors I am currently aware of:

- The pre-processing currently only looks for NASDAQ symbols
within the text, not for company names. For example, a post that
contains 'AAPL' will be correctly flagged as discussing Apple, Inc.,
however a post containing 'Apple' will not. This means that not all
the companies being discussed are being correctly 'bought' in the
simulation, and that companies with names that are commonly
abbreviated to their NASDAQ symbols, such as 'GME', will be
overrepresented in the simulation compared to companies that are
often fully spelled out when discussed online.
- Some companies have NASDAQ symbols that happen to be equivalent
to common words, most apparently is Agilent Technologies Inc.,
which has the NASDAQ symbol 'A'. This means that stocks were being
'bought' when they shouldn't have been. The subreddit hurt most by
this error was clearly r/wallstreet bets. Whose portfolio was
comprised almost entirely of 'YOLO', which is the AdvisorShares
Pure Cannabis ETF. It is clear from the context of the comments
that the intention behind saying 'YOLO' was almost always
as the acronym "You Only Live Once". An example comment containing
"YOLO" from r/wallstreetbets:

"Keynes said we're all dead in the long run, I think he meant
always YOLO"*
- Another issue that particularly hurt r/wallstreetbets were
sentiment mis-identifications. For example the post:

"CLASS ACTION AGAINST ROBINHOOD. Allowing people to only sell is
the definition of market manipulation. A class action must be
started, Robinhood has made plenty of money off selling info about
our trades to the hedge funds to be able to pay out a little for
causing people to loose money now","LEAVE ROBINHOOD. They dont
deserve to make money off us after the millions they caused in
losses. It might take a couple of days, but send Robinhood to the
ground and GME to the moon."*

Scored a negative sentiment for GME. While this appears to be
correct as in the sentiment of the statement itself is negative,
that negativity is not intended to be directed towards GME. As a
matter of fact, a great deal of the discussion on r/wallstreetbets
was targeted towards this Robinhood class action lawsuit, and
similar lawsuits. The end result of this was that r/wallstreetbets
bought almost no shares of GME, which is the community's stock of
choice.
- Subreddits were allowed to buy or sell no more than one share of
each company a day. A better simulation probably would allow for
the purchase of numerous shares of a stock if the subreddit's
sentiment towards that company was extremely positive, and
conversely, allow for the sale of numerous shares if the sentiment
were extremely negative.
- Clearly, more data from each subreddit, as well as model trained
on the text of the subreddits themselves would've improved
accuracy.

*I unfortunately cannot quote the users as their
usernames were not included in the dataset.


### Limitations
It should be made explicitly clear to anyone who wishes to work on a
project like this, make a similar project, or base their financial
decisions based on a project like this that it is incredibly easy to
manipulate the results. Almost any portfolio can be made to look
incredible if one is willing to cherry pick the dates. I personally would
under no circumstances recommend that anyone invest money based on the
advice of strangers on the Internet, without thoroughly doing their own
research. It may be tempting to start following r/stocks now and just
invest in whatever the users there seem to be buying, but it should
always be stated again and again that past performance does not indicative
of future results.
