# Import Algorithm API
import quantopian.algorithm as algo
import quantopian.optimize as opt

# Pipeline imports for stocktwits
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.psychsignal import stocktwits
from quantopian.pipeline.factors import SimpleMovingAverage

# Pipeline imports for mean-reversion
from quantopian.pipeline.factors import Returns
from quantopian.pipeline.data.builtin import USEquityPricing

# Import built-in universe and Risk API method
from quantopian.pipeline.filters import QTradableStocksUS

# Define returns window length used by the Returns factor to rank stocks
RETURNS_LOOKBACK_DAYS = 5

def initialize(context):
    # Define constraint parameters
    context.max_leverage = 1.0
    context.max_pos_size = 0.015
    context.max_turnover = 0.95

    # Attach data pipeline
    algo.attach_pipeline(
        make_pipeline(),
        'data_pipe'
    )

    # Schedule rebalance function, called when the market opens on the first     # trading day of each week
    algo.schedule_function(
        rebalance,
        algo.date_rules.week_start(),
        algo.time_rules.market_open(),
    )


def before_trading_start(context, data):
    # Get pipeline outputs and store them in context
    context.pipeline_data = algo.pipeline_output('data_pipe')

    
def make_pipeline():
    # Create sentiment_score factor based on data from the StockTwits API
    # Uses a simple moving average of the past three days for all 
    # securities in the QTradableStocksUS Filter.
    sentiment_score = SimpleMovingAverage(
        inputs=[stocktwits.bull_minus_bear],
        window_length=3,
        mask=QTradableStocksUS()
    )
    
    # Creates a returns factor with a 5-day lookback window for all   
    # securities in the QTradableStocksUS Filter.
    recent_returns = Returns(
        window_length=RETURNS_LOOKBACK_DAYS, 
        mask=QTradableStocksUS()
    )
    
    # Combination of both factors using a weighted z.score to normalize 
    # results
    combined_factor = (
        sentiment_score.zscore() * 0.65 - recent_returns.zscore() * 0.35
    )
    
    # Create a filter such that only securities at the low and high end 
    # of the combined factor are kept
    low_combined_factors = combined_factor.percentile_between(0,10)
    high_combined_factors = combined_factor.percentile_between(90,100)
    securities_to_trade = (low_combined_factors | high_combined_factors)

    return Pipeline(
        columns={
            'combined_factor': combined_factor
        },
        screen=securities_to_trade
    )


def rebalance(context, data):
    # Define alpha as the negative of our pipeline_data.combined_factor
    alpha = context.pipeline_data.combined_factor

    # Define the objective as to maximise alpha
    objective = opt.MaximizeAlpha(alpha)
    
    # Constrtain our portfolio to invest a maximum amount of money
    # in any given position, defined as +/- MAX_POSITION_CONCENTRATION
    constrain_pos_size = opt.PositionConcentration.with_equal_bounds(
        -context.max_pos_size,
        context.max_pos_size
    )

    # Constrain our portfolio's max leverage
    max_leverage = opt.MaxGrossExposure(context.max_leverage)

    # Constrain our portfolio to be dollar neutral (equal amounts 
    # invested in long and short positions)
    dollar_neutral = opt.DollarNeutral()

    # Constrain portfolio turnover
    max_turnover = opt.MaxTurnover(context.max_turnover)

    # Rebalance portfolio using objective and list of constraints
    algo.order_optimal_portfolio(
        objective=objective,
        constraints=[
            constrain_pos_size,
            max_leverage,
            dollar_neutral,
            max_turnover
        ]
        )
