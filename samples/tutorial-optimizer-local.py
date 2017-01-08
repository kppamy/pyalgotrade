import itertools
from pyalgotrade.optimizer import local
from pyalgotrade.barfeed import quandlfeed
import rsi2


def parameters_generator():
   # instrument = ["ibm"]
   # entrySMA = range(150, 251)
   # exitSMA = range(5, 16)
   # rsiPeriod = range(2, 11)
   # overBoughtThreshold = range(75, 96)
   # overSoldThreshold = range(5, 26)
    
    instrument = ["dia"]
    entrySMA =[56]
    exitSMA =[8]
    rsiPeriod =[2]
    overBoughtThreshold =range(75,100) 
    overSoldThreshold =range(10,20) 
    #entrySMA = range(50,74,2)
    #exitSMA = range(5, 12,2)
    #rsiPeriod = range(2, 5,2)
    #overBoughtThreshold = range(70,68,2)
    #overSoldThreshold = range(15, 26,2)

    return itertools.product(instrument, entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold)
    


# The if __name__ == '__main__' part is necessary if running on Windows.
if __name__ == '__main__':
    # Load the bar feed from the CSV files.
#    feed = quandlfeed.Feed()
#    feed.addBarsFromCSV("ibm", "WIKI-IBM-2009-quandl.csv")
#    feed.addBarsFromCSV("ibm", "WIKI-IBM-2010-quandl.csv")
#    feed.addBarsFromCSV("ibm", "WIKI-IBM-2011-quandl.csv")
#
    # Load the feed from the CSV files.
    feed = yahoofeed.Feed()
    print('************bear************************')
    feed.addBarsFromCSV("dia", "njyh-2016.csv")
    local.run(rsi2.RSI2, feed, parameters_generator())
    feed = yahoofeed.Feed()
    #print('*************boll*************')
    #feed.addBarsFromCSV("dia", "boll.csv")
    #local.run(rsi2.RSI2, feed, parameters_generator())
