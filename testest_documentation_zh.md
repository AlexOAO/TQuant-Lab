# `testest.py` 文件說明

## 概述
各函數和代碼部分的概述。每個部分包括函數的用途、參數和使用示例。

## 注意事項
- 腳本使用 `zipline` 進行數據導入，使用 `plotly` 進行可視化。
- 在運行腳本之前，請確保已設置所需的環境變量和依賴項。

## 參考資料
- [Zipline 文檔](https://www.zipline.io/)
- [Plotly 文檔](https://plotly.com/python/)

---

## 函數與代碼部分

### **指定 root_symbol、起訖期間，導入期貨價量資料**
- **描述**: 設置期貨數據的環境變量，並使用 `zipline` 導入數據。
- **環境變量**:
  - `future`: 指定期貨符號。
  - `mdate`: 指定日期範圍。
<!-- - **命令**: `!zipline ingest -b tquant_future` -->

---

### **get_futures_prices**
- **描述**: 獲取指定期間內期貨合約的 OHLCV（開、高、低、收、量）數據。
- **參數**:
  - `start_dt` (str): 起始日期，格式為 `yyyy-mm-dd`。
  - `end_dt` (str): 結束日期，格式為 `yyyy-mm-dd`。
  - `bundle` (str): 數據來源，默認為 `tquant-future`。
  
- **示例**:
  ```python
  df_ohlcv = get_futures_prices(
    start_dt='2020-01-01', 
    end_dt='2024-12-31', 
    bundle='tquant_future')
  ```

---

### **get_root_symbol_ohlcv**
- **描述**: 從 OHLCV 數據表中提取指定 root symbol 的特定數據字段（如 close, volume）。
- **參數**:
  - `df_ohlcv` (pd.DataFrame): 包含 OHLCV 數據的 DataFrame。
  - `get_field` (str): 要提取的字段（如 "close"）。
  - `get_root_symbol` (str): 要篩選的 root symbol（如 "TX"）。
- **示例**:
  ```python
  df_close = get_root_symbol_ohlcv(
    df_ohlcv, 
    get_field='close', 
    get_root_symbol='TX')
  ```

---

### **get_continues_futures_price**
- **描述**: 根據指定參數生成連續期貨價格數據。
- **參數**:
  - `root_symbol` (str): 期貨 root symbol（如 "TX"）。
  - `offset` (int): 合約序列偏移量（0 表示近月，1 表示次月，依此類推）。
  - `roll_style` (str): 滾動方式（如 "calendar"）。
  - `adjustment` (str): 調整方式（如 "add", "mul" 或 None）。
  - `field` (str): 數據字段（如 "close"）。
  - `start_dt` (str): 起始日期，格式為 `yyyy-mm-dd`。
  - `end_dt` (str): 結束日期，格式為 `yyyy-mm-dd`。
  - `bundle` (str): 數據來源（如 "tquant-future"）。
- **示例**:
  ```python
  df_con_fut = get_continues_futures_price(
    root_symbol='TX', 
    offset=0, 
    roll_style='calendar', 
    adjustment='mul', 
    field='volume', 
    start_dt='2018-01-01', 
    end_dt='2025-03-16', 
    bundle='tquant_future')
  ```

---

### **get_futures_institutions_data**
- **描述**: 獲取期貨市場主要機構（如外資、投信、自營商）的交易數據。
- **參數**:
  - `root_symbol` (list): root symbol 列表（如 ["TX"]）。
  - `start_dt` (str): 起始日期，格式為 `yyyy-mm-dd`。
  - `end_dt` (str): 結束日期，格式為 `yyyy-mm-dd`。
- **示例**:
  ```python
  df = institution_future_data.get_futures_institutions_data(
    root_symbol=['TX'], 
    st='2025-01-01')
  ```

---

### **get_futures_oi_trader_data**
- **描述**: 獲取期貨市場大額交易人的交易數據，包括前五大和前十大交易人。
- **參數**:
  - `root_symbol` (list): root symbol 列表（如 ["TX"]）。
  - `contract_code` (str): 合約代碼（如 "N" 表示近月合約，"A" 表示所有合約）。
  - `start_dt` (str): 起始日期，格式為 `yyyy-mm-dd`。
  - `end_dt` (str): 結束日期，格式為 `yyyy-mm-dd`。
- **示例**:
  ```python
  df = rept_trader_future_data.get_futures_oi_trader_data(
    root_symbol=['TX'], 
    contract_code='A', 
    st='2025-01-01')
  ```

---

### **數據整合與可視化**
- **描述**: 將連續期貨價格數據與機構和大額交易人數據整合，並使用 Plotly 進行可視化。
- **步驟**:
  1. 獲取連續期貨價格數據。
  2. 獲取機構數據。
  3. 獲取大額交易人數據。
  4. 將數據合併為單一 DataFrame。
  5. 使用子圖進行可視化。
   
- **示例**:
  ```python
  df = pd.concat(
    [cont_fut, 
    df_fut_inst.set_index('mdate')[['oi_con_ls_net_finis', 'oi_con_ls_net_dealers', 
    'oi_con_ls_net_funds']]], 
    axis=1).dropna()
  ```

---

