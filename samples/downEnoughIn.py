from pyalgotrade import strategy
from pyalgotrade.technical import cross
from pyalgotrade.broker import backtesting
from pyalgotrade import broker
from pyalgotrade import plotter
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.technical import roc
from pyalgotrade.technical import ma
import pandas as pd
import datetime
from pyalgotrade.technical import cross

DEBUG = True


class DownEnoughIn(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, window=3):
        commission = backtesting.TradePercentage(0.0025)
        broker = backtesting.Broker(1000000, feed, commission)
        broker.getFillStrategy().setVolumeLimit(None)
        super(DownEnoughIn, self).__init__(feed, broker)
        self.__instrument = instrument
        # We'll use adjusted close values, if available, instead of regular close values.
        if feed.barsHaveAdjClose():
            self.setUseAdjustedValues(True)
        self.__priceDS = feed[instrument].getPriceDataSeries()
        self.__refDS =  ma.SMA(feed[instrument].getPriceDataSeries(), 5)
        self.__pricePCT = roc.RateOfChange(self.__priceDS, 1).getValues()
        self.__longPos = None
        self.__window = window
        self.__enter = False
        self.__downCount = -1
        self.__enterTime = None

    def onEnterCanceled(self, position):
        if self.__longPos == position:
            self.__longPos = None
        else:
            assert (False)

    def print_transactions(self, action, execInfo):
        if action == broker.Order.Action.BUY:
            self.info("BUY at $%.2f" % (execInfo.getPrice()) +
                      " shares: " + str((execInfo.getQuantity())) + ' on ' + execInfo.getDateTime().strftime("%Y%m%d"))
        elif action == broker.Order.Action.BUY_TO_COVER:
            self.info("BUY_TO_COVER at $%.2f" % (execInfo.getPrice()) +
                      " shares: " + str((execInfo.getQuantity())) + ' on ' + execInfo.getDateTime().strftime(
                "%Y%m%d"))
        elif action == broker.Order.Action.SELL:
            self.info("SELL at $%.2f" % (execInfo.getPrice()) +
                      " shares:" + str((execInfo.getQuantity())) + ' on ' + execInfo.getDateTime().strftime("%Y%m%d"))
        elif action == broker.Order.Action.SELL_SHORT:
            self.info("SELL_SHORT at $%.2f" % (execInfo.getPrice()) +
                      " shares:" + str((execInfo.getQuantity())) + ' on ' + execInfo.getDateTime().strftime(
                "%Y%m%d"))

    def onEnterOk(self, position):
        order = position.getEntryOrder()
        execInfo = order.getExecutionInfo()
        action = order.getAction()
        self.__enterTime = execInfo.getDateTime()
        if DEBUG:
            self.print_transactions(action, execInfo)

    def onExitOk(self, position):
        if self.__longPos == position:
            self.__longPos = None
        else:
            assert (False)
        order = position.getExitOrder()
        execInfo = order.getExecutionInfo()
        action = order.getAction()
        self.__enterTime = None
        if DEBUG:
            self.print_transactions(action, execInfo)

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        position.exitMarket()

    def getRefSMA(self):
        return self.__refDS

    def onBars(self, bars):
        # Wait for enough bars to be available for specified observations
        if len(self.__pricePCT) < (self.__window + 1):
            return
        priceS = pd.Series(self.__pricePCT)[(-self.__window):]
        # self.__pricePCT = pd.Series(feed[instrument].getPriceDataSeries().getValues()).pct_change()
        self.__downCount = priceS[priceS < 0].count()
        self.__pdPrice = pd.Series(self.__priceDS.getValues(), self.__priceDS.getDateTimes())
        bar = bars[self.__instrument]
        # if self.__longPos is not None and bar.getDateTime() != self.__enterTime:
        if self.__longPos is not None and self.exitLongSignal(bar):
            self.__longPos.exitMarket()
            if DEBUG:
                print("exit long position: ", self.__longPos.getShares(), " on ",
                      bar.getDateTime().strftime('%Y%m%d'), ' at  price: ', str(bar.getPrice()))
        else:
            if self.__longPos is None and self.enterLongSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__longPos = self.enterLong(self.__instrument, shares, True)
                if DEBUG:
                    print("enter long shares: ", shares, " on ", bar.getDateTime().strftime('%Y%m%d'),
                          ' at  price: ', str(bar.getPrice()), ' volume: ', str(bar.getVolume()))

    def enterLongSignal(self, bar):
        return self.__downCount == self.__window

    def exitLongSignal(self, bar):
        # current = bar.getPrice()
        # pivotal = self.__pdPrice[self.__enterTime:].max()
        # limit = (pivotal - current) / pivotal >= 0.06
        # enter = self.__pdPrice[self.__enterTime]
        # stop = (enter - current) / enter >= 0.03
        # return stop | limit
        return cross.cross_below(self.__priceDS,self.__refDS)

feed = yahoofeed.Feed()
instrument = "whole_2018"
feed.addBarsFromCSV(instrument, instrument+".csv")
strat = DownEnoughIn(feed, instrument, 5)
sharpeRatioAnalyzer = sharpe.SharpeRatio()
strat.attachAnalyzer(sharpeRatioAnalyzer)
plot = True

if plot:
    plt = plotter.StrategyPlotter(strat, True, True, False)
    plt.getInstrumentSubplot(instrument).addDataSeries("pri", strat.getRefSMA())

strat.run()
print("Sharpe ratio: %.2f", '%', sharpeRatioAnalyzer.getSharpeRatio(0.05))
strat.info("Final portfolio value: $%.2f" % strat.getResult())
from datetime import datetime

if plot:
    plt.plot(fromDateTime=datetime.strptime('2018-05-01', '%Y-%m-%d'),
             toDateTime=datetime.strptime('2018-07-01', '%Y-%m-%d'))
