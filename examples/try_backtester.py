from os.path import abspath, join, pardir
import sys
sys.path.append(abspath(join(abspath(__file__), pardir, pardir)))

# Import all Created exchanges here
from pyjuque.Exchanges.Binance import Binance
from pyjuque.Exchanges.CcxtExchange import CcxtExchange
from pandas import DataFrame

from pyjuque.Strategies.BBRSIStrategy import BBRSIStrategy
from pyjuque.Engine.Backtester import backtest
from pyjuque.Plotting.Plotter import PlotData
from pyjuque.Utils import dotdict

from pprint import pprint

entry_strategy:dotdict = dotdict(dict(
    strategy_class = BBRSIStrategy,
    args = (13, 40, 70, 30),
))

entry_settings:dotdict = dotdict(dict(
    # subsequent entries
    se = dotdict(dict(
        times = 0,
        after_profit = 0.99,
        pt_decrease = 0.998,
    ))
))

exit_settings:dotdict = dotdict(dict(
    pt = 1.045,
    # trailing stop loss
    tsl = dotdict(dict(
        value = 0.99,
        after_profit = 1.015
    )),
    # stop loss
    sl = 0.9
))

def Main():
    # Initialize exchanges and test
    exchange = CcxtExchange('binance')
    
    # symbol = "ZILBTC"
    # symbol = "XRPBTC"
    symbol = "BTCUSDT"
    interval = "1m"
    df = exchange.getOHLCV(symbol, interval, limit=1000)
    
    strategy = entry_strategy.strategy_class(*entry_strategy.args)
    strategy.setUp(df)
    # pprint(strategy.df)
    results = backtest(df, symbol, exchange, entry_strategy, entry_settings, exit_settings)

    print("P\L: {}".format(results["total_profit_loss"]))

    signals=[
        dict(points=results['buy_times'], name="buy_times"),
        dict(points=results['tp_sell_times'], name="tp_sell_times"),
        dict(points=results['sl_sell_times'], name="sl_sell_times"),
        dict(points=results['tsl_sell_times'], name="tsl_sell_times"),
        dict(points=results['tsl_active_times'], name="tsl_active_times"),
        dict(points=results['tsl_increase_times'], name="tsl_increase_times")]

    plot_indicators = []
    for indicator in strategy.indicators:
        yaxis = 'y'
        if indicator['indicator_name'] == 'rsi':
            yaxis = 'y3'
        plot_indicators.append(dict(name=indicator['indicator_name'], title=indicator['indicator_name'], yaxis=yaxis))

    PlotData(df, 
    add_candles=True, 
    signals=signals, 
    plot_indicators=plot_indicators,
    # plot_title=symbol,
    save_plot=True, 
    plot_title="backtest_"+symbol.lower() + "_" + interval, 
    show_plot=False
    # plot_shapes=lines,
    )

if __name__ == '__main__':
    Main()