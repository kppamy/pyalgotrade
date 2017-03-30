#!/usr/bin/env python
# coding=utf-8
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.broker import backtesting
from pyalgotrade.barfeed import yahoofeed

threshold = 0.8;
PtsPctATR = 2; #{0=Points, 1=Precent, 2=ATR}
tradetrends = 1; #{0=trends and reactions, 1=trends only}
#{self.state = 0 self.upTrend }
#{self.state = 1 self.dnTrend }
#{self.state = 2 NatRally}
#{self.state = 3 SecRally}
#{self.state = 4 NatReact}
#{self.state = 5 SecReact}

def addCommentary(comment):
    print(comment)

if (PtsPctATR == 0):
    Thresh = threshold;
    HalfThresh = Thresh/2;
else:
    Thresh = threshold;
    HalfThresh = Thresh/2;
    addCommentary('******HalfThresh******'+str(HalfThresh))

class JLV(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument,window):
        self.priceDS = feed[instrument].getPriceDataSeries()
        self.MA10_Now = ma.SMA(self.priceDS,window)
        self.instrument=instrument
        commission=backtesting.TradePercentage(0.0025)
        broker = backtesting.Broker(1000000, feed,commission)
        self.lastposition=None
        self.__longPos=None
        self.__shortPos=None
        super(JLV, self).__init__(feed,broker)

    def onBars(self, bars):
        bar=bars[self.instrument]
        lth=len(self.priceDS)
        self.close=bar.getPrice()
        if lth ==21:
            self.initStrate()
            if self.MA10_Now[-1] > self.MA10_Now[-11] :
                addCommentary('InUpTrend '+str(bar.getDateTime()));
                self.state = 0;
                self.upTrend = self.close;
            else :
                addCommentary('InDnTrend '+str(bar.getDateTime()));
                self.dnTrend = self.close;
                self.state = 1;
        elif lth>21:
            self.mainLoop(bars)
            self.handleTrade(bars)

    def initStrate(self):
        addCommentary('Init');
        self.secondaryRally = self.close;
        self.natRally = self.close;
        self.natRallyBL=self.close;
        self.upTrend = self.close;
        self.secondaryReaction = self.close;
        self.naturalReaction = self.close;
        self.dnTrend = self.close;
        self.dnTrendBL =self.close;
        self.resumeUT = False;
        self.resumeDnTrend = False;

    def mainLoop(self,bars):
        if self.state == 0:
            self.handleUpTrend(bars);
        elif self.state == 1:
            self.handleDnTrend(bars);
        elif self.state == 2:
            self.handleNaturalRally(bars);
        elif self.state == 3:
            self.handleSecondRally(bars);
        elif self.state == 4:
            self.handleNaturalReaction(bars);
        elif self.state == 5:
            self.handleSecondReaction(bars);

    def resumeUpTrend(self):
        #begin {6}
        if (self.close > (self.upTrendRL + HalfThresh)) :
            self.resumeUT = False; #{Rule 10a}
            self.state = 4; #{InNatReact}
            self.naturalReaction = self.close;
            self.upTrend = self.close;
        elif (self.close < (self.upTrendRL - HalfThresh)) :
            self.resumeUT = False; #{Rule 10b}
            self.state = 4; #{InNatReact}
            self.naturalReaction = self.close;

    def handleUpTrend(self,bars):
        bar=bars[self.instrument]
        #begin {4}
        if (self.close > (self.naturalReaction + Thresh)) :
            self.naturalReactionRL = self.naturalReaction; #{Rule 4b}
            addCommentary('InUpTrend '+str(bar.getDateTime()));
            if self.resumeUT : #{ Rule 10 logic. }
               self.resumeUpTrend()
        elif (self.close < (self.upTrend - Thresh)) : #{start self.naturalReaction}
            #begin {Rules 4a, 6a}
            self.state = 4; #{InNatReact}
            addCommentary('InNatReact'+str(bar.getDateTime()));
            self.upTrendRL = self.upTrend #{pivot point, rule 8}
            self.naturalReaction = self.close;
            self.resumeUT = False;
        elif (self.close > self.upTrend) : #{Remain in self.upTrend higher high price}
            self.upTrend = self.close;
         #{4  InUpTrend}

    def resumeDnTrendProcess(self,bars):
        bar=bars[self.instrument]
        if (self.close < (self.dnTrendBL - HalfThresh)) :
            self.resumeDnTrend = False; #{Rule 10a}
            self.dnTrend =  self.close; #{Rule 2, 6b}
        elif (self.close > (self.dnTrendBL + HalfThresh)) : #{self.dnTrend Over}
            #{return to self.natRally}
            addCommentary('return to self.natRally'+str(bar.getDateTime()));
            self.resumeDnTrend = False;
            self.state = 2; #{InNatRally}
            self.natRally = self.close;

    def handleDnTrend(self,bars):
        bar=bars[self.instrument]
        #begin {9}
        if (self.close < (self.natRally - Thresh)) :
            self.natRallyBL = self.natRally; #{Rule 4d}
            if self.resumeDnTrend : #{Rule 10 logic best works with futures}
               self.resumeDnTrendProcess(bars)
        elif (self.close > (self.dnTrend + Thresh))  :  #{start self.natRally}
            #begin  { rules 4c, 6c}
            addCommentary('return to self.natRally'+str(bar.getDateTime()));
            self.state = 2; #{InNatRally}
            self.natRally = self.close;
            self.dnTrendBL = self.dnTrend #{Pivot Pt, Rule 8}
            self.resumeDnTrend = False;
        elif (self.close < self.dnTrend)  : #{Remain in down trend, record lower lows}
            self.dnTrend = self.close; #{Rule 2, 6b}

    def handleNaturalRally(self,bars):
        bar=bars[self.instrument]
        #{Natural Rally State}
        #begin {7}
        if (self.close > (self.naturalReaction + Thresh)) :
            self.naturalReactionRL = self.naturalReaction; #{Rule 4b}
        if (self.close > self.upTrend) : #{Resume self.upTrend}
            #begin {rules 6d, 6f}
            self.state = 0; #{InUpTrend}
            addCommentary(' Set to InUpTrend'+str(bar.getDateTime()));
            self.upTrend = self.close;
            self.resumeUT = True;
        elif (self.close > (self.natRallyBL + HalfThresh)) :
            #begin {Rules 5a}
            addCommentary('Set to InUpTrend'+str(bar.getDateTime()));
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.resumeUT = True;
        elif (self.close < self.dnTrend) : #{start self.dnTrend}
            #begin {Rule 6b}
            addCommentary('InNatRally start self.dnTrend'+str(bar.getDateTime()));
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.natRallyBL = self.close; #{Rule 4D}
        elif (self.close < (self.natRally - Thresh)) :
            if (self.close < self.naturalReaction) : #{start Natural Reaction}
                #begin {rule 4d, 6b}
                self.state = 4; #{InNatReact}
                addCommentary('InNatRally start nat reaction'+str(bar.getDateTime()));
                self.naturalReaction = self.close;
                self.natRallyBL =  self.close; #{Rule 4D} {Pivot pt, Rule 9b}
            else: #{start secondaryreaction}
                #begin  {rule 6h}
                addCommentary('InNatRally start sec reaction'+str(bar.getDateTime()));
                self.state = 5; #{InSecReact}
                self.secondaryReaction = self.close;
        if (self.close > self.natRally) :
            self.natRally = self.close;
            addCommentary(' none of the above');

    def handleSecondRally(self,bars):
        bar = bars[self.instrument]
        if (self.close > self.upTrend)  :
            #begin {rules 6d, 6f}
            addCommentary('InSecRally'+str(bar.getDateTime()));
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.resumeUT = True;
        elif (self.close > (self.natRallyBL + HalfThresh)) :
            #begin {rules 5a}
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.resumeUT = True;
        elif (self.close > self.natRally)  :
            #begin {rule 6g}
            self.state = 2; #{InNatRally}
            self.natRally = self.close;
        elif (self.close < self.dnTrend) : #{start self.dnTrend}
            #begin {rule 6b}
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.natRallyBL = self.close; #{Rule 4d, pivot pt, rule 9b}
        elif (self.close > self.secondaryRally) : #{Record higher high}
            self.secondaryRally = self.close; #{Rule 3, 6g}

    def handleNaturalReaction(self,bars):
        bar=bars[self.instrument]
        #{ Natural Reaction self.state }
        #begin   {Nat Reaction State}
        if (self.close < (self.natRally - Thresh)) :
            self.natRallyBL = self.natRally; #{Rule 4d}
            if (self.close < self.dnTrend) : #{Resume self.dnTrend}
                #begin {Rule 6b, 6e}
                addCommentary('InNatReact - InDnTrend1'+str(bar.getDateTime()));
                self.state = 1; #{InDnTrend}
                self.dnTrend = self.close;
                self.resumeDnTrend = True;
        elif (self.close < (self.naturalReactionRL - HalfThresh )) :
            #{resume self.dnTrend}
            #begin {rules 5b}
            addCommentary('InNatReact - InDnTrend2'+str(bar.getDateTime()));
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.resumeDnTrend = True;
        elif (self.close > self.upTrend)  : #{start self.upTrend}
            #begin {rule 6d}
            addCommentary('InNatReact - InUpTrend1'+str(bar.getDateTime()));
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.naturalReactionRL = self.close; #{Rule 4b, pvt point, rule 9c}
        elif (self.close > self.naturalReaction + Thresh) :
            if (self.close > self.natRally) : #{start Natural Rally}
                #begin {rules 4b, 6d}
                self.state = 2; #{In Nat Rally}
                self.natRally = self.close;
                self.naturalReactionRL = self.close; #{Rule 4b, pvt point, rule 9c}
            else :#{start SecondaryRally}
               #begin {rule 6g}
               self.state = 3; #{In Sec Rally}
               self.secondaryRally = self.close;
        elif (self.close < self.naturalReaction) : #{Remain in self.naturalReaction , record lower lows}
            self.naturalReaction = self.close; #{Rule 3, 6a, 6b}

    def handleSecondReaction(self, bar):
        addCommentary('InSecReact');
        if (self.close < self.dnTrend)  : #{Resume self.dnTrend}
            #begin {rules 6b, 6e}
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.resumeDnTrend = True;
        elif (self.close < (self.naturalReactionRL - HalfThresh)) :
            #begin {rules 5b}
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.resumeDnTrend = True;
        elif (self.close > self.upTrend) : #{start self.upTrend}
            #begin {rules 6d}
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.naturalReactionRL = self.close; #{Rule 4b, pivot point, rule 9c}
        elif (self.close < self.naturalReaction) :
            #begin {rules 6h}
            self.state = 4; #{InNatReact}
            self.naturalReaction = self.close;
        elif (self.close < self.secondaryReaction) : #{Record lower lows}
            self.secondaryReaction = self.close; #{Rule 6h}

    def handleTrade(self,bars):
        if tradetrends ==1:
            self.tradeOnly(bars)
        else:
            self.tradeReac(bars)

    def tradeOnly(self,bars):
        #{ Trend Rules }
        if (self.state == 0) : #{uptrend}
            if (self.__longPos is None) :
                self.buyAtMarket( bars, 'LE');
            if self.__shortPos is not None:
                self.coverAtMarket( bars,self.lastposition, 'SXL');
        if (self.state == 1) : #{downtrend}
           if (self.__shortPos is None) :
               self.shortAtMarket( bars, 'SE');
           if self.__longPos is not None:
               self.sellAtMarket( bars, self.lastposition, 'LXS');

    def tradeReac(self,bars):
        #{ Trend plus Rules = trade trends, rallies, reactions}
        if ((self.state == 0) or (self.state == 2) or (self.state == 3)) :
            if (not self.self.lastpositionactive()) :
                self.buyAtMarket( bars, 'LE');
            if self.ositionshort(self.lastposition) :
                self.coverAtMarket( bars,self.lastposition, 'SXL');
        if ((self.state == 1) or (self.state == 4) or (self.state == 5)) :
            if (not self.astpositionactive()) :
               self.shortAtMarket( bars, 'SE');
            if self.positionlong(self.lastposition) :
               self.sellAtMarket( bars, self.lastposition, 'LXS');

    def lastpositionactive(self):
        return False

    def positionshort(self,pos):
        if self.__shortPos > 0:
            return True
        else:
            return False

    def positionlong(self,pos):
        if self.__longPos > 0:
            return True
        else:
            return False

    def buyAtMarket(self,bars,comment):
        shares = int(self.getBroker().getCash() * 0.9 / bars[self.instrument].getPrice())
        #execInfo = position.getEntryOrder().getExecutionInfo()
        #self.info("BUY at $%.2f" % (execInfo.getPrice()))
        print("buy " +str(shares)+" shares at "+str(bars[self.instrument].getDateTime()))
        self.__longPos = self.enterLong(self.instrument, shares, True)
        self.lastposition=self.__longPos

    def coverAtMarket(self,bars,pos,comment):
        print("conver short at " +str(bars[self.instrument].getDateTime()))
        self.__shortPos.exitMarket()

    def shortAtMarket(self,bars,comment):
        shares = int(self.getBroker().getCash() * 0.9 / bars[self.instrument].getPrice())
        self.__shortPos = self.enterShort(self.instrument, shares, True)
        self.lastposition=self.__shortPos
        print("short " +str(shares)+" shares at "+str(bars[self.instrument].getDateTime()))

    def sellAtMarket(self,bars,pos,comment):
        print("conver short at " +str(bars[self.instrument].getDateTime()))
        self.__longPos.exitMarket()

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onExitOk(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))

def main():
    instrument='njyh'
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("njyh", "boll.csv")
    stra=JLV(feed,instrument,10)
    stra.run()

if __name__ == "__main__":
    main()
