from pyalgotrade import strategy
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades
from pyalgotrade import plotter 
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.technical import roc
from pandas import DataFrame
import pandas as pd


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed,dataframe, instrument, smaPeriod,vsmaPeriod):
        super(MyStrategy, self).__init__(feed, 1000)
        self.__position = None
        self.__instrument = instrument
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(True)
        self.__prices=feed[instrument].getPriceDataSeries()
        self.__sma = ma.SMA(self.__prices, smaPeriod)
        self.__vsma = ma.SMA(feed[instrument].getVolumeDataSeries(),vsmaPeriod)
        self.convertDataFrame(dataframe)
        self.roc=roc.RateOfChange(self.__prices,1)

    def convertDataFrame(self,dataframe):
        dataframe.Date=pd.to_datetime(dataframe.Date)
        dataframe=dataframe.set_index('Date')
        dataframe=dataframe.sort_index()
        self.dataframe=dataframe

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]
        cur=bar.getPrice()
        prcs=self.__prices
        pre=self.__prices[-2]
        print('pre:  '+str(pre)+' cur: '+str(cur))
        print('roc: \n'+self.roc[-1])
        vol=bar.getVolume()
        vols=self.__vsma
        prevol=self.__vsma[-2]
        print('prev:  '+str(prevol)+' curv: '+str(vol))
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if cur < self.__sma[-1]*0.9 and vol >prevol*2 and self.roc[-1]>0: 
                # Enter a buy market order for 10 shares. The order is good till canceled.
                print('pre:  '+str(pre)+' cur: '+str(cur))
                print('prev:  '+str(prevol)+' curv: '+str(vol))
                self.__position = self.enterLong(self.__instrument, 10, True)
        # Check if we have to exit the position.
        elif bar.getPrice() > self.__sma[-1]*1.1 and not self.__position.exitActive():
            self.__position.exitMarket()


def run_strategy(smaPeriod,vsmaPeriod):
    # Load the yahoo feed from the CSV file
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("orcl", "njyh.csv")
    df=DataFrame.from_csv('njyh.csv')

    myStrategy = MyStrategy(feed,df,"orcl", smaPeriod,vsmaPeriod)
    # Evaluate the strategy with the feed.
    # Attach a returns analyzers to the strategy.
    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    myStrategy.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    myStrategy.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    myStrategy.attachAnalyzer(tradesAnalyzer)

    # Attach the plotter to the strategy.
    plt = plotter.StrategyPlotter(myStrategy,plotPortfolio=False)
    # Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
    plt.getInstrumentSubplot("orcl").addDataSeries("SMAH", myStrategy._MyStrategy__sma)
    # Plot the simple returns on each bar.
    plt.getOrCreateSubplot("orcl").addDataSeries("daily",myStrategy._MyStrategy__prices)
    plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getCumulativeReturns())
    plt.getOrCreateSubplot("returns").addDataSeries("sharp", sharpeRatioAnalyzer.getReturns())

    # Run the strategy.
    myStrategy.run()
    myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())
    plt.plot()

    ## Plot the strategy.
    #myStrategy = MyStrategy(feed, "orcl", smaPeriod)
    #myStrategy.run()
    #print "Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity()

run_strategy(51,6)
