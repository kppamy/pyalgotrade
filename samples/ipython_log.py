# IPython log file

get_ipython().magic(u'run -d -b47 attract.py')
get_ipython().magic(u'ls ')
df=DataFrame.from_csv('njyh.csv')
df.Date=pd.to_datetime(df.Date)
df.head()
df.dtypes
df.set_index('Date')
df.head()
get_ipython().magic(u'logstart')
get_ipython().magic(u'hist ')
from datetime import datetime
datetime.now()
to=datetime.now()
df[:to]
to.date
to.date()
df[:20080917]
now
to
df[:to]
df[:datetime(2009,8,1)]
df[:datetime(2009,8,1)]
df.head()
df.dtypes
df.set_index('Date')
df.head()
df=df.set_index('Date')
df.head()
df[:to]
df.sort_index？
get_ipython().magic(u'pinfo df.sort_index')
df.sort_index()
df.head()
df=df.sort_index()
df.head()
df[:datetime(2007,8,5)]
to
df[:to]
len(df)
