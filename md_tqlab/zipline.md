# tej環境設置
```python
import os
import subprocess
import sys
# ==================== 環境設定 ====================
os.environ['TEJAPI_BASE'] = ''
os.environ['TEJAPI_KEY'] = ''

# 設定期貨商品和時間範圍
os.environ['future'] = 'TX MTX'
os.environ['mdate'] = '20100101 20250630'
```
```python
# ==================== 執行zipline ingest ====================
try:
    result = subprocess.run([sys.executable, '-m', 'zipline', 'ingest', '-b', 'tquant_future'], 
                          capture_output=True, text=True, cwd='/Users/lixiangwei/Desktop/python_tqlabw')
    print("Zipline ingest 執行完成")
    if result.returncode != 0:
        print(f"Zipline ingest 警告: {result.stderr}")
except Exception as e:
    print(f"執行zipline ingest時發生錯誤: {e}")
```
```python
# ==================== 導入模組 ====================
try:
    from zipline.TQresearch.futures_price import get_continues_futures_price
    from zipline.TQresearch.futures_package import retail_long_short_ratio
    from zipline.TQresearch.futures_smart_money_positions import institution_future_data
    ZIPLINE_AVAILABLE = True
    print("zipline模組導入成功")
except ImportError as e:
    print(f"zipline模組導入失敗: {e}")
    print("請確保已安裝zipline和相關的TQresearch模組。")
    ZIPLINE_AVAILABLE = False
    sys.exit(1)

# ==================== 導入模組 ====================
try:
    from zipline.TQresearch.futures_price import get_continues_futures_price
    from zipline.TQresearch.futures_package import retail_long_short_ratio
    from zipline.TQresearch.futures_smart_money_positions import institution_future_data
    ZIPLINE_AVAILABLE = True
    print("zipline模組導入成功")
except ImportError as e:
    print(f"zipline模組導入失敗: {e}")
    print("請確保已安裝zipline和相關的TQresearch模組。")
    ZIPLINE_AVAILABLE = False
    sys.exit(1)
```