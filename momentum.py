import pandas as pd


def mom_return(data):

    df = data.copy()
    df['date'] = pd.to_datetime(df['date'])

    df['CumReturn'] = df.groupby('permno')['Rn'].apply(lambda x: x.shift(1).rolling(window=11).sum()).reset_index(level=0, drop=True)
    df['momentum_rank'] = df.groupby('date')['CumReturn'].transform(lambda x: pd.qcut(x, 10, labels=False, duplicates='drop') + 1)
    df['vw_weight'] = df.groupby(['date', 'momentum_rank'])['mcap'].transform(lambda x: x / x.sum())
    df['weighted_ret'] = df['Rn'] * df['vw_weight']
    decile_returns = df.groupby(['date', 'momentum_rank'], group_keys=False)['weighted_ret'].sum().reset_index(name='ret_vw')
    long = decile_returns[decile_returns['momentum_rank'] >= 8].groupby('date')['ret_vw'].mean()
    short = decile_returns[decile_returns['momentum_rank'] <= 3].groupby('date')['ret_vw'].mean()
    MOM_return = (long - short).reset_index(name='MOM_return')

    return MOM_return
