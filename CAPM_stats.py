import numpy as np
import statsmodels.api as sm
import pandas as pd

def statistics(factor_df, factor_return, market_df, market_return='Rm_e', date='date'):

    tmp = pd.merge(factor_df[[date, factor_return]], market_df[[date, market_return]].drop_duplicates(), on=date, how='left')
    tmp = tmp.dropna()
    tmp['const'] = 1

    model = sm.OLS(tmp[factor_return], tmp[['const', market_return]]).fit()

    alpha_annual = model.params['const'] * 12
    beta = model.params[market_return]
    alpha_tstat = model.tvalues['const']

    factor_std_annual = tmp[factor_return].std() * np.sqrt(12)
    factor_mean = tmp[factor_return].mean()
    sharpe = factor_mean / factor_std_annual
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

    stats = pd.DataFrame([results])
    pd.options.display.float_format = '{:,.4f}'.format
    print(stats.T.rename(columns={0: 'Value'}))

    return results

