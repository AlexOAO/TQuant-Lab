#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台指期貨散戶多空比情緒指標策略 - 純策略版本 (修復版)
移除所有風險控制機制，探討最純粹的策略效果
比較單利 vs 複利計算方式，並與台灣加權指數 Buy and Hold 策略比較
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os
import sys
import subprocess
from matplotlib.font_manager import FontProperties

warnings.filterwarnings('ignore')

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 關鍵參數設定 ====================
# 可調整的關鍵參數，修改這裡即可測試不同配置
POSITION_SIZE = 1  # 持倉口數 (1口=1元標準化, 2口=2元風險暴露, 3口=3元風險暴露)
SIGNAL_THRESHOLD = 0.0  # 散戶情緒進場閾值 (越負越嚴格)
EXIT_SIGNAL_THRESHOLD = 0.0  # 散戶情緒出場閾值 (越正越嚴格)
INITIAL_CAPITAL = 1_000_000  # 初始資金 (TWD)
START_DATE = '2013-01-01'  # 策略開始日期 (受散戶情緒數據限制)
SPLIT_DATE = '2020-01-01'  # 樣本內外分割線
END_DATE = '2025-06-30'  # 策略結束日期

print(f"🔧 當前參數設定：")
print(f"   持倉口數: {POSITION_SIZE}口 (風險暴露: {POSITION_SIZE}倍)")
print(f"   進場閾值: {SIGNAL_THRESHOLD} (散戶情緒)")
print(f"   出場閾值: {EXIT_SIGNAL_THRESHOLD} (散戶情緒)")
print(f"   初始資金: {INITIAL_CAPITAL:,} TWD")
print(f"   回測期間: {START_DATE} ~ {END_DATE}")

# ==================== 環境設定 ====================
os.environ['TEJAPI_BASE'] = ''
os.environ['TEJAPI_KEY'] = ''

# 設定期貨商品和時間範圍
os.environ['future'] = 'TX MTX'
os.environ['mdate'] = '20100101 20250630'

class PureStrategyConfig:
    """純策略配置"""
    def __init__(self):
        # 使用全域參數
        self.start_date = START_DATE
        self.split_date = SPLIT_DATE
        self.end_date = END_DATE
        self.initial_capital = INITIAL_CAPITAL
        self.position_size = POSITION_SIZE  # 改為使用全域參數

        # 策略信號閾值
        self.signal_threshold = SIGNAL_THRESHOLD  # 使用全域參數
        self.exit_signal_threshold = EXIT_SIGNAL_THRESHOLD  # 使用全域參數

print("=== 台指期貨散戶多空比情緒指標策略 - 純策略版本 (修復版) ===")
print("移除所有風險控制機制，探討最純粹的策略效果")
print("📅 數據範圍：受散戶情緒數據限制，實際從2013年開始")
print("樣本內：2013/01/01-2019/12/31 (7年)")
print("樣本外：2020/01/01-2025/06/30 (5.5年)")
print("⚠️  注意：原計畫從2010年開始，但散戶情緒數據僅從2013年可用")
print(f"📊 當前配置：{POSITION_SIZE}口標準化1元 (可調整 POSITION_SIZE 參數)")
print(f"🎯 進場條件：散戶情緒 < {SIGNAL_THRESHOLD}")
print(f"🎯 出場條件：散戶情緒 > {EXIT_SIGNAL_THRESHOLD}")

# ==================== 執行zipline ingest ====================
try:
    # 執行zipline ingest
    result = subprocess.run([sys.executable, '-m', 'zipline', 'ingest', '-b', 'tquant_future'], 
                          capture_output=True, text=True, cwd='/Users/lixiangwei/Desktop/python_tqlabw')
    print("Zipline ingest 執行完成")
    if result.returncode != 0:
        print(f"Zipline ingest 警告: {result.stderr}")
except Exception as e:
    print(f"執行zipline ingest時發生錯誤: {e}")

# ==================== 導入真實數據模組 ====================
try:
    from zipline.TQresearch.futures_price import get_continues_futures_price
    from zipline.TQresearch.futures_package import retail_long_short_ratio
    ZIPLINE_AVAILABLE = True
    print("zipline模組導入成功")
except ImportError:
    print("zipline模組未安裝，程式將終止。")
    print("請確保已安裝zipline和相關的TQresearch模組。")
    ZIPLINE_AVAILABLE = False
    sys.exit(1)

