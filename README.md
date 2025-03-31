# AKShare One

**AKShare One** 是一个标准化中国金融市场数据接口，基于 [AKShare](https://github.com/akfamily/akshare) 二次封装，解决AKShare多数据源输入输出不统一的问题。

## 项目背景

AKShare提供了丰富的中国金融市场数据，但不同数据源的：
- 股票代码格式不统一（如东方财富和新浪使用不同格式）
- 返回数据结构不一致
- 参数命名和用法有差异

AKShare One希望通过统一封装，提供：
- 标准化的股票代码格式
- 一致的数据返回结构
- 简化的API参数

## 核心功能

### 目前仅实现了以下功能：
- 历史数据 (`get_hist_data`)
- 实时行情 (`get_realtime_data`) 
- 个股新闻 (`get_news_data`)
- 财务数据 (资产负债表/利润表/现金流量表)
- 内部交易 (`get_inner_trade_data`)

### 标准化处理
- 统一时间戳为UTC
- 自动处理复权数据
- 清理异常值和缺失数据
- 统一列名和数据类型

## 快速开始

安装：
```bash
pip install akshare-one
```

使用示例：
```python
from akshare_one import get_hist_data, get_realtime_data

# 获取历史数据
df_hist = get_hist_data(
    symbol="600000",  # 统一股票代码格式
    interval="day",
    adjust="qfq"      # 支持前复权
)

# 获取实时数据
df_realtime = get_realtime_data(symbol="600000")
```

## API文档
详细API说明请参考 [docs/api.md](docs/api.md)
