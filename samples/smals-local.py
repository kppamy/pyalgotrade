import itertools
from pyalgotrade.optimizer import local
from pyalgotrade.barfeed import yahoofeed
import smals 


def parameters_generator():
    instrument = ["dia"]
    entrySMA = range(40, 80,2)
    exitSMA = range(1,15,2)
    return itertools.product(instrument, entrySMA, exitSMA)


# The if __name__ == '__main__' part is necessary if running on Windows.
if __name__ == '__main__':
    # Load the feed from the CSV files.
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("dia", "njyh.csv")

    local.run(smals.SMALS, feed, parameters_generator())