# 1. 載入真實數據
def load_real_data():
    """載入真實的市場數據和散戶情緒數據"""
    print("載入真實TEJ數據...")
    
    # 設定時間範圍 - 情緒指標數據從2013年開始
    start_date = START_DATE
    end_date = END_DATE
    
    try:
        # 載入台指期貨價格數據
        print("正在載入台指期貨價格數據...")
        print("📊 使用 mul 調整的原因:")
        print("  ✅ 保持報酬率準確性 (相對價格變化正確)")
        print("  ✅ 適合績效計算 (投入1元的績效變化)")
        print("  ⚠️  注意: 絕對價格水準有偏差 (約27%)")
        print("  💡 用途: 策略績效比較，非價格水準分析")
        
        price_data = get_continues_futures_price(
            root_symbol='TX',
            offset=0,
            roll_style='calendar',
            adjustment= 'mul',  # 使用乘法調整   
            field='close',
            start_dt=start_date,
            end_dt=end_date,
            bundle='tquant_future'
        )
        
        if price_data is None or price_data.empty:
            raise ValueError("無法載入台指期貨價格數據")
        
        print(f"台指期貨價格數據載入成功: {len(price_data)} 筆記錄")
        print(f"價格數據類型: {type(price_data)}")
        
        # 確保價格數據有正確的結構
        if isinstance(price_data, pd.Series):
            # 如果是Series，創建完整的OHLCV DataFrame
            tx_data = pd.DataFrame({
                'close': price_data.values,
                'open': price_data.values,
                'high': price_data.values * 1.005,  # 假設高價比收盤價高0.5%
                'low': price_data.values * 0.995,   # 假設低價比收盤價低0.5%
                'volume': 100000  # 假設固定成交量
            }, index=price_data.index)
            price_data = tx_data
            print("已將Series轉換為完整的OHLCV DataFrame")
        elif isinstance(price_data, pd.DataFrame):
            # 如果是DataFrame，需要正確重命名欄位
            print(f"原始欄位: {list(price_data.columns)}")
            if len(price_data.columns) == 1:
                # 只有一個欄位，當作收盤價
                col_name = price_data.columns[0]
                tx_data = pd.DataFrame({
                    'close': price_data[col_name].values,
                    'open': price_data[col_name].values,
                    'high': price_data[col_name].values * 1.005,
                    'low': price_data[col_name].values * 0.995,
                    'volume': 100000
                }, index=price_data.index)
                price_data = tx_data
                print(f"已將單欄位DataFrame (欄位: {col_name}) 轉換為完整的OHLCV DataFrame")
        
        print(f"轉換後價格數據欄位: {list(price_data.columns)}")
        
        # 載入散戶多空比數據
        print("正在載入散戶多空比數據...")
        sentiment_data = retail_long_short_ratio(root_symbol='MTX')
        
        if sentiment_data is None or sentiment_data.empty:
            raise ValueError("無法載入散戶多空比數據")
        
        print(f"散戶多空比數據載入成功: {len(sentiment_data)} 筆記錄")
        
        # 合併數據 - 使用價格數據的索引為主
        combined_data = price_data.copy()
        
        # 添加散戶多空比 (sentiment_data 是 Series，直接使用)
        print(f"散戶情緒數據類型: {type(sentiment_data)}")
        
        if isinstance(sentiment_data, pd.Series):
            # 重新索引散戶情緒數據以匹配價格數據
            sentiment_aligned = sentiment_data.reindex(price_data.index, method='ffill')
            combined_data['sentiment_ratio'] = sentiment_aligned
        else:
            # 如果是DataFrame，嘗試找到合適的欄位
            if 'ratio' in sentiment_data.columns:
                sentiment_aligned = sentiment_data['ratio'].reindex(price_data.index, method='ffill')
                combined_data['sentiment_ratio'] = sentiment_aligned
            else:
                print("警告：散戶多空比數據中找不到'ratio'欄位")
                # 使用第一個數值欄位作為替代
                numeric_cols = sentiment_data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    sentiment_aligned = sentiment_data[numeric_cols[0]].reindex(price_data.index, method='ffill')
                    combined_data['sentiment_ratio'] = sentiment_aligned
                    print(f"使用欄位 '{numeric_cols[0]}' 作為散戶多空比")
                else:
                    raise ValueError("散戶多空比數據中找不到數值欄位")
        
        # 移除含有NaN的行
        combined_data = combined_data.dropna()
        
        if combined_data.empty:
            raise ValueError("合併後的數據為空")
        
        print(f"真實數據載入完成: {len(combined_data)} 筆有效記錄")
        print(f"數據時間範圍: {combined_data.index[0]} 到 {combined_data.index[-1]}")
        
        return combined_data
        
    except Exception as e:
        print(f"載入真實數據時發生錯誤: {e}")
        print("程式將終止，請檢查數據源設定")
        sys.exit(1)

