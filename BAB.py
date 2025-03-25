import pandas as pd
import numpy as np

def bab_return(data):
    # Weights
    data['z'] = data.groupby('date')['beta'].transform(lambda x: x.rank())
    data['z_'] = data['z'] - data.groupby('date')['z'].transform('mean')
    data['k'] = np.abs(data['z_'])
    data['k'] = 2 / data.groupby('date')['k'].transform('sum')
    data['w_H'] = data['k'] * data['z_'] * (data['z_'] > 0)
    data['w_L'] = -data['k'] * data['z_'] * (data['z_'] < 0)

    # Weighted returns and beta
    data['beta_H'] = data['w_H'] * data['beta']
    data['beta_L'] = data['w_L'] * data['beta']
    data['R_H'] = data['w_H'] * data['Rn']
    data['R_L'] = data['w_L'] * data['Rn']
    data['R_H_e'] = data['w_H'] * data['Rn_e']
    data['R_L_e'] = data['w_L'] * data['Rn_e']
    BAB = data.groupby('date')[['R_H', 'R_L', 'R_H_e', 'R_L_e', 'beta_H', 'beta_L']].sum().reset_index()

    # Levered and unlevered returns
    # BAB['BAB1'] = BAB['R_L'] - BAB['R_H']
    BAB['BAB_return'] = BAB['R_L_e'] / BAB['beta_L'] - BAB['R_H_e'] / BAB['beta_H']
    BAB = BAB.rename(columns={'beta_L': 'beta_L_BAB', 'beta_H': 'beta_H_BAB'})

    data = data.merge(BAB[['date', 'beta_H_BAB', 'beta_L_BAB']], on='date', how='left')

    # Strategy weights
    data['BAB_Weights'] = data['w_L'] / data['beta_L_BAB'] - data['w_H'] / data['beta_H_BAB']

    return data, BAB