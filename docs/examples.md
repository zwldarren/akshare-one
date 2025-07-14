# 示例代码

本页提供了一些实用的代码示例，展示如何使用 AKShare One 进行常见的数据分析任务。

## 1. 批量获取多只股票的实时行情

```python
import pandas as pd
from akshare_one import get_realtime_data

def get_batch_realtime_data(symbols):
    """
    批量获取多只股票的实时行情数据
    """
    all_data = []
    for symbol in symbols:
        try:
            df = get_realtime_data(symbol=symbol, source="eastmoney")
            if not df.empty:
                all_data.append(df)
        except Exception as e:
            print(f"获取 {symbol} 数据失败: {e}")
    
    if not all_data:
        return pd.DataFrame()
        
    return pd.concat(all_data, ignore_index=True)

# 股票列表
stock_list = ["600000", "000001", "600519", "000858", "300750"]

# 获取数据
realtime_df = get_batch_realtime_data(stock_list)
print(realtime_df)
```

## 2. 计算并绘制股票的移动平均线

```python
import pandas as pd
import matplotlib.pyplot as plt
from akshare_one import get_hist_data
from akshare_one.indicators import get_sma

# 获取历史数据
symbol = "600036"
hist_df = get_hist_data(symbol=symbol, start_date="2023-01-01", adjust="qfq")

if not hist_df.empty:
    # 计算5日、20日和60日移动平均线
    sma_5 = get_sma(hist_df, window=5)
    sma_20 = get_sma(hist_df, window=20)
    sma_60 = get_sma(hist_df, window=60)

    # 绘制图表
    plt.figure(figsize=(15, 8))
    plt.plot(hist_df['timestamp'], hist_df['close'], label='Close Price')
    plt.plot(hist_df['timestamp'], sma_5, label='SMA 5')
    plt.plot(hist_df['timestamp'], sma_20, label='SMA 20')
    plt.plot(hist_df['timestamp'], sma_60, label='SMA 60')

    plt.title(f'{symbol} - Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()
```
