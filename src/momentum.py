import pandas as pd
import numpy as np


def momentum_portfolio(data, n_port=10, k=3):

    data['logret'] = np.log1p(data['Rn'])
    # Momentum signal: t−12 to t−2 (11 months), skip t−1
    data['signal'] = (
        data.groupby('permno')['logret']
        .transform(lambda x: x.shift(2).rolling(window=11).sum())
    )
    data['signal'] = np.exp(data['signal']) - 1  # Convert log return back to arithmetic

    data = data.dropna(subset=['signal']).copy()

    # Rank into portfolios using signal (Rn)
    data['rank'] = data.groupby('date')['signal'].transform(
        lambda x: pd.qcut(x, n_port, labels=False, duplicates='drop') + 1
    )

    # Define formation date and weights
    data['form_date'] = data['date']
    data['w'] = data.groupby(['form_date', 'rank'])['mcap'].transform(
        lambda x: x / x.sum(min_count=1)
    )

    # Efficient holding expansion: hold for k months
    holding_months = k
    expanded = []

    for i in range(holding_months):
        temp = data.copy()
        temp['date'] = temp['form_date'] + pd.offsets.MonthEnd(i)
        expanded.append(temp)

    holdings = pd.concat(expanded, ignore_index=True)

    # Merge with actual returns for each holding month
    returns = data[['permno', 'date', 'Rn']]
    holdings = holdings.drop(columns=['Rn'], errors='ignore')
    holdings = holdings.merge(returns, on=['permno', 'date'], how='left')
    holdings = holdings.dropna(subset=['Rn'])

    holdings['retw'] = holdings['Rn'] * holdings['w']
    ret_panel = holdings.groupby(['date', 'rank', 'form_date'])['retw'].sum(min_count=1)


    # Average across overlapping portfolios
    ret_panel = ret_panel.groupby(['date', 'rank']).mean().unstack()

    # Momentum by buying winners
    ret_panel['MOM_return'] = (
            ret_panel[[n_port - 2, n_port - 1, n_port]].mean(axis=1)
    )

    # Final output
    ret_panel = ret_panel.reset_index()

    return ret_panel[['date', 'MOM_return']]

