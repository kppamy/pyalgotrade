from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi
from pyalgotrade.technical import cross
from pyalgotrade.broker import backtesting
from pyalgotrade import broker

DEBUG = False
class RSI2(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold):
        commission=backtesting.TradePercentage(0.0025)
        broker = backtesting.Broker(1000000, feed,commission)
        super(RSI2, self).__init__(feed,broker)
        #super(RSI2, self).__init__(feed)
        self.__instrument = instrument
        # We'll use adjusted close values, if available, instead of regular close values.
        if feed.barsHaveAdjClose():
            self.setUseAdjustedValues(True)
        self.__priceDS = feed[instrument].getPriceDataSeries()
        self.__entrySMA = ma.SMA(self.__priceDS, entrySMA)
        self.__exitSMA = ma.SMA(self.__priceDS, exitSMA)
        self.__rsi = rsi.RSI(self.__priceDS, rsiPeriod)
        self.__overBoughtThreshold = overBoughtThreshold
        self.__overSoldThreshold = overSoldThreshold
        self.__longPos = None
        self.__shortPos = None

    def getEntrySMA(self):
        return self.__entrySMA

    def getExitSMA(self):
        return self.__exitSMA

    def getRSI(self):
        return self.__rsi

    def onEnterCanceled(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

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
        if DEBUG:
            self.print_transactions(action, execInfo)

    def onExitOk(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)
        order = position.getEntryOrder()
        execInfo = order.getExecutionInfo()
        action = order.getAction()
        if DEBUG:
            self.print_transactions(action, execInfo)

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate SMA and RSI.
        if self.__exitSMA[-1] is None or self.__entrySMA[-1] is None or self.__rsi[-1] is None:
            return
        bar = bars[self.__instrument]
        if self.__longPos is not None:
            if self.exitLongSignal(bar):
                self.__longPos.exitMarket()
                if DEBUG:
                    print("exit long position: ",  self.__longPos.getShares(), " on ",
                          bar.getDateTime().strftime('%Y%m%d') , ' at  price: ', str(bar.getPrice()))
        elif self.__shortPos is not None:
            if self.exitShortSignal():
                self.__shortPos.exitMarket()
                if DEBUG:
                    print("exit short position ",  self.__shortPos.getShares(), " on ",
                          bar.getDateTime().strftime('%Y%m%d'), ' at  price: ', str(bar.getPrice()))
        else:
            if self.enterLongSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__longPos = self.enterLong(self.__instrument, shares, True)
                if DEBUG:
                    print("enter long shares: ", shares, " on ", bar.getDateTime().strftime('%Y%m%d'),
                          ' at  price: ', str(bar.getPrice()), ' volume: ', str(bar.getVolume()))
            elif self.enterShortSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__shortPos = self.enterShort(self.__instrument, shares, True)
                if DEBUG:
                    print("enter short shares: ", shares, " on ", bar.getDateTime().strftime('%Y%m%d'),
                          ' at  price: ', str(bar.getPrice()),' volume: ', str(bar.getVolume()))

    def enterLongSignal(self, bar):
        return bar.getPrice() > self.__entrySMA[-1] and self.__rsi[-1] <= self.__overSoldThreshold

    def exitLongSignal(self,bar):
        return bar.getPrice() > self.__exitSMA[-1] and self.__rsi[-1] >= self.__overBoughtThreshold and not self.__longPos.exitActive()
        #return cross.cross_above(self.__priceDS, self.__exitSMA) and not self.__longPos.exitActive()

    def enterShortSignal(self, bar):
        return bar.getPrice() < self.__entrySMA[-1] and self.__rsi[-1] >= self.__overBoughtThreshold

    def exitShortSignal(self):
        return cross.cross_below(self.__priceDS, self.__exitSMA) and not self.__shortPos.exitActive()
