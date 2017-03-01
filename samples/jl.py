#!/usr/bin/env python
# coding=utf-8
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi
from pyalgotrade.technical import cross

threshold = 5;
PtsPctATR = 2; #{0=Points, 1=Precent, 2=ATR}
tradetrends = 1; #{0=trends and reactions, 1=trends only}
#{self.state = 0 self.upTrend }
#{self.state = 1 self.dnTrend }
#{self.state = 2 NatRally}
#{self.state = 3 SecRally}
#{self.state = 4 NatReact}
#{self.state = 5 SecReact}
if (PtsPctATR = 0):
    Thresh = threshold;
    HalfThresh = thresh/2;

def addCommentary(comment):
    print(comment)

class JLV(strategy.BacktestingStrategy):

    def __init__(self, feed, instrument,window):
        self.priceDS = feed[instrument].getPriceDataSeries()
        self.MA10_Now = ma.SMA(self.priceDS,window)
        self.instrement=instrument

    def onBars(self, bars):
        bar=bars[self.instrement]
        lth=len(self.priceDS)
        self.close=bar.getPrice()
        if lth==1:
            initStrate()
        elif lth ==21:
            if self.MA10_Now[-1] > self.MA10_10[-11] :
                addCommentary('InUpTrend');
                self.state = 0;
                self.upTrend = self.close;
            else : 
                addCommentary('InDnTrend');
                self.dnTrend = self.close;;
                self.state = 1;
        elif lth>21:
            mainLoop(bar)
        else:
            addCommentary('Never got here')

    def initStrate(self):
        addCommentary('Init');
        self.secondaryRally = self.close;
        self.natRally = self.close;
        self.upTrend = self.close;
        self.secondaryReaction = self.close;
        self.naturalReaction = self.close;
        self.dnTrend = self.close;
        self.resumeUpTrend = False;
        self.resumeDnTrend = False;

    def mainLoop(self):
        switch(state){
            case 0:
                handleUpTrend();
                break;
            case 1:
                handleDnTrend();
                break;
            case 2:
                handleNaturalRally();
                break;
            case 3:
                handleSecondRally();
                break;
            case 4:
                handleNaturalReaction();
                break;
            case 5:
                handleSecondReaction();
                break;
        }
    def resumeUpTrend(self):
        #begin {6}
        if (self.close > (UpTrendRL + HalfThresh)) :
            self.resumeUpTrend = False; #{Rule 10a}
            self.state = 4; #{InNatReact}
            self.naturalReaction = self.close;
            self.upTrend = self.close;
        elif (self.close < (UpTrendRL - HalfThresh)) :
            self.resumeUpTrend = False; #{Rule 10b}
            self.state = 4; #{InNatReact}
            self.naturalReaction = self.close;

    def handleUpTrend(self):
        #begin {4}
        if (self.close > (self.naturalReaction + Thresh)) :
            self.naturalReactionRL = NaturalReaction; #{Rule 4b}
            addCommentary('InUpTrend');
            if self.resumeUpTrend : #{ Rule 10 logic. }
               resumeUpTrend()
        elif (self.close < (self.upTrend - Thresh)) : #{start NaturalReaction}
            #begin {Rules 4a, 6a}
            self.state = 4; #{InNatReact}
            UpTrendRL = UpTr #{pivot point, rule 8}
            self.naturalReaction = self.close;
            self.resumeUpTrend = False;
        elif (self.close > UpTrend) : #{Remain in self.upTrend higher high price}
            self.upTrend = self.close;
         #{4  InUpTrend}

    def resumeDnTrend(self,bar):
    def handleDnTrend(self,bar):
        #begin {9}
        if (self.close < (self.natRally - Thresh)) :
            self.naturalRallyBL = NaturalRally; #{Rule 4d}
            if self.resumeDnTrend : #{Rule 10 logic best works with futures}
                if (self.close < (DnTrendBL - HalfThresh)) :
                    self.resumeDnTrend = False; #{Rule 10a}
                    self.dnTrend =  self.close; #{Rule 2, 6b}
                elif (self.close > (DnTrendBL + HalfThresh)) : #{self.dnTrend Over}
                    #{return to NaturalRally}
                    addCommentary('return to NaturalRally');
                    self.resumeDnTrend = False;
                    self.state = 2; #{InNatRally}
                    self.natRally = self.close;
        elif (self.close > (self.dnTrend + Thresh))  :  #{start NaturalRally}
            #begin  { rules 4c, 6c}
            addCommentary('return to NaturalRally');
            self.state = 2; #{InNatRally}
            self.natRally = self.close;
            self.dnTrendBL = DnTr #{Pivot Pt, Rule 8}
            self.resumeDnTrend = False;
        elif (self.close < self.dnTrend)  : #{Remain in down trend, record lower lows}
            self.dnTrend = self.close; #{Rule 2, 6b}

    def handleNaturalRally(self,bar):
        #{Natural Rally State}
        #begin {7}
        if (self.close > (self.naturalReaction + thresh)) :
            self.naturalReactionRL = NaturalReaction; #{Rule 4b}
        if (self.close > UpTrend) : #{Resume UpTrend}
            #begin {rules 6d, 6f}
            self.state = 0; #{InUpTrend}
            addCommentary(' Set to InUpTrend');
            self.upTrend = self.close;
            self.resumeUpTrend = True;
        elif (self.close > (self.naturalRallyBL + HalfThresh)) :
            #begin {Rules 5a}
            addCommentary('Set to InUpTrend');
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.resumeUpTrend = True;
        elif (self.close < self.dnTrend) : #{start self.dnTrend}
            #begin {Rule 6b}
            addCommentary('InNatRally start self.dnTrend');
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.naturalRallyBL = self.close; #{Rule 4D}
        elif (self.close < (self.natRally - Thresh)) :
            if (self.close < NaturalReaction) : #{start Natural Reaction}
                #begin {rule 4d, 6b}
                self.state = 4; #{InNatReact}
                addCommentary('InNatRally start nat reaction');
                self.naturalReaction = self.close;
                self.naturalRallyBL =  self.close; #{Rule 4D} {Pivot pt, Rule 9b}
            else #{start secondaryreaction}
                #begin  {rule 6h}
                addCommentary('InNatRally start sec reaction');
                self.state = 5; #{InSecReact}
                self.secondaryReaction = self.close;
        if (self.close > NaturalRally) :
            self.natRally = self.close;
            addCommentary(' none of the above');

    def handleSecondRally(self,bar):
        if (self.close > UpTrend)  :
            #begin {rules 6d, 6f}
            addCommentary('InSecRally');
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.resumeUpTrend = True;
        elif (self.close > (self.naturalRallyBL + halfthresh)) :
            #begin {rules 5a}
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.resumeUpTrend = True;
        elif (self.close > NaturalRally)  :
            #begin {rule 6g}
            self.state = 2; #{InNatRally}
            self.natRally = self.close;
        elif (self.close < self.dnTrend) : #{start self.dnTrend}
            #begin {rule 6b}
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.naturalRallyBL = self.close; #{Rule 4d, pivot pt, rule 9b}
        elif (self.close > SecondaryRally) : #{Record higher high}
            self.secondaryRally = self.close; #{Rule 3, 6g}

    def handleNaturalReaction(self,bar): 
        #{ Natural Reaction self.state }
        #begin   {Nat Reaction State}
        if (self.close < (self.natRally - Thresh)) :
            self.naturalRallyBL = NaturalRally; #{Rule 4d}
            if (self.close < self.dnTrend) : #{Resume self.dnTrend}
                #begin {Rule 6b, 6e}
                addCommentary('InNatReact - InDnTrend1');
                self.state = 1; #{InDnTrend}
                self.dnTrend = self.close;
                self.resumeDnTrend = True;
        elif (self.close < (self.naturalReactionRL - halfthresh )) :
            #{resume self.dnTrend}
            #begin {rules 5b}
            addCommentary('InNatReact - InDnTrend2');
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.resumeDnTrend = True;
         elif (self.close > UpTrend)  : #{start UpTrend}
             #begin {rule 6d}
             addCommentary('InNatReact - InUpTrend1');
             self.state = 0; #{InUpTrend}
             self.upTrend = self.close;
             self.naturalReactionRL = self.close; #{Rule 4b, pvt point, rule 9c}
        elif (self.close > self.naturalReaction + Thresh) :
            if (self.close > NaturalRally) : #{start Natural Rally}
                #begin {rules 4b, 6d}
                self.state = 2; #{In Nat Rally}
                self.natRally = self.close;
                self.naturalReactionRL = self.close; #{Rule 4b, pvt point, rule 9c}
           else #{start SecondaryRally}
               #begin {rule 6g}
               self.state = 3; #{In Sec Rally}
               self.secondaryRally = self.close;
        elif (self.close < NaturalReaction) : #{Remain in self.naturalReaction , record lower lows}
            self.naturalReaction = self.close; #{Rule 3, 6a, 6b}

    def handleSecondReaction(self, bar):
        addCommentary('InSecReact');
        if (self.close < self.dnTrend)  : #{Resume self.dnTrend}
            #begin {rules 6b, 6e}
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.resumeDnTrend = True;
        elif (self.close < (self.naturalReactionRL - halfthresh)) :
            #begin {rules 5b}
            self.state = 1; #{InDnTrend}
            self.dnTrend = self.close;
            self.resumeDnTrend = True;
        elif (self.close > UpTrend) : #{start UpTrend}
            #begin {rules 6d}
            self.state = 0; #{InUpTrend}
            self.upTrend = self.close;
            self.naturalReactionRL = self.close; #{Rule 4b, pivot point, rule 9c}
        elif (self.close < NaturalReaction) :
            #begin {rules 6h}
            self.state = 4; #{InNatReact}
            self.naturalReaction = self.close;
        elif (self.close < SecondaryReaction) : #{Record lower lows}
            self.secondaryReaction = self.close; #{Rule 6h}
                          
    def handleTrade(self,bar):
        if tradetrends ==1:
            self.tradeOnly(bar)
        else
            self.tradeReac(bar)

    def tradeOnly(self,bar):
        #{ Trend Rules }
        if (self.state = 0) : #{uptrend}
            if (not lastpositionactive()) :
                buyAtMarket( Bar+1, 'LE');
            if positionshort(lastposition) :
                coverAtMarket( Bar+1,LastPosition, 'SXL');
        if (self.state = 1) : #{downtrend}
           if (not lastpositionactive()) :
               shortAtMarket( Bar+1, 'SE');
           if positionlong(lastposition) :
               SellAtMarket( Bar+1, Lastposition, 'LXS');

    def tradeReac(self,bar):
        #{ Trend plus Rules = trade trends, rallies, reactions}
        if ((self.state = 0) or (self.state = 2) or (self.state = 3)) :
            if (not lastpositionactive()) :
                buyAtMarket( Bar+1, 'LE');
            if positionshort(lastposition) :
                coverAtMarket( Bar+1,LastPosition, 'SXL');
        if ((self.state = 1) or (self.state = 4) or (self.state = 5)) :
            if (not lastpositionactive()) :
               shortAtMarket( Bar+1, 'SE');
            if positionlong(lastposition) :
               SellAtMarket( Bar+1, Lastposition, 'LXS');
