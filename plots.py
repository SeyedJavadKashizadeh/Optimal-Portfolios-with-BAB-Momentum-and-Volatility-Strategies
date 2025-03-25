import matplotlib.pyplot as plt


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
