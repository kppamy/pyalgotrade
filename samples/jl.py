#!/usr/bin/env python
# coding=utf-8
import pandas as pd
import numpy as np
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
        self.window=window
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
            if self.MA10_Now[-1] > self.MA10_Now[-1*(1+self.window)] :
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
        price_ori_index=pd.Series(self.priceDS[:])
        price_ori_index.sort_values(inplace=True)
        prices_sorted=price_ori_index.get_values()
        #self.secondaryRally = self.close;
        self.natRally = prices_sorted[self.window*2-1];
        self.natRallyRL = self.natRally;
        self.upTrend = prices_sorted.max()
        #self.upTrendRL = -1;
        self.upTrendRL = self.upTrend;
        #self.secondaryReaction = self.close;
        self.naturalReaction = prices_sorted[1]
        self.natReacBL =self.naturalReaction;
        self.dnTrend = prices_sorted.min() ;
        self.dnTrendBL =prices_sorted.min();
        addCommentary('*************Init**********dnTrend ='+str(self.dnTrend));
        addCommentary('*************Init**********naturalReaction  ='+str(self.naturalReaction));
        addCommentary('*************Init**********upTrend ='+str(self.upTrend));
        addCommentary('*************Init**********natRally  ='+str(self.natRally));
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

    def handleUpTrend(self,bars):
        bar=bars[self.instrument]
        today=' '+str(self.close)+' '+str(bar.getDateTime())
        self.checkPivots(today)
        #begin {4}
        #if self.resumeUT : #{ Rule 10 logic. }
        #    #begin {6}
        #    self.resumeUT = False; #{Rule 10a}
        #    if (self.close > (self.upTrendRL + HalfThresh)) :
        #        self.state = 0; #{InUpTend}
        #        self.naturalReaction = self.close;
        #        self.upTrend = self.close;
        #        addCommentary('resumeUpTrend success'+today)
        #    elif (self.close < (self.upTrendRL - HalfThresh)) :
        #        self.state = 4; #{InNatReact}
        #        self.naturalReaction = self.close;
        #        addCommentary('resumeUpTrend fail '+today)
        if (self.close < self.dnTrendBL):
            self.state = 1; #{InDnTrend}
            addCommentary(' UpTrend ===> InDnTrend '+today);
            self.upTrendRL = self.upTrend #{pivot point, rule 8}
            self.dnTrend = self.close;
            self.resumeUT = False;
            addCommentary('***************upTrendRL*************'+str(self.upTrendRL))
        elif (self.close < (self.upTrend - Thresh)) : #{start self.naturalReaction}
            #begin {Rules 4a, 6a}
            self.state = 4; #{InNatReact}
            addCommentary(' UpTrend ===> InNatReact '+today);
            self.upTrendRL = self.upTrend #{pivot point, rule 8}
            addCommentary('***************upTrendRL*************'+str(self.upTrendRL))
            self.naturalReaction = self.close;
            self.resumeUT = False;
        elif (self.close > self.upTrend) : #{Remain in self.upTrend higher high price}
            self.upTrend = self.close;
            #addCommentary('remain in upTrend: '+today)
         #{4  InUpTrend}

    def handleDnTrend(self,bars):
        #begin {9}
        bar=bars[self.instrument]
        today=' '+str(self.close)+' '+str(bar.getDateTime())
        self.checkPivots(today)
        #if self.resumeDnTrend : #{Rule 10 logic best works with futures}
        #    if (self.close < (self.dnTrendBL - HalfThresh)) :
        #        self.resumeDnTrend = False; #{Rule 10a}
        #        self.dnTrend =  self.close; #{Rule 2, 6b}
        #        addCommentary('resume dnTrend success'+today)
        #    elif (self.close > (self.dnTrendBL + HalfThresh)) : #{self.dnTrend Over}
        #        #{return to self.natualRally}
        #        self.resumeDnTrend = False;
        #        self.state = 2; #{InNatRally}
        #        self.natRally = self.close;
        #        addCommentary(' resume dnTrend fail, go back to natRally '+today)
        if (self.close > (self.upTrendRL))  :  #{start self.natualRally}
            #begin  { rules 4c, 6c}
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.dnTrendBL = self.dnTrend #{Pivot Pt, Rule 8}
            addCommentary('dnTrend ==> natRally dnTrend= '+str(self.dnTrend)+today);
            addCommentary('***************dnTrendBL************'+str(self.dnTrendBL)+ today)
        elif (self.close > (self.dnTrend + Thresh))  :  #{start self.natualRally}
            #begin  { rules 4c, 6c}
            self.state = 2; #{InNatRally}
            self.natRally = self.close;
            self.dnTrendBL = self.dnTrend #{Pivot Pt, Rule 8}
            addCommentary('dnTrend ==> natRally dnTrend= '+str(self.dnTrend)+today);
            addCommentary('***************dnTrendBL************'+str(self.dnTrendBL)+ today)
        elif (self.close < self.dnTrend)  : #{Remain in down trend, record lower lows}
            self.dnTrend = self.close; #{Rule 2, 6b}
            #addCommentary('remain in dnTrend '+today)

    def handleNaturalRally(self,bars):
        bar=bars[self.instrument]
        today=' '+str(self.close)+' '+str(bar.getDateTime())
        self.checkPivots(today)
        #{Natural Rally State}
        #begin {7}
        if ( self.close > self.upTrendRL) : #{Resume self.upTrend}
            #begin {rules 6d, 6f}
            self.state = 0; #{InUpTrend}
            addCommentary(' natualRally ==>InUpTrend1 resumeUT  '+today);
            self.upTrend = self.close;
            self.resumeUT = True;
            self.natRallyRL = self.natRally;
            addCommentary('*************naturalRallyBL************ = '+str(self.natRallyRL))
        elif ( self.close > (self.natRallyRL + HalfThresh)) :
            #begin {Rules 5a}
            addCommentary('natualRally ==> InUpTrend2 resumeUT '+today);
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            #self.upTrendRL = self.close;
            #addCommentary('*************InNatRally upTrendRL************* = '+str(self.upTrendRL))
            self.resumeUT = True;
            self.natRallyRL = self.close;
            addCommentary('*************naturalRallyBL************ = '+str(self.natRallyRL))
        elif (self.close < self.dnTrendBL) : #{start self.dnTrend}
            #begin {Rule 6b}
            addCommentary('InNatRally ==> dnTrend '+today);
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.natRallyRL = self.natRally; #{Rule 4d}
            addCommentary('****************naturalRallyBL**************'+str(self.natRallyRL)+today)
        elif (self.close < (self.natRally - Thresh)) :
            if (self.close < self.natReacBL) : #{start Natural Reaction}
                #begin {rule 4d, 6b}
                self.state = 4; #{InNatReact}
                addCommentary('InNatRally ==> natReaction '+today);
                self.naturalReaction = self.close;
                self.natRallyRL =  self.natRally; #{Rule 4d} {Pivot pt, Rule 9b}
                addCommentary('****************naturalRallyBL**************'+str(self.natRallyRL)+today)
            else: #{start secondaryreaction}
                #begin  {rule 6h}
                addCommentary('InNatRally ==> secReaction '+today);
                self.state = 5; #{InSecReact}
                self.secondaryReaction = self.close;
        elif (self.close > self.natRally) :
            self.natRally = self.close;
            #addCommentary('remain in natRally'+today);

    def handleSecondRally(self,bars):
        bar=bars[self.instrument]
        today=' '+str(self.close)+' '+str(bar.getDateTime())
        self.checkPivots(today)
        if self.close > self.upTrendRL :
            #begin {rules 6d, 6f}
            addCommentary('InSecRally ==> upTrend1 '+today);
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.resumeUT = True;
        elif ( self.close > (self.natRallyRL + HalfThresh)) :
            #begin {rules 5a}
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.resumeUT = True;
            addCommentary('InSecRally ==> upTrend2 '+today);
        elif (self.close > self.natRallyRL)  :
            #begin {rule 6g}
            self.state = 2; #{InNatRally}
            self.natRally = self.close;
            addCommentary('InSecRally ==> natRally '+today);
        elif (self.close < self.dnTrendBL) : #{start self.dnTrend}
            #begin {rule 6b}
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            #self.natRallyRL = self.secondaryRally; #{Rule 4d, pivot pt, rule 9b}
            addCommentary('InSecRally ==> dnTrend '+today);
        elif (self.close < self.secondaryRally - Thresh) : #{start self.dnTrend}
            self.state = 4; #{InNatReac}
            self.naturalReaction = self.close;
            addCommentary('InSecRally ==> naturalReaction '+today);
        elif (self.close > self.secondaryRally) : #{Record higher high}
            self.secondaryRally = self.close; #{Rule 3, 6g}
            #addCommentary('remain In SecRally '+today);
        else :
            addCommentary('===============InSecRally never got here================')

    def handleNaturalReaction(self,bars):
        bar=bars[self.instrument]
        today=' '+str(self.close)+' '+str(bar.getDateTime())
        #{ Natural Reaction self.state }
        #begin   {Nat Reaction State}
        if (self.close < self.dnTrendBL - HalfThresh) : #{Resume self.dnTrend}
            #begin {Rule 6b, 6e}
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.dnTrendBL = self.close;
            self.resumeDnTrend = True;
            addCommentary('InNatReact ==> InDnTrend1'+today);
        elif (self.natReacBL > 0 and self.close < (self.natReacBL - HalfThresh )) :
            #{resume self.dnTrend}
            #begin {rules 5b}
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.resumeDnTrend = True;
            addCommentary('InNatReact ==> InDnTrend2  '+today);
            #addCommentary(' naturalReactionRL= '+str(self.natReacBL)+' dnTrend= '+str(self.dnTrend));
        elif (self.close > self.upTrendRL)  : #{start self.upTrend}
            #begin {rule 6d}
            addCommentary('InNatReact ==> InUpTrend1'+today);
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.natReacBL = self.naturalReaction; #{Rule 4b, pvt point, rule 9c}
            addCommentary('************naturalReactionRL***********'+str(self.natReacBL)+today);
        elif (self.close > self.naturalReaction + Thresh) :
            if (self.close > self.natRallyRL) : #{start Natural Rally}
                #begin {rules 4b, 6d}
                self.state = 2; #{In Nat Rally}
                self.natRally = self.close;
                self.natReacBL = self.naturalReaction; #{Rule 4b, pvt point, rule 9c}
                addCommentary(' naturalReaction ==> natRally day 1'+today)
                addCommentary('************naturalReactionRL***********'+str(self.natReacBL));
            else :#{start SecondaryRally}
               #begin {rule 6g}
               self.state = 3; #{In Sec Rally}
               self.natReacBL = self.naturalReaction;
               self.secondaryRally = self.close
               addCommentary('InNatReact ==> secondaryRally'+today);
               addCommentary('naturalRallyBL = '+str(self.natRallyRL))
        elif (self.close < self.naturalReaction) : #{Remain in self.naturalReaction , record lower lows}
            self.naturalReaction = self.close; #{Rule 3, 6a, 6b}
            #addCommentary('remain in naturalReaction '+today)
        else :
            addCommentary('===============InNatReac never got here================')

    def handleSecondReaction(self, bars):
        bar=bars[self.instrument]
        today=' '+str(self.close)+' '+str(bar.getDateTime())
        self.checkPivots(today)
        if (self.close < self.dnTrendBL)  : #{Resume self.dnTrend}
            #begin {rules 6b, 6e}
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.resumeDnTrend = True;
            addCommentary('secondaryReaction ==> dnTrend '+today)
        elif (self.close < (self.natReacBL - HalfThresh)) :
            #begin {rules 5b}
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.resumeDnTrend = True;
            addCommentary('secondaryReaction ==> dnTrend naturalReactionRL= '+str(self.natReacBL)+today)
        elif (self.close < self.natReacBL) :
            #begin {rules 6h}
            self.state = 4; #{InNatReact}
            self.naturalReaction = self.close;
            addCommentary('secondaryReaction ==> naturalReaction '+today)
        elif (self.close > self.upTrendRL + Thresh) : #{start self.upTrend}
            #begin {rules 6d}
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            addCommentary('secondaryReaction ==> upTrend '+today)
            #self.natReacBL = self.close; #{Rule 4b, pivot point, rule 9c}
        elif (self.close > self.secondaryReaction + Thresh) : #{start self.upTrend}
            #begin {rules 6d}
            self.state = 2; #{InUpTrend}
            self.natRally = self.close;
            addCommentary('secondaryReaction ==> natRally '+today)
            #self.natReacBL = self.close; #{Rule 4b, pivot point, rule 9c}
        elif (self.close < self.secondaryReaction) : #{Record lower lows}
            self.secondaryReaction = self.close; #{Rule 6h}
            #addCommentary('remain in secondaryReaction  '+today)
        else :
            addCommentary('===============InSecReac never got here================')

    def handleTrade(self,bars):
        if tradetrends ==1:
            self.tradeOnly(bars)
        else:
            self.tradeReac(bars)

    def checkPivots(today):
        flag= ( (self.upTrendRL > self.natRallyRL) and (self.natRallyRL >  self.natReacBL ) and (self.natReacBL > self.dnTrendBL))
        if flag is False:
            addCommentary('!!!!!!!!!!!!!!!!!!!not comply with assumption!!!!!!!!!!!'+today)
            addCommentary('upTrendRL= '+str(self.upTrendRL) +' natRallyRL '+str(self.natRallyRL)+' natReacBL '+str(self.natReacBL) + ' self.dnTrendBL '+str(self.dnTrendBL))

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
        if not self.__shortPos.exitActive():
            self.__shortPos.exitMarket()

    def shortAtMarket(self,bars,comment):
        shares = int(self.getBroker().getCash() * 0.9 / bars[self.instrument].getPrice())
        self.__shortPos = self.enterShort(self.instrument, shares, True)
        self.lastposition=self.__shortPos
        print("short " +str(shares)+" shares at "+str(bars[self.instrument].getDateTime()))

    def sellAtMarket(self,bars,pos,comment):
        if not self.__longPos.exitActive():
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
