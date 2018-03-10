from __future__ import print_function

import rsi2
from pyalgotrade import plotter
from pyalgotrade.tools import yahoofinance
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import returns
import pandas as pd


def main(plot):
    instrument = "lpyl"
    entrySMA =56 
    exitSMA = 8
    rsiPeriod = 2
    overBoughtThreshold =75 
    overSoldThreshold = 17

    # Load the bars. These files were manually downloaded from Yahoo Finance.
#    feed = yahoofeed.Feed()
#    for year in range(2009, 2013):
#        fileName = "%s-%d-yahoofinance.csv" % (instrument, year)
#        print("Loading bars from %s" % fileName)
#        feed.addBarsFromCSV(instrument, fileName)

    # Download the bars.
    #feed = yahoofinance.build_feed([instrument], 2009, 2012, ".")
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("lpyl", "lpyl.csv")
    strat = rsi2.RSI2(feed, instrument, entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)
    plot=True

    if plot:
        plt = plotter.StrategyPlotter(strat, True, True,False)
        plt.getInstrumentSubplot(instrument).addDataSeries("Entry SMA", strat.getEntrySMA())
        plt.getInstrumentSubplot(instrument).addDataSeries("Exit SMA", strat.getExitSMA())
        plt.getOrCreateSubplot("rsi").addDataSeries("RSI", strat.getRSI())
        plt.getOrCreateSubplot("rsi").addLine("Overbought", overBoughtThreshold)
        plt.getOrCreateSubplot("rsi").addLine("Oversold", overSoldThreshold)
        

    strat.run()
    print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)
    strat.info("Final portfolio value: $%.2f" % strat.getResult())
    from datetime import datetime

    if plot:
        plt.plot(fromDateTime=datetime.strptime('2017-07-01','%Y-%m-%d'),toDateTime=datetime.strptime('2018-03-01','%Y-%m-%d'))


if __name__ == "__main__":
    main(True)
