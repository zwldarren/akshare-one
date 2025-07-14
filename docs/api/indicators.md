# 技术指标

技术指标模块提供常见的技术分析指标计算功能，需要通过`akshare_one.indicators`模块调用：

```python
from akshare_one.indicators import (
    get_sma, get_ema, get_rsi, get_macd, get_bollinger_bands, get_stoch, get_atr,
    get_cci, get_adx, get_willr, get_ad, get_adosc, get_obv, get_mom, get_sar,
    get_tsf, get_apo, get_aroon, get_aroonosc, get_bop, get_cmo, get_dx, get_mfi,
    get_minus_di, get_minus_dm, get_plus_di, get_plus_dm, get_ppo, get_roc,
    get_rocp, get_rocr, get_rocr100, get_trix, get_ultosc
)
```

!!! note
    - `simple`计算方式支持以下指标: SMA, EMA, RSI, MACD, Bollinger Bands, Stochastic, ATR, CCI, ADX
    - 其他指标仅支持`talib`计算方式，需要额外安装[TA-Lib](https://ta-lib.org/install/)依赖并使用`pip install akshare-one[talib]`安装

- **简单移动平均线(SMA)**: `get_sma(df, window=20, calculator_type="talib")`
- **指数移动平均线(EMA)**: `get_ema(df, window=20, calculator_type="talib")`
- **相对强弱指数(RSI)**: `get_rsi(df, window=14, calculator_type="talib")`
- **移动平均收敛发散指标(MACD)**: `get_macd(df, fast=12, slow=26, signal=9, calculator_type="talib")`
- **布林带(Bollinger Bands)**: `get_bollinger_bands(df, window=20, std=2, calculator_type="talib")`
- **随机指标(Stochastic Oscillator)**: `get_stoch(df, window=14, smooth_d=3, smooth_k=3, calculator_type="talib")`
- **平均真实波幅(ATR)**: `get_atr(df, window=14, calculator_type="talib")`
- **商品通道指数(CCI)**: `get_cci(df, window=14, calculator_type="talib")`
- **平均方向性指标(ADX)**: `get_adx(df, window=14, calculator_type="talib")`
- **威廉指标(Williams' %R)**: `get_willr(df, window=14, calculator_type="talib")`
- **蔡金A/D线(Chaikin A/D Line)**: `get_ad(df, calculator_type="talib")`
- **蔡金A/D振荡器(Chaikin A/D Oscillator)**: `get_adosc(df, fast_period=3, slow_period=10, calculator_type="talib")`
- **能量潮(On Balance Volume)**: `get_obv(df, calculator_type="talib")`
- **动量指标(Momentum)**: `get_mom(df, window=10, calculator_type="talib")`
- **抛物线转向指标(Parabolic SAR)**: `get_sar(df, acceleration=0.02, maximum=0.2, calculator_type="talib")`
- **时间序列预测(Time Series Forecast)**: `get_tsf(df, window=14, calculator_type="talib")`
- **绝对价格振荡器(Absolute Price Oscillator)**: `get_apo(df, fast_period=12, slow_period=26, ma_type=0, calculator_type="talib")`
- **阿隆指标(Aroon)**: `get_aroon(df, window=14, calculator_type="talib")`
- **阿隆振荡器(Aroon Oscillator)**: `get_aroonosc(df, window=14, calculator_type="talib")`
- **均势指标(Balance of Power)**: `get_bop(df, calculator_type="talib")`
- **钱德动量振荡器(Chande Momentum Oscillator)**: `get_cmo(df, window=14, calculator_type="talib")`
- **动向指标(Directional Movement Index)**: `get_dx(df, window=14, calculator_type="talib")`
- **资金流量指标(Money Flow Index)**: `get_mfi(df, window=14, calculator_type="talib")`
- **负方向指标(-DI)**: `get_minus_di(df, window=14, calculator_type="talib")`
- **负方向运动(-DM)**: `get_minus_dm(df, window=14, calculator_type="talib")`
- **正方向指标(+DI)**: `get_plus_di(df, window=14, calculator_type="talib")`
- **正方向运动(+DM)**: `get_plus_dm(df, window=14, calculator_type="talib")`
- **价格振荡器百分比(Percentage Price Oscillator)**: `get_ppo(df, fast_period=12, slow_period=26, ma_type=0, calculator_type="talib")`
- **变动率(Rate of change)**: `get_roc(df, window=10, calculator_type="talib")`
- **变动率百分比(Rate of change Percentage)**: `get_rocp(df, window=10, calculator_type="talib")`
- **变动率比率(Rate of change ratio)**: `get_rocr(df, window=10, calculator_type="talib")`
- **变动率比率100刻度(Rate of change ratio 100 scale)**: `get_rocr100(df, window=10, calculator_type="talib")`
- **三重指数平滑平均线的1日变动率(TRIX)**: `get_trix(df, window=30, calculator_type="talib")`
- **终极振荡器(Ultimate Oscillator)**: `get_ultosc(df, window1=7, window2=14, window3=28, calculator_type="talib")`

## 示例

```python
from akshare_one import get_hist_data
from akshare_one.indicators import get_sma, get_macd

# 获取历史数据
df = get_hist_data(symbol="600000", interval="day")

# 计算20日简单移动平均
df_sma = get_sma(df, window=20)

# 计算MACD指标
df_macd = get_macd(df)
```