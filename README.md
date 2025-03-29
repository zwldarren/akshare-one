# AKShare One

**AKShare One** 是一个统一的中国市场数据接口，基于 [AKShare](https://github.com/akfamily/akshare) 构建的标准化数据中台，目的是为了自动转换AKShare各个不同数据源，为各种金融数据提供更方便的接口。

## 功能特性

- 统一的数据格式和符号标准
- 支持多种时间粒度(日/周/月)
- 提供复权选项(前复权/后复权)
- 自动清理和标准化数据

## 快速开始

```python
from akshare_one import get_hist_data

# 获取股票日线数据
df = get_hist_data(
    symbol="600000",  # 股票代码
    interval="day",   # 时间粒度
    adjust="qfq"      # 前复权
)
print(df.head())
```

## 数据源

当前支持的数据源:
- 东方财富(eastmoney) - A股历史行情数据
