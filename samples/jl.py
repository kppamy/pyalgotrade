#!/usr/bin/env python
# coding=utf-8
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi
from pyalgotrade.technical import cross
threshold := 5;
PtsPctATR := 2;     {0=Points, 1=Precent, 2=ATR}
tradetrends := 1;   {0=trends and reactions, 1=trends only}
{State = 0 Uptrend }
{State = 1 Dntrend }
{State = 2 NatRally}
{State = 3 SecRally}
{State = 4 NatReact}
{State = 5 SecReact}
if (PtsPctATR = 0):
    Thresh := threshold;
    HalfThresh := thresh/2;
def AddCommentary(comment):
    print(comment+\n)
    
def PriceClose(bar):
    return bar.getPrice() 

class JLV(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold):
    def onBars(self, bars):
        
