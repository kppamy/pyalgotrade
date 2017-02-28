#!/usr/bin/env python
# coding=utf-8
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi
from pyalgotrade.technical import cross
threshold = 5;
PtsPctATR = 2; #{0=Points, 1=Precent, 2=ATR}
tradetrends = 1; #{0=trends and reactions, 1=trends only}
#{state = 0 Uptrend }
#{state = 1 Dntrend }
#{state = 2 NatRally}
#{state = 3 SecRally}
#{state = 4 NatReact}
#{state = 5 SecReact}
if (PtsPctATR = 0):
    Thresh = threshold;
    HalfThresh = thresh/2;
    def AddCommentary(comment):
        print(comment+\n)

def PriceClose(bar):
    return bar.getPrice() 

class JLV(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument,window):
        self.priceDS = feed[instrument].getPriceDataSeries()
        self.MA10_Now = ma.SMA(self.priceDS,window)

    def onBars(self, bars):
        lth=len(self.priceDS)
        if lth==1:
            initStrate(bar)
        elif lth ==21:
            if self.MA10_Now[-1] > self.MA10_10[-11] :
                AddCommentary('InUpTrend');
                State = 0;
                UpTrend = PriceClose(bar);
            else : 
                AddCommentary('InDnTrend');
                DnTrend = PriceClose(bar);;
                State = 1;
        elif lth>21:
            mainLoop(bar)
        else:
            AddCommentary('Never got here')

    def initStrate(self, bar):
        AddCommentary('Init');
        SecondaryRally = PriceClose(bar);
        NaturalRally = PriceClose(bar);
        UpTrend = PriceClose(bar);
        SecondaryReaction = PriceClose(bar);
        NaturalReaction = PriceClose(bar);
        DnTrend = PriceClose(bar);
        ResumeUpTrend = False;
        ResumeDnTrend = False;

    def mainLoop(self,bar):
        switch(state){
            case 0:
                handleUpTrend(bar);
                break;
            case 1:
                handleDnTrend(bar);
                break;
            case 2:
                handleNaturalRally(bar);
                break;
            case 3:
                handleSecondRally(bar);
                break;
            case 4:
                handleNaturalReaction(bar);
                break;
            case 5:
                handleSecondReaction(bar);
                break;
        }
    def resumeUpTrend(self,bar):
        #begin {6}
        if (PriceClose(bar) > (UpTrendRL + HalfThresh)) :
            ResumeUpTrend = False; #{Rule 10a}
            State = 4; #{InNatReact}
            NaturalReaction = PriceClose(bar);
            UpTrend = PriceClose(bar);
        elif (PriceClose(bar) < (UpTrendRL - HalfThresh)) :
            ResumeUpTrend = False; #{Rule 10b}
            State = 4; #{InNatReact}
            NaturalReaction = PriceClose(bar);

    def handleUpTrend(self,bar):
        #begin {4}
        if (PriceClose(bar) > (NaturalReaction + Thresh)) :
            NaturalReactionRL = NaturalReaction; #{Rule 4b}
            AddCommentary('InUpTrend');
            if ResumeUpTrend : #{ Rule 10 logic. }
                resumeUpTrend(bar)
        elif (PriceClose(bar) < (UpTrend - Thresh)) : #{start NaturalReaction}
            #begin {Rules 4a, 6a}
            State = 4; #{InNatReact}
            UpTrendRL = UpTr #{pivot point, rule 8}
            NaturalReaction = PriceClose(bar);
            ResumeUpTrend = False;
         elif (PriceClose(bar) > UpTrend) : #{Remain in uptrend higher high price}
             UpTrend = PriceClose(bar);
         #{4  InUpTrend}

     def resumeDnTrend(self,bar):
     def handleDnTrend(self,bar):
         #begin {9}
         if (PriceClose(bar) < (NaturalRally - Thresh)) :
             NaturalRallyBL = NaturalRally; #{Rule 4d}
             if ResumeDnTrend : #{Rule 10 logic best works with futures}
                 if (PriceClose(bar) < (DnTrendBL - HalfThresh)) :
                 ResumeDnTrend = False; #{Rule 10a}
                 DnTrend =  PriceClose(bar); #{Rule 2, 6b}
             elif (PriceClose(bar) > (DnTrendBL + HalfThresh)) : #{DnTrend Over}
             #{return to NaturalRally}
                      AddCommentary('return to NaturalRally');
                      ResumeDnTrend = False;
                      State = 2; #{InNatRally}
                      NaturalRally = PriceClose(bar);


         elif (PriceClose(bar) > (DnTrend + Thresh))  :  #{start NaturalRally}
         #begin  { rules 4c, 6c}
         AddCommentary('return to NaturalRally');
         State = 2; #{InNatRally}
         NaturalRally = PriceClose(bar);
         DnTrendBL = DnTr #{Pivot Pt, Rule 8}
         ResumeDnTrend = False;

                       elif (PriceClose(bar) < DnTrend)  : #{Remain in down trend, record lower lows}
                       DnTrend = PriceClose(bar); #{Rule 2, 6b}
                       def handleNaturalRally(self,bar):
                           {Natural Rally State}
                           #begin {7}

           if (PriceClose(bar) > (NaturalReaction + thresh)) :
           NaturalReactionRL = NaturalReaction; #{Rule 4b}
           if (PriceClose(bar) > UpTrend) : #{Resume UpTrend}
           #begin {rules 6d, 6f}
           State = 0; #{InUpTrend}
           AddCommentary(' Set to InUpTrend');
           UpTrend = PriceClose(bar);
           if UseRule10 : ResumeUpTrend = true;
           
               elif (PriceClose(bar) > (NaturalRallyBL + HalfThresh)) :
               #begin {Rules 5a}
               AddCommentary('Set to InUpTrend');
               State = 0; #{InUpTrend}
               UpTrend = PriceClose(bar);
               if UseRule10 : ResumeUpTrend = true;
               
               elif (PriceClose(bar) < DnTrend) : #{start DnTrend}
               #begin {Rule 6b}
               AddCommentary('InNatRally start dntrend');
               State = 1; #{InDnTrend}
               DnTrend = PriceClose(bar);
               NaturalRallyBL = PriceClose(bar); #{Rule 4D}
               
                elif (PriceClose(bar) < (NaturalRally - Thresh)) :
                
                if (PriceClose(bar) < NaturalReaction) : #{start Natural Reaction}
                #begin {rule 4d, 6b}
                State = 4; #{InNatReact}
                AddCommentary('InNatRally start nat reaction');
                NaturalReaction = PriceClose(bar);
                NaturalRallyBL =  PriceClose(bar); #{Rule 4D} {Pivot pt, Rule 9b}
                
                   else #{start secondaryreaction}
                   begin  {rule 6h}
                   AddCommentary('InNatRally start sec reaction');
                   State = 5; #{InSecReact}
                   SecondaryReaction = PriceClose(bar);
                   
                   if (PriceClose(bar) > NaturalRally) :
                   NaturalRally = PriceClose(bar);
                   AddCommentary(' none of the above');
                   

