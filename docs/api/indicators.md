# 技术指标

技术指标模块提供常见的技术分析指标计算功能，需要通过 `akshare_one.indicators` 模块调用。

## 导入模块

```python
from akshare_one.indicators import (
    get_sma, get_ema, get_rsi, get_macd, get_bollinger_bands, get_stoch, get_atr,
    get_cci, get_adx, get_willr, get_ad, get_adosc, get_obv, get_mom, get_sar,
    get_tsf, get_apo, get_aroon, get_aroonosc, get_bop, get_cmo, get_dx, get_mfi,
    get_minus_di, get_minus_dm, get_plus_di, get_plus_dm, get_ppo, get_roc,
    get_rocp, get_rocr, get_rocr100, get_trix, get_ultosc
)
```

!!! note "注意事项"
    - 大部分指标函数支持 `calculator_type` 参数，可以是 `talib` 或 `simple`，默认值为 `simple`。
    - `simple` 使用 Python 实现，不需要额外依赖。
    - `talib` 需要额外安装 [TA-Lib](https://ta-lib.org/install/) 依赖并使用 `pip install akshare-one[talib]` 安装。

## 趋势指标

### 简单移动平均线 (SMA)

```python
def get_sma(df: pd.DataFrame, window: int = 20) -> pd.DataFrame
```

### 指数移动平均线 (EMA)

```python
def get_ema(df: pd.DataFrame, window: int = 20) -> pd.DataFrame
```

### 移动平均收敛发散指标 (MACD)

```python
def get_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame
```

### 抛物线转向指标 (Parabolic SAR)

```python
def get_sar(df: pd.DataFrame, acceleration: float = 0.02, maximum: float = 0.2) -> pd.DataFrame
```

### 时间序列预测 (Time Series Forecast)

```python
def get_tsf(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

### 平均方向性指标 (ADX)

```python
def get_adx(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

### 动向指标 (DMI/DX)

```python
def get_dx(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

### 正/负方向指标 (+DI/-DI)

```python
def get_plus_di(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
def get_minus_di(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

### 正/负方向运动 (+DM/-DM)

```python
def get_plus_dm(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
def get_minus_dm(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

### 阿隆指标 (Aroon)

```python
def get_aroon(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

## 动量指标

### 相对强弱指数 (RSI)

```python
def get_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

### 随机指标 (Stochastic Oscillator)

```python
def get_stoch(df: pd.DataFrame, window: int = 14, smooth_d: int = 3, smooth_k: int = 3) -> pd.DataFrame
```

### 商品通道指数 (CCI)

```python
def get_cci(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

### 威廉指标 (Williams' %R)

```python
def get_willr(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

### 动量指标 (Momentum)

```python
def get_mom(df: pd.DataFrame, window: int = 10) -> pd.DataFrame
```

### 变动率 (ROC)

```python
def get_roc(df: pd.DataFrame, window: int = 10) -> pd.DataFrame
def get_rocp(df: pd.DataFrame, window: int = 10) -> pd.DataFrame
def get_rocr(df: pd.DataFrame, window: int = 10) -> pd.DataFrame
def get_rocr100(df: pd.DataFrame, window: int = 10) -> pd.DataFrame
```

### 终极振荡器 (Ultimate Oscillator)

```python
def get_ultosc(df: pd.DataFrame, window1: int = 7, window2: int = 14, window3: int = 28) -> pd.DataFrame
```

### 钱德动量振荡器 (CMO)

```python
def get_cmo(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

### 均势指标 (BOP)

```python
def get_bop(df: pd.DataFrame) -> pd.DataFrame
```

### 三重指数平滑平均线的1日变动率 (TRIX)

```python
def get_trix(df: pd.DataFrame, window: int = 30) -> pd.DataFrame
```

### 绝对价格振荡器 (APO)

```python
def get_apo(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, ma_type: int = 0) -> pd.DataFrame
```

### 价格振荡器百分比 (PPO)

```python
def get_ppo(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, ma_type: int = 0) -> pd.DataFrame
```

### 阿隆振荡器 (Aroon Oscillator)

```python
def get_aroonosc(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

## 波动率指标

### 布林带 (Bollinger Bands)

```python
def get_bollinger_bands(df: pd.DataFrame, window: int = 20, std: int = 2) -> pd.DataFrame
```

### 平均真实波幅 (ATR)

```python
def get_atr(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

## 成交量指标

### 能量潮 (OBV)

```python
def get_obv(df: pd.DataFrame) -> pd.DataFrame
```

### 蔡金 A/D 线 (Chaikin A/D Line)

```python
def get_ad(df: pd.DataFrame) -> pd.DataFrame
```

### 蔡金 A/D 振荡器 (Chaikin A/D Oscillator)

```python
def get_adosc(df: pd.DataFrame, fast_period: int = 3, slow_period: int = 10) -> pd.DataFrame
```

### 资金流量指标 (MFI)

```python
def get_mfi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame
```

## 使用示例

```python
from akshare_one import get_hist_data
from akshare_one.indicators import get_sma, get_macd

# 获取历史数据
df = get_hist_data(symbol="600000", interval="day")

# 计算20日简单移动平均
df_sma = get_sma(df, window=20)
print(df_sma.tail())

# 计算MACD指标
df_macd = get_macd(df)
print(df_macd.tail())
```
