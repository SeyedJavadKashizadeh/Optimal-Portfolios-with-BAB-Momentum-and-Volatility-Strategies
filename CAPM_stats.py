import numpy as np
import statsmodels.api as sm
import pandas as pd

def sharpe_ratio(series, annualize=True):
    mean = series.mean()
    std = series.std()
    if annualize:
        mean *= 12
        std *= np.sqrt(12)
    return mean / std


def factor_statistics(factor_df, factor_return, market_df, market_return='Rm_e', date='date'):
    tmp = pd.merge(factor_df[[date, factor_return]],
                   market_df[[date, market_return]].drop_duplicates(),
                   on=date, how='left').dropna()
    tmp['const'] = 1

    model = sm.OLS(tmp[factor_return], tmp[['const', market_return]]).fit()

    alpha_annual = model.params['const'] * 12
    beta = model.params[market_return]
    alpha_tstat = model.tvalues['const']
    factor_std_annual = tmp[factor_return].std() * np.sqrt(12)
    factor_mean = tmp[factor_return].mean()
    sharpe = sharpe_ratio(tmp[factor_return])  # <- reused
    idio_vol = (tmp[factor_return] - model.predict()).std() * np.sqrt(12)
    market_rp = tmp[market_return].mean() * 12
    market_vol = tmp[market_return].std() * np.sqrt(12)

    results = {
        'monthly_mean': factor_mean,
        'annual_std': factor_std_annual,
        'annual_alpha': alpha_annual,
        'alpha_tstat': alpha_tstat,
        'sharpe_ratio': sharpe,
        'beta': beta,
        'idio_vol': idio_vol,
        'market_rp': market_rp,
        'market_vol': market_vol
    }

    print(pd.DataFrame([results]).T.rename(columns={0: 'Value'}))
    return results


def fund_statistics(data):
    strategies = ['equal_return', 'rp_return', 'mv_return']
    metrics = {
        'Mean': [],
        'Target Volatility': [],
        'Sharpe Ratio': []
    }
    index = []

    for strat in strategies:
        ret_adj = data[f'{strat}_adj']
        mean_adj = ret_adj.mean() * 12
        std_adj = ret_adj.std() * np.sqrt(12)
        sharpe = sharpe_ratio(ret_adj)

        metrics['Mean'].append(mean_adj)
        metrics['Target Volatility'].append(std_adj)
        metrics['Sharpe Ratio'].append(sharpe)
        index.append(f'{strat}_adj')

    return pd.DataFrame(metrics, index=index)