def handleSecondRally(self,bar):
    
    if (PriceClose(bar) > UpTrend)  :
    #begin {rules 6d, 6f}
    AddCommentary('InSecRally');
    State = 0; #{InUpTrend}
    UpTrend = PriceClose(bar);
    if UseRule10 : ResumeUpTrend = true;
    
                      elif (PriceClose(bar) > (NaturalRallyBL + halfthresh)) :
                      #begin {rules 5a}
                      State = 0; #{InUpTrend}
                      UpTrend = PriceClose(bar);
                      if UseRule10 : ResumeUpTrend = true;
                      
                      elif (PriceClose(bar) > NaturalRally)  :
                      #begin {rule 6g}
                      State = 2; #{InNatRally}
                      NaturalRally = PriceClose(bar);
                      
                       elif (PriceClose(bar) < DnTrend) : #{start DnTrend}
                       #begin {rule 6b}
                       State = 1; #{InDnTrend}
                       DnTrend = PriceClose(bar);
                       NaturalRallyBL = PriceClose(bar); #{Rule 4d, pivot pt, rule 9b}
                       
                       elif (PriceClose(bar) > SecondaryRally) : #{Record higher high}
                       SecondaryRally = PriceClose(bar); #{Rule 3, 6g}


       def handleNaturalReaction(self,bar): 
           { Natural Reaction State }
           begin   {Nat Reaction State}
           if (PriceClose(bar) < (NaturalRally - Thresh)) :
           NaturalRallyBL = NaturalRally; #{Rule 4d}
           if (PriceClose(bar) < DnTrend) : #{Resume DnTrend}
           #begin {Rule 6b, 6e}
           AddCommentary('InNatReact - InDnTrend1');
           State = 1; #{InDnTrend}
           DnTrend = PriceClose(bar);
           if UseRule10 : ResumeDnTrend = true;
           
                        elif (PriceClose(bar) < (NaturalReactionRL - halfthresh )) :
                        {resume DnTrend}
                        #begin {rules 5b}
                        AddCommentary('InNatReact - InDnTrend2');
                        State = 1; #{InDnTrend}
                        DnTrend = PriceClose(bar);
                        if UseRule10 : ResumeDnTrend = true;
                        
                         elif (PriceClose(bar) > UpTrend)  : #{start UpTrend}
                         #begin {rule 6d}
                         AddCommentary('InNatReact - InUpTrend1');
                         State = 0; #{InUpTrend}
                         UpTrend = PriceClose(bar);
                         NaturalReactionRL = PriceClose(bar); #{Rule 4b, pvt point, rule 9c}
                         
                            elif (PriceClose(bar) > NaturalReaction + Thresh) :
                            
                            if (PriceClose(bar) > NaturalRally) : #{start Natural Rally}
                            #begin {rules 4b, 6d}
                            State = 2; #{In Nat Rally}
                            NaturalRally = PriceClose(bar);
                            NaturalReactionRL = PriceClose(bar); #{Rule 4b, pvt point, rule 9c}
                            
                               else #{start SecondaryRally}
                               #begin {rule 6g}
                               State = 3; #{In Sec Rally}
                               SecondaryRally = PriceClose(bar);
                               
                               
                            elif (PriceClose(bar) < NaturalReaction) : #{Remain in NaturalReaction , record lower lows}
                            NaturalReaction = PriceClose(bar); #{Rule 3, 6a, 6b}
                            def handleSecondReaction(self, bar):
                                
                                AddCommentary('InSecReact');
                                if (PriceClose(bar) < DnTrend)  : #{Resume DnTrend}
                                #begin {rules 6b, 6e}
                                State = 1; #{InDnTrend}
                                DnTrend = PriceClose(bar);
                                if UseRule10 : ResumeDnTrend = true;
                                
                         elif (PriceClose(bar) < (NaturalReactionRL - halfthresh)) :
                         #begin {rules 5b}
                         State = 1; #{InDnTrend}
                         DnTrend = PriceClose(bar);
                         if UseRule10 : ResumeDnTrend = true;
                         
                          elif (PriceClose(bar) > UpTrend) : #{start UpTrend}
                          #begin {rules 6d}
                          State = 0; #{InUpTrend}
                          UpTrend = PriceClose(bar);
                          NaturalReactionRL = PriceClose(bar); #{Rule 4b, pivot point, rule 9c}
                          
                          elif (PriceClose(bar) < NaturalReaction) :
                          #begin {rules 6h}
                          State = 4; #{InNatReact}
                          NaturalReaction = PriceClose(bar);
                          
                          elif (PriceClose(bar) < SecondaryReaction) : #{Record lower lows}
                          SecondaryReaction = PriceClose(bar); #{Rule 6h}
                          
    def handleTrade(self,bar):
        if tradetrends ==1:
            self.tradeOnly(bar)
        else
            self.tradeReac(bar)

    def tradeOnly(self,bar):
        #{ Trend Rules }
        if (State = 0) : #{uptrend}
            if (not lastpositionactive()) :
                buyAtMarket( Bar+1, 'LE');
            if positionshort(lastposition) :
                coverAtMarket( Bar+1,LastPosition, 'SXL');
        if (State = 1) : #{downtrend}
           if (not lastpositionactive()) :
               shortAtMarket( Bar+1, 'SE');
           if positionlong(lastposition) :
               SellAtMarket( Bar+1, Lastposition, 'LXS');

    def tradeReac(self,bar):
        #{ Trend plus Rules = trade trends, rallies, reactions}
        if ((State = 0) or (State = 2) or (State = 3)) :
            if (not lastpositionactive()) :
                buyAtMarket( Bar+1, 'LE');
            if positionshort(lastposition) :
                coverAtMarket( Bar+1,LastPosition, 'SXL');
        if ((State = 1) or (State = 4) or (State = 5)) :
            if (not lastpositionactive()) :
               shortAtMarket( Bar+1, 'SE');
            if positionlong(lastposition) :
               SellAtMarket( Bar+1, Lastposition, 'LXS');