class PureRetailSentimentStrategy:
    """純散戶情緒策略（移除所有風險控制）- 市值曲線 vs 權益曲線 - 單利計算版本"""
    
    def __init__(self, config):
        self.config = config
        self.position = 0  # 持倉狀態 (0: 無持倉, N: 做多N口)
        self.entry_price = 0
        self.market_value = 1.0  # 當前市值（含未實現損益），從1開始
        self.equity_value = 1.0  # 策略權益（純粹策略績效），從1開始
        self.daily_risk_free_rate = 0.01 / 252  # 日化無風險利率
        
        # 單利累積變數
        self.cumulative_realized_pnl = 0.0  # 累積已實現損益（單利）
        
        # 交易記錄
        self.trades = []
        self.equity_curve = []
        
    def generate_signal(self, sentiment_value):
        """生成交易信號（只基於散戶情緒）"""
        if sentiment_value < -self.config.signal_threshold:
            return 'buy'  # 散戶過度悲觀，做多
        elif sentiment_value > self.config.exit_signal_threshold:
            return 'sell'  # 散戶過度樂觀，出場
        return 'hold'
    
    def execute_trade(self, date, price, signal, sentiment):
        """執行交易（只負責記錄交易狀態，不計算市值）"""
        # 這個方法現在只負責記錄交易狀態，市值計算在run_backtest中統一處理
        pass  # 交易邏輯已移到run_backtest方法中
    
    def run_backtest(self, data):
        """執行回測 - 正確實現市值曲線與權益曲線的區別"""
        print(f"\n=== 開始純策略回測 (市值曲線 vs 權益曲線) ===")
        
        # 使用已合併的數據
        combined_data = data.copy()
        
        print(f"回測期間: {combined_data.index[0]} ~ {combined_data.index[-1]}")
        print(f"共同交易日期數: {len(combined_data)}")
        print("💡 市值曲線：投資組合實際市場價值（含未實現損益實時波動）")
        print("💡 權益曲線：策略淨值表現（只在平倉時實現損益）")
        print(f"💡 計算方式：單利累積（{self.config.position_size}口標準化1元）")
        print("⚠️  風險控制: 已全部移除 (無停損、停利、時間停損)")
        
        for i, (date, row) in enumerate(combined_data.iterrows()):
            price = row['close']
            sentiment = row['sentiment_ratio']
            
            # 生成信號
            signal = self.generate_signal(sentiment)
            
            # === 交易邏輯處理 ===
            if signal == 'buy' and self.position == 0:
                # 進場做多 N口
                self.position = self.config.position_size  # 使用配置的口數
                self.entry_price = price
                print(f"{date.strftime('%Y-%m-%d')}: 進場做多 {self.config.position_size}口 @ {price:.2f} (情緒:{sentiment:.3f})")
                
            elif signal == 'sell' and self.position > 0:
                # 出場平倉 - 實現損益（單利累積）
                single_contract_return = (price - self.entry_price) / self.entry_price
                total_return = single_contract_return * self.position  # N口總報酬
                # 單利累積已實現損益
                self.cumulative_realized_pnl += total_return
                # 權益曲線更新
                self.equity_value = 1.0 + self.cumulative_realized_pnl
                
                print(f"{date.strftime('%Y-%m-%d')}: 出場平倉 {self.position}口 @ {price:.2f} 單筆報酬:{total_return:.4f} 累積報酬:{self.cumulative_realized_pnl:.4f} 權益:{self.equity_value:.4f}")
                
                # 記錄交易
                self.trades.append({
                    'entry_price': self.entry_price,
                    'exit_date': date,
                    'exit_price': price,
                    'trade_return': total_return,
                    'cumulative_pnl': self.cumulative_realized_pnl,
                    'equity_value': self.equity_value
                })
                
                self.position = 0
                self.entry_price = 0
            
            # === 市值曲線與權益曲線的正確區別 ===
            
            # 1. 市值曲線：永遠反映當前投資組合的市場價值
            if self.position > 0:
                # 持倉期間：已實現損益 + 未實現損益
                single_contract_return = (price - self.entry_price) / self.entry_price
                total_unrealized_return = single_contract_return * self.position
                self.market_value = 1.0 + self.cumulative_realized_pnl + total_unrealized_return
            else:
                # 無持倉：只有已實現損益
                self.market_value = 1.0 + self.cumulative_realized_pnl
            
            # 2. 權益曲線：只在平倉時更新，持倉期間保持不變
            # self.equity_value 只在上面平倉時更新，這裡不做任何操作
            
            # 計算日報酬率
            if i > 0:
                daily_market_return = (self.market_value / self.equity_curve[-1]['market_value']) - 1
                daily_equity_return = (self.equity_value / self.equity_curve[-1]['equity_value']) - 1
            else:
                daily_market_return = 0
                daily_equity_return = 0
            
            # 記錄曲線數據
            self.equity_curve.append({
                'date': date,
                'market_value': self.market_value,
                'equity_value': self.equity_value,
                'daily_market_return': daily_market_return,
                'daily_equity_return': daily_equity_return,
                'price': price,
                'sentiment': sentiment,
                'position': self.position,
                'cumulative_pnl': self.cumulative_realized_pnl
            })
        
        # 轉換為DataFrame
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df.set_index('date', inplace=True)
        
        print(f"成功生成 {len(equity_df)} 天的完整數據")
        print(f"最終市值: {equity_df.iloc[-1]['market_value']:.4f}")
        print(f"最終權益: {equity_df.iloc[-1]['equity_value']:.4f}")
        print(f"市值總報酬率: {(equity_df.iloc[-1]['market_value'] - 1) * 100:.2f}%")
        print(f"權益總報酬率: {(equity_df.iloc[-1]['equity_value'] - 1) * 100:.2f}%")
        
        return equity_df

