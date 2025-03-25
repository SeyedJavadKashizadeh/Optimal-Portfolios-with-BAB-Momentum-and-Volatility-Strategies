import pandas as pd


def mom_return(data):

    data = data.copy()
    data['date'] = pd.to_datetime(data['date']).dt.date
    data['date'] = pd.to_datetime(data['date'])

    data['CumReturn'] = data.groupby('permno')['Rn'].apply(lambda x: x.shift(1).rolling(window=11).sum()).reset_index(level=0, drop=True)

    # Assign deciles based on CumReturn within each month
    data['momentum_rank'] = data.groupby('date')['CumReturn'].transform(lambda x: pd.qcut(x, 10, labels=False, duplicates='drop') + 1)

    # Value weights within each decile-month group
    data['vw_weight'] = data.groupby(['date', 'momentum_rank'])['mcap'].transform(lambda x: x / x.sum())

    # Value-weighted return per decile per month
    data['weighted_ret'] = data['Rn'] * data['vw_weight']
    decile_returns = data.groupby(['date', 'momentum_rank'], group_keys=False)['weighted_ret'].sum().reset_index(name='ret_vw')

    # Construct long-short momentum portfolio: top 3 deciles - bottom 3
    long = decile_returns[decile_returns['momentum_rank'] >= 8].groupby('date')['ret_vw'].mean()
    short = decile_returns[decile_returns['momentum_rank'] <= 3].groupby('date')['ret_vw'].mean()

    MOM_return = (long - short).reset_index(name='MOM_return')
    return MOM_return
