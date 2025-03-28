
import matplotlib.pyplot as plt
import pandas as pd

def signal_returns(df, date, return_col, title, label, saving_path):

    df = df[[date, return_col]].dropna()

    plt.figure(figsize=(12, 6))
    plt.plot(df[date], df[return_col], label=label, linewidth=1.5)
    plt.axhline(0, color='gray', linestyle='--', linewidth=1)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Monthly Return')
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(f"{saving_path}")
    plt.show()




def cum_return(
        df,
        return_col,
        saving_path,
        date_col='date',
        label='Strategy',
        start_date=None,
        end_date=None,
        title='Cumulative Return',
        ylabel='Cumulative Return'
        ):

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    # Optional filtering
    if start_date:
        df = df[df[date_col] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df[date_col] < pd.to_datetime(end_date)]

    # Cumulative return calculation
    df['cumulative_return'] = (1 + df[return_col]).cumprod()

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(df[date_col], df['cumulative_return'], label=label)
    plt.axhline(y=1, color='gray', linestyle='--', linewidth=1)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{saving_path}")
    plt.show()