class TXBuyAndHoldStrategy:
    """台指期貨 TX Buy and Hold 策略 - 同時計算市值曲線和權益曲線"""
    
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        
    def run_backtest(self, data):
        """執行 Buy and Hold 回測 - 市值曲線 vs 權益曲線"""
        print(f"\n=== 執行台指期貨 TX Buy and Hold 策略 (市值曲線 vs 權益曲線) ===")
        
        # 使用與策略數據相同的時間範圍
        start_date = data.index[0]
        end_date = data.index[-1]
        
        print(f"台指期貨 Buy and Hold 期間: {start_date} 到 {end_date}")
        print(f"買入價格: {data['close'].iloc[0]:.2f}")
        print(f"賣出價格: {data['close'].iloc[-1]:.2f}")
        print(f"💡 Buy & Hold: {POSITION_SIZE}口持倉，1元標準化（與情緒策略一致）")
        print("💡 Buy & Hold: 市值曲線 = 權益曲線 (無策略調整)")
        
        # 使用真實的TX台指期貨價格數據
        tx_prices = data['close'].copy()
        
        # 計算每日市值和權益（Buy & Hold下兩者相同）
        equity_curve = []
        cumulative_realized_pnl = 0.0  # 累積已實現損益（與情緒策略一致）
        
        for i, (date, price) in enumerate(tx_prices.items()):
            if i == 0:
                # 第一天
                daily_market_return = 0
                daily_equity_return = 0
                market_value = 1.0
                equity_value = 1.0
            else:
                # 計算日報酬率（N口標準化到1元，與情緒策略一致）
                single_contract_return = (price / tx_prices.iloc[i-1]) - 1
                total_return = single_contract_return * POSITION_SIZE  # N口總報酬
                cumulative_realized_pnl += total_return  # 累積報酬
                market_value = 1.0 + cumulative_realized_pnl  # 1元標準化
                equity_value = 1.0 + cumulative_realized_pnl  # Buy & Hold下兩者相同
                daily_market_return = total_return  # N口的日報酬
                daily_equity_return = total_return  # 相同
            
            equity_curve.append({
                'date': date,
                'market_value': market_value,
                'equity_value': equity_value,  # Buy & Hold: 市值 = 權益
                'daily_market_return': daily_market_return,
                'daily_equity_return': daily_equity_return,
                'tx_price': price
            })
        
        result_df = pd.DataFrame(equity_curve)
        result_df.set_index('date', inplace=True)
        
        print(f"TX Buy and Hold 策略回測完成，共 {len(result_df)} 天")
        print(f"最終市值: {result_df.iloc[-1]['market_value']:.4f}")
        print(f"最終權益: {result_df.iloc[-1]['equity_value']:.4f}")
        print(f"總報酬率: {(result_df.iloc[-1]['market_value'] - 1) * 100:.2f}%")
        
        return result_df
        
        # 使用真實的TX台指期貨價格數據
        tx_prices = data['close'].copy()
        
        print(f"買入日期: {start_date}")
        print(f"買入價格: {tx_prices.iloc[0]:.2f}")
        print(f"賣出日期: {end_date}")
        print(f"賣出價格: {tx_prices.iloc[-1]:.2f}")
        print("💡 Buy & Hold: 市值曲線 = 權益曲線 (買入後持有到底)")
        
        # 計算每日市值和權益
        equity_curve = []
        market_value = 1.0  # 從1開始
        equity_value = 1.0  # Buy & Hold策略中，權益曲線 = 市值曲線
        
        for i, (date, price) in enumerate(tx_prices.items()):
            if i == 0:
                # 第一天
                market_daily_return = 0
                equity_daily_return = 0
                market_value = 1.0
                equity_value = 1.0
            else:
                # 計算日報酬率
                daily_return = (price / tx_prices.iloc[i-1]) - 1
                market_value = market_value * (1 + daily_return)
                equity_value = equity_value * (1 + daily_return)  # Buy & Hold中兩者相同
                market_daily_return = daily_return
                equity_daily_return = daily_return
            
            equity_curve.append({
                'date': date,
                'market_value': market_value,
                'equity_value': equity_value,
                'market_daily_return': market_daily_return,
                'equity_daily_return': equity_daily_return,
                'tx_price': price
            })
        
        result_df = pd.DataFrame(equity_curve)
        result_df.set_index('date', inplace=True)
        
        print(f"TX Buy and Hold 策略回測完成，共 {len(result_df)} 天")
        print(f"最終市值: {result_df.iloc[-1]['market_value']:.4f}")
        print(f"最終權益: {result_df.iloc[-1]['equity_value']:.4f}")
        print(f"總報酬率: {(result_df.iloc[-1]['market_value'] - 1) * 100:.2f}%")
        
        return result_df

