import numpy as np
import pandas as pd

def risk_parity(data, window=12):
    # Step 1: Compute rolling volatility and inverse vol weights
    factors = data[['BAB_return', 'MOM_return', 'IVOL_return']]
    volatility = factors.rolling(window=window).std()
    inv_vol = 1 / volatility
    RP_weights = inv_vol.div(inv_vol.sum(axis=1), axis=0).dropna()

    # Step 2: Align the weights and returns on common dates
    RiskParity = factors.copy()
    common_dates = RP_weights.index.intersection(RiskParity.index)
    RP_weights = RP_weights.loc[common_dates]
    RiskParity = RiskParity.loc[common_dates]

    # Step 3: Compute risk parity return
    RiskParity['rp_return'] = (RP_weights * RiskParity).sum(axis=1)
    RiskParity['date'] = data.loc[common_dates, 'date'].values
    return RiskParity[['date', 'rp_return']]


def fund_return(BAB_factor,mom_factor,idio_vol_factor):

    fund_portfolio = BAB_factor
    fund_portfolio = fund_portfolio.merge(mom_factor, on='date', how='inner').merge(idio_vol_factor, on='date', how='inner')
    fund_portfolio['equal_return'] = fund_portfolio[['BAB_return', 'MOM_return', 'IVOL_return']].mean(axis=1)

    RiskParity = risk_parity(fund_portfolio)
    fund_portfolio = fund_portfolio.merge(RiskParity[['rp_return','date']], on='date', how='inner')

    return fund_portfolio