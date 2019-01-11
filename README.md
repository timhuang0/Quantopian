# Quantopian
Developing basic trading algorithms using the Quantopian API.

I wrote this program to learn how quantitive trading algorithms work and the basics of the Quantopian API. Quantopian is a platform that provides freelance analysts the tools, education, and datasets necessary to develop algorithmically constructed securities portfolios. Though the algorithm I designed was relatively simple, I learned how to implement fundamental quantitative trading concepts such as data pipelines, risk analysis, and backtesting.  

All of the code is written using Python, though the easiest way to view the code and run a sample backtest is by cloning the algorithm.

# Mean Reversion and Stocktwits Weighted Strategy

I developed an trading algorithm which would create an optimal portfolio based on two factors: mean-reversion and public sentiment based on data from stocktwits.com. The program would then normalize both factors using a z-score and take a weighted average of both factors to create the combined factor.

### Mean Reversion

Mean reversion is the concept that securities will tend to return to their long-term averages (i.e. that short-term overperforming stocks will tend to lose value and vice versa). I created a simple mean reversion implementation by importing the USEquityPricing data builtin and creating a recent returns factor with a 5-day lookback window. 

### Stocktwits

I created a public sentiment factor through importing data from the stocktwits API. On stocktwits.com, traders can indicate that they are "bullish" or "bearish" on a given stock. I measured public sentiment as the number of "bullish" labels subtracted by the "bearish" labels a stock received. This was tracked with a window length of three days and normalized using a Simple Moving Average.

### Portfolio Construction

After creating a combined factor, I created a filter such that only securities in the top 10% and bottom 10% of the combined factor distribution would be considered. This is to ensure that the algorithm can only buy/short securities that it is definitive about. Additionally, the portfolio is limited by a maximum position size, maximum leverage, maximum turnover, and must be dollar neutral.