class PerformanceAnalyzer:
    """績效分析器 (修正版)"""
    
    def __init__(self, risk_free_rate=0.01):
        """
        初始化績效分析器
        Args:
            risk_free_rate: 年化無風險利率，預設1%
        """
        self.risk_free_rate = risk_free_rate
        self.daily_risk_free_rate = risk_free_rate / 252  # 日化無風險利率
    
    def calculate_performance_metrics(self, equity_data, equity_column, period_name):
        """計算績效指標 (基於市值日報酬率版本)"""
        if len(equity_data) == 0:
            return {}
            
        initial_value = 1.0  # 基準從1開始
        final_value = equity_data.iloc[-1][equity_column]
        
        # 1. 計算總報酬率 (Total Return)
        total_return = (final_value - initial_value) / initial_value * 100
        
        # 2. 計算日報酬率序列
        market_values = equity_data[equity_column]
        daily_returns = market_values.pct_change().dropna()
        
        # 3. 時間計算
        actual_days = (equity_data.index[-1] - equity_data.index[0]).days
        trading_days = len(equity_data)
        years = trading_days / 252  # 使用交易日計算年數
        
        if len(daily_returns) > 1 and years > 0:
            # 4. 年化報酬率 (Annualized Return)
            annualized_return = (final_value / initial_value) ** (1/years) - 1
            annualized_return_pct = annualized_return * 100
            
            # 5. 波動率計算
            volatility = daily_returns.std()
            annualized_volatility = volatility * np.sqrt(252) * 100  # 年化波動率(%)
            
            # 6. 夏普比率 (Sharpe Ratio)
            if volatility != 0:
                sharpe_ratio = (annualized_return - self.risk_free_rate) / (annualized_volatility/100)
            else:
                sharpe_ratio = 0
            
            # 7. 索提諾比率 (Sortino Ratio)
            negative_returns = daily_returns[daily_returns < 0]
            if len(negative_returns) > 0:
                downside_deviation = np.sqrt(np.mean(negative_returns**2)) * np.sqrt(252)
                sortino_ratio = (annualized_return - self.risk_free_rate) / downside_deviation if downside_deviation != 0 else 0
            else:
                sortino_ratio = np.inf if annualized_return > self.risk_free_rate else 0
            
            # 8. 最大回撤 (Maximum Drawdown)
            rolling_max = market_values.expanding().max()
            drawdown = (market_values - rolling_max) / rolling_max
            max_drawdown = drawdown.min() * 100
            
            # 9. 卡瑪比率 (Calmar Ratio)
            calmar_ratio = (annualized_return - self.risk_free_rate) / abs(max_drawdown/100) if max_drawdown != 0 else 0
            
            # 10. 風報比
            return_to_volatility_ratio = annualized_return / (annualized_volatility/100) if annualized_volatility != 0 else 0
            return_to_mdd_ratio = annualized_return / abs(max_drawdown/100) if max_drawdown != 0 else 0
            
        else:
            annualized_return_pct = 0
            annualized_volatility = 0
            sharpe_ratio = 0
            sortino_ratio = 0
            max_drawdown = 0
            calmar_ratio = 0
            return_to_volatility_ratio = 0
            return_to_mdd_ratio = 0
        
        # 調試信息
        print(f"\n🔍 {period_name} 詳細計算 (市值日報酬率版本):")
        print(f"  期初市值: {initial_value:.4f}")
        print(f"  期末市值: {final_value:.4f}")
        print(f"  實際日數: {actual_days}")
        print(f"  交易日數: {trading_days}")
        print(f"  年數(交易日): {years:.3f}")
        print(f"  無風險利率: {self.risk_free_rate*100:.1f}%")
        print(f"  總報酬率: {total_return:.2f}%")
        if years > 0:
            print(f"  年化報酬率: {annualized_return_pct:.2f}%")
        else:
            print(f"  年化報酬率: 無法計算 (時間過短)")
        
        metrics = {
            'period': period_name,
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'annualized_return': annualized_return_pct,
            'volatility': annualized_volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'return_to_volatility_ratio': return_to_volatility_ratio,
            'return_to_mdd_ratio': return_to_mdd_ratio,
            'actual_days': actual_days,
            'trading_days': trading_days,
            'risk_free_rate': self.risk_free_rate
        }
        
        # 打印結果
        print(f"\n{period_name} 績效 (市值日報酬率版本):")
        print(f"  期初市值: {initial_value:.4f}")
        print(f"  期末市值: {final_value:.4f}")
        print(f"  總報酬率: {total_return:.2f}%")
        print(f"  年化報酬率: {annualized_return_pct:.2f}%")
        print(f"  年化波動率: {metrics['volatility']:.2f}%")
        print(f"  夏普比率: {sharpe_ratio:.2f}")
        print(f"  索提諾比率: {sortino_ratio:.2f}")
        print(f"  最大回撤: {max_drawdown:.2f}%")
        print(f"  卡瑪比率: {calmar_ratio:.2f}")
        print(f"  風報比(波動): {return_to_volatility_ratio:.2f}")
        print(f"  風報比(回撤): {return_to_mdd_ratio:.2f}")
        print(f"  💡 投入100萬元的績效: {(final_value - 1) * 1000000:,.0f} TWD")
        
        return metrics

