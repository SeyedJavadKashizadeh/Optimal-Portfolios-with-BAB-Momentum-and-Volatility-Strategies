import numpy as np
import pandas as pd
import datetime

today = datetime.date.today().strftime('%Y-%m-%d')

def rf_rate(db):
    Rf = db.raw_sql(f"""
        select mcaldt, tmytm 
        from crsp.tfz_mth_rf            
        where kytreasnox = 2000001 
          and mcaldt >= '1964-01-01'
          and mcaldt <= '{today}'
    """, date_cols=['mcaldt'])

    Rf['tmytm'] = Rf['tmytm'] / 12 / 100
    Rf = Rf.rename(columns={"mcaldt": "date", "tmytm": "rf"})
    return Rf


def market_ret(db):
    Rm = db.raw_sql(f"""
        select date, vwretd 
        from crsp.msi 
        where date >= '1964-01-01' and date <= '{today}'
    """, date_cols=['date'])

    return Rm.rename(columns={'vwretd': 'Rm'})

def sic_data(db):
    sic_data = db.raw_sql(f"""
        SELECT a.permno, a.date, 
               c.siccd,
                c.comnam
        FROM crsp.msf AS a
        LEFT JOIN crsp.msenames AS b
        ON a.permno = b.permno
        AND b.namedt <= a.date
        AND a.date <= b.nameendt
        LEFT JOIN crsp.stocknames AS c
        ON a.permno = c.permno
        WHERE a.date BETWEEN '01/01/1964' AND '{today}'
        AND b.exchcd BETWEEN 1 AND 2
        AND b.shrcd BETWEEN 10 AND 11
    """, date_cols=['date'])

    return sic_data

def stock_data(db):
    stock_data = db.raw_sql(f"""
        select a.permno, a.date, 
               b.shrcd, b.exchcd,
               a.ret, a.shrout, a.prc
        from crsp.msf as a
        left join crsp.msenames as b
          on a.permno = b.permno
         and b.namedt <= a.date
         and a.date <= b.nameendt
        left join crsp.stocknames as c 
          on a.permno = c.permno
        where a.date between '1964-01-01' and '{today}'
          and b.exchcd between 1 and 2
          and b.shrcd between 10 and 11
    """, date_cols=['date'])


    stock_data = stock_data.drop(['shrcd', 'exchcd'], axis=1)
    stock_data = stock_data.rename(columns={'ret': 'Rn'})
    stock_data['mcap'] = np.abs(stock_data['prc']) * stock_data['shrout']
    stock_data['mcap_l'] = stock_data.groupby(['permno'])['mcap'].shift(1)
    return stock_data
