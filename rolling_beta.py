import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import os
from numba import njit
import concurrent.futures


@njit
def cov_numba(Rn_e, Rm_e, window=60, min_periods=36):
    n = len(Rn_e)
    beta = np.full(n, np.nan)
    for i in range(min_periods - 1, n):
        start = max(0, i - window + 1)
        end = i + 1
        x = Rm_e[start:end]
        y = Rn_e[start:end]
        count = 0
        x_mean = 0.0
        y_mean = 0.0

        for j in range(start, end):
            # print(f" j in the second loop = {j}")
            if not np.isnan(x[j - start]) and not np.isnan(y[j - start]):
                x_mean += x[j - start]
                y_mean += y[j - start]
                count += 1

        if count >= min_periods:
            x_mean /= count
            y_mean /= count
            cov = 0.0
            var = 0.0
            for j in range(count):
                dx = x[j] - x_mean
                dy = y[j] - y_mean
                cov += dx * dy
                var += dx * dx
            if var != 0:
                beta[i] = cov / var
    return beta

def process_one_permno(group):
    group = group.sort_values('date')
    Rn = np.ascontiguousarray(group['Rn_e'].values, dtype=np.float64)
    Rm = np.ascontiguousarray(group['Rm_e'].values, dtype=np.float64)
    beta_vals = cov_numba(Rn, Rm)
    beta_df = group[['permno', 'date']].copy()
    beta_df['beta'] = beta_vals
    return beta_df

def beta_calculator(data, parquet_path='beta_chunks.parquet', window=60, min_periods=36):

    data = data.copy()
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values(by=['permno', 'date'])
    data = data.dropna(subset=['mcap_l', 'Rn_e', 'Rm_e'])
    data['N'] = data.groupby('permno')['date'].transform('count')
    data = data[data['N'] > 35]

    grouped = list(data.groupby('permno'))

    # Clean previous output file
    if os.path.exists(parquet_path):
        os.remove(parquet_path)

    num_threads = 2

    print("Computing betas in parallel...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = executor.map(lambda g: process_one_permno(g[1]), grouped)


    pqwriter = None

    for counter, beta_df in enumerate(results, 1):
        table = pa.Table.from_pandas(beta_df)
        if pqwriter is None:
            pqwriter = pq.ParquetWriter(parquet_path, table.schema)
        pqwriter.write_table(table)
        if counter % 1000 == 0:
            print(f" {counter} beta blocks written")

    if pqwriter:
        pqwriter.close()

    # ---- Step 3: Merge with original data and calculate alpha ----
    beta_n = pd.read_parquet(parquet_path)
    data = pd.merge(data, beta_n, on=['permno', 'date'], how='left')
    data['beta'] = data.groupby('permno')['beta'].shift(1)
    data['beta_original'] = data['beta']
    data['beta'] = data['beta'].clip(data['beta'].quantile(0.05), data['beta'].quantile(0.95))

    Rn_e_mean = data.set_index('date').groupby('permno')['Rn_e'].rolling(window, min_periods=min_periods).mean().reset_index()
    Rm_e_mean = data.set_index('date').groupby('permno')['Rm_e'].rolling(window, min_periods=min_periods).mean().reset_index()
    Rn_e_mean['Rn_e'] = Rn_e_mean.groupby('permno')['Rn_e'].shift(1)
    Rm_e_mean['Rm_e'] = Rm_e_mean.groupby('permno')['Rm_e'].shift(1)
    Rn_e_mean = Rn_e_mean.rename(columns={'Rn_e': 'Rn_e_mean'})
    Rm_e_mean = Rm_e_mean.rename(columns={'Rm_e': 'Rm_e_mean'})

    data = pd.merge(data, Rn_e_mean, on=['permno', 'date'], how='left')
    data = pd.merge(data, Rm_e_mean, on=['permno', 'date'], how='left')
    data['alpha'] = data['Rn_e_mean'] - (data['beta'] * data['Rm_e_mean'])

    return data