def create_comparison_charts(results, taiex_results, config):
    """創建比較圖表 - 市值曲線 vs 權益曲線"""
    print("\n=== 生成比較圖表 (市值曲線 vs 權益曲線) ===")
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 12))
    fig.suptitle(f'台指期貨散戶情緒策略：市值曲線 vs 權益曲線 vs Buy & Hold ({POSITION_SIZE}口標準化)', fontsize=16, fontweight='bold')
    
    # 樣本分割線
    split_date = pd.to_datetime(config.split_date)
    
    # 1. 市值曲線 vs 權益曲線 vs Buy & Hold 比較 (左上角)
    ax1 = axes[0, 0]
    
    # 繪製三條曲線
    ax1.plot(results.index, results['market_value'], label='情緒策略-市值曲線', linewidth=2.5, color='blue', alpha=0.8)
    ax1.plot(results.index, results['equity_value'], label='情緒策略-權益曲線', linewidth=2, color='darkblue', linestyle='--', alpha=0.9)
    ax1.plot(taiex_results.index, taiex_results['market_value'], label='TX Buy & Hold', linewidth=2, color='red', alpha=0.8)
    
    # 樣本分割線
    ax1.axvline(x=split_date, color='orange', linestyle=':', alpha=0.8, linewidth=2, label='樣本分割線')
    
    # 設置圖表
    ax1.set_title('市值曲線 vs 權益曲線 vs Buy & Hold 比較', fontsize=12, fontweight='bold')
    ax1.set_ylabel('投入1元的價值')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 2. 散戶情緒指標散點圖分析
    ax2 = axes[0, 1]
    
    # 準備散點圖數據
    dates = results.index
    sentiment_values = results['sentiment']
    position_status = results['position']
    
    # 將日期轉換為數值以便散點圖使用
    import matplotlib.dates as mdates
    x_numeric = mdates.date2num(dates)
    
    # 根據持倉狀態和情緒強度分類數據點
    no_position_mask = position_status == 0
    in_position_mask = position_status > 0
    
    # 根據情緒強度進一步分類
    strong_bullish = sentiment_values < -0.1
    medium_bullish = (sentiment_values >= -0.1) & (sentiment_values < -0.05)
    weak_bullish = (sentiment_values >= -0.05) & (sentiment_values < 0)
    bearish_neutral = sentiment_values >= 0
    
    # 繪製不同類別的散點
    ax2.scatter(x_numeric[no_position_mask & strong_bullish], sentiment_values[no_position_mask & strong_bullish], 
               c='lightgray', s=15, alpha=0.6, label='無持倉', edgecolors='none')
    ax2.scatter(x_numeric[no_position_mask & medium_bullish], sentiment_values[no_position_mask & medium_bullish], 
               c='lightgray', s=12, alpha=0.6, edgecolors='none')
    ax2.scatter(x_numeric[no_position_mask & weak_bullish], sentiment_values[no_position_mask & weak_bullish], 
               c='lightgray', s=10, alpha=0.6, edgecolors='none')
    ax2.scatter(x_numeric[no_position_mask & bearish_neutral], sentiment_values[no_position_mask & bearish_neutral], 
               c='lightgray', s=8, alpha=0.6, edgecolors='none')
    
    # 持倉狀態的點（藍色系）
    ax2.scatter(x_numeric[in_position_mask & strong_bullish], sentiment_values[in_position_mask & strong_bullish], 
               c='darkblue', s=25, alpha=0.8, label='強烈看多持倉', edgecolors='none')
    ax2.scatter(x_numeric[in_position_mask & medium_bullish], sentiment_values[in_position_mask & medium_bullish], 
               c='blue', s=20, alpha=0.7, label='中等看多持倉', edgecolors='none')
    ax2.scatter(x_numeric[in_position_mask & weak_bullish], sentiment_values[in_position_mask & weak_bullish], 
               c='lightblue', s=15, alpha=0.6, label='弱看多持倉', edgecolors='none')
    
    # 添加關鍵閾值線
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1, label='中性線')
    ax2.axhline(y=-0.05, color='orange', linestyle='--', alpha=0.7, linewidth=1, label='弱信號閾值')
    ax2.axhline(y=-0.1, color='red', linestyle='--', alpha=0.7, linewidth=1, label='強信號閾值')
    
    # 添加樣本分割線
    split_date_num = mdates.date2num(split_date)
    ax2.axvline(x=split_date_num, color='orange', linestyle=':', alpha=0.8, linewidth=2, label='樣本分割線')
    
    # 設置x軸格式
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator(2))
    
    ax2.set_title('散戶情緒指標散點圖（顏色=持倉狀態，大小=信號強度）', fontsize=12, fontweight='bold')
    ax2.set_ylabel('散戶情緒指標')
    ax2.set_xlabel('年份')
    ax2.legend(loc='upper right', fontsize=8, ncol=2)
    ax2.grid(True, alpha=0.3)
    
    # 設置y軸範圍以更好展示數據分布
    y_min, y_max = sentiment_values.min(), sentiment_values.max()
    y_range = y_max - y_min
    ax2.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)
    
    # 3. 回撤分析
    ax3 = axes[1, 0]
    # 計算回撤 - 分別計算市值曲線和權益曲線的回撤
    rolling_max_market = results['market_value'].expanding().max()
    drawdown_market = (results['market_value'] - rolling_max_market) / rolling_max_market * 100
    
    rolling_max_equity = results['equity_value'].expanding().max()
    drawdown_equity = (results['equity_value'] - rolling_max_equity) / rolling_max_equity * 100
    
    rolling_max_taiex = taiex_results['market_value'].expanding().max()
    drawdown_taiex = (taiex_results['market_value'] - rolling_max_taiex) / rolling_max_taiex * 100
    
    ax3.fill_between(results.index, drawdown_market, 0, alpha=0.4, color='blue', label='情緒策略-市值回撤')
    ax3.fill_between(results.index, drawdown_equity, 0, alpha=0.6, color='darkblue', label='情緒策略-權益回撤')
    ax3.fill_between(taiex_results.index, drawdown_taiex, 0, alpha=0.4, color='red', label='TX回撤')
    ax3.axvline(x=split_date, color='orange', linestyle=':', alpha=0.8, linewidth=2)
    ax3.set_title('回撤比較：市值曲線 vs 權益曲線', fontsize=12, fontweight='bold')
    ax3.set_ylabel('回撤 (%)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 績效對比表
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # 計算整體績效
    analyzer = PerformanceAnalyzer()
    
    # 情緒策略績效 - 分別計算市值曲線和權益曲線
    market_metrics = analyzer.calculate_performance_metrics(results, 'market_value', '情緒策略-市值')
    equity_metrics = analyzer.calculate_performance_metrics(results, 'equity_value', '情緒策略-權益')
    
    # TX績效
    taiex_metrics = analyzer.calculate_performance_metrics(taiex_results, 'market_value', 'TX Buy & Hold')
    
    # 創建表格數據
    table_data = [
        ['指標', '市值曲線', '權益曲線', 'TX Buy & Hold'],
        ['總報酬率', f"{market_metrics['total_return']:.2f}%", f"{equity_metrics['total_return']:.2f}%", f"{taiex_metrics['total_return']:.2f}%"],
        ['年化報酬率', f"{market_metrics['annualized_return']:.2f}%", f"{equity_metrics['annualized_return']:.2f}%", f"{taiex_metrics['annualized_return']:.2f}%"],
        ['夏普比率', f"{market_metrics['sharpe_ratio']:.2f}", f"{equity_metrics['sharpe_ratio']:.2f}", f"{taiex_metrics['sharpe_ratio']:.2f}"],
        ['最大回撤', f"{market_metrics['max_drawdown']:.2f}%", f"{equity_metrics['max_drawdown']:.2f}%", f"{taiex_metrics['max_drawdown']:.2f}%"],
        ['投入100萬效果', f"{(market_metrics['final_value'] - 1) * 1000000:,.0f}", f"{(equity_metrics['final_value'] - 1) * 1000000:,.0f}", f"{(taiex_metrics['final_value'] - 1) * 1000000:,.0f}"]
    ]
    
    table = ax4.table(cellText=table_data, cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.2)
    
    # 設置表格樣式
    for i in range(len(table_data)):
        for j in range(len(table_data[i])):
            cell = table[i, j]
            if i == 0:  # 標題行
                cell.set_facecolor('#4CAF50')
                cell.set_text_props(weight='bold', color='white', fontsize=12)
            else:
                cell.set_facecolor('#F8F9FA')
    
    ax4.set_title('績效對比表：市值曲線 vs 權益曲線', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(f'策略績效比較_市值vs權益曲線_{POSITION_SIZE}口標準化.png', dpi=300, bbox_inches='tight')
    print(f"圖表已保存：策略績效比較_市值vs權益曲線_{POSITION_SIZE}口標準化.png")
    plt.show()

def main():
    """主程式"""
    # 配置
    config = PureStrategyConfig()
    
    print(f"\n純策略配置（移除風險控制）：")
    print(f"  實際期間：{config.start_date} ~ {config.end_date} (受數據限制)")
    print(f"  樣本內期間：{config.start_date} ~ {config.split_date[:-1] + '31'} (7年)")
    print(f"  樣本外期間：{config.split_date} ~ {config.end_date} (5.5年)")
    print(f"  初始資金：{config.initial_capital:,} TWD")
    print(f"  交易標的：TX")
    print(f"  持倉口數：{config.position_size}口 (風險暴露: {config.position_size}倍)")
    print(f"  📊 數據限制：散戶情緒數據只從2013年開始，非原計畫的2010年")
    print(f"  ⚠️  已移除：停損、停利、時間停損")
    
    try:
        # 1. 載入真實數據
        if ZIPLINE_AVAILABLE:
            data = load_real_data()
        else:
            print("無法載入真實數據，程式終止")
            return
        
        # 2. 執行純策略回測
        pure_strategy = PureRetailSentimentStrategy(config)
        results = pure_strategy.run_backtest(data)
        
        # 3. 執行台指期貨 TX Buy and Hold 策略
        buy_hold_strategy = TXBuyAndHoldStrategy(config.initial_capital)
        taiex_results = buy_hold_strategy.run_backtest(data)
        
        # 4. 績效分析
        print("\n" + "="*80)
        print("純策略績效分析 vs TX期貨 Buy & Hold")
        print("="*80)
        
        analyzer = PerformanceAnalyzer()
        split_date = pd.to_datetime(config.split_date).tz_localize('UTC')
        
        # 樣本內外分析
        print("\n📊 情緒策略績效分析 (基於市值日報酬率計算)：")
        print("="*60)
        
        in_sample = results[results.index < split_date]
        out_sample = results[results.index >= split_date]
        
        in_sample_perf = analyzer.calculate_performance_metrics(in_sample, 'market_value', "樣本內 (2010-2019)")
        out_sample_perf = analyzer.calculate_performance_metrics(out_sample, 'market_value', "樣本外 (2020-2025)")
        
        print("\n📊 TX期貨 Buy & Hold 績效分析：")
        print("="*60)
        
        # 處理台指數據的時區問題
        if taiex_results.index.tz is None:
            taiex_split_date = split_date.tz_localize(None) if split_date.tz is not None else split_date
        else:
            taiex_split_date = split_date.tz_localize('UTC') if split_date.tz is None else split_date
        
        taiex_in_sample = taiex_results[taiex_results.index < taiex_split_date]
        taiex_out_sample = taiex_results[taiex_results.index >= taiex_split_date]
        
        taiex_in_perf = analyzer.calculate_performance_metrics(taiex_in_sample, 'market_value', "樣本內 (2010-2019)")
        taiex_out_perf = analyzer.calculate_performance_metrics(taiex_out_sample, 'market_value', "樣本外 (2020-2025)")
        
        # 5. 生成比較圖表
        create_comparison_charts(results, taiex_results, config)
        
        print("\n✅ 純策略分析完成！(基於市值日報酬率計算)")
        print(f"📊 生成圖表：策略績效比較_市值vs權益曲線_{POSITION_SIZE}口標準化.png")
        
        # 總結報告
        print(f"\n🏆 總結報告 (基於市值日報酬率計算)：")
        final_strategy_value = results.iloc[-1]['market_value']
        final_tx_value = taiex_results.iloc[-1]['market_value']
        
        print(f"情緒策略 最終市值: {final_strategy_value:.4f}")
        print(f"情緒策略 總報酬率: {(final_strategy_value - 1) * 100:.2f}%")
        print(f"TX期貨 Buy & Hold 最終市值: {final_tx_value:.4f}")
        print(f"TX期貨 Buy & Hold 總報酬率: {(final_tx_value - 1) * 100:.2f}%")
        print(f"\n💰 投入100萬元的效果：")
        print(f"情緒策略: {(final_strategy_value - 1) * 1000000:,.0f} TWD")
        print(f"TX期貨 Buy & Hold: {(final_tx_value - 1) * 1000000:,.0f} TWD")
        
    except Exception as e:
        print(f"\n❌ 執行過程中出現錯誤：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
