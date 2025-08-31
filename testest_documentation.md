# Documentation for `testest.py`

## Overview
This document provides an overview of the functions and code sections in the `testest.py` script. Each section includes a description of the function's purpose, parameters, and usage examples.

---

## Functions and Code Sections

### **指定root_symbol、起訖期間，導入期貨價量資料**
- **Description**: Sets the environment variables for futures data and ingests the data using `zipline`.
- **Environment Variables**:
  - `future`: Specifies the futures symbols.
  - `mdate`: Specifies the date range.
- **Command**: `!zipline ingest -b tquant_future`

---

### **get_futures_prices**
- **Description**: Fetches OHLCV (Open, High, Low, Close, Volume) data for futures contracts within a specified period.
- **Parameters**:
  - `start_dt` (str): Start date in `yyyy-mm-dd` format.
  - `end_dt` (str): End date in `yyyy-mm-dd` format.
  - `bundle` (str): Data source, default is `tquant-future`.
- **Example**:
  ```python
  df_ohlcv = get_futures_prices(start_dt='2020-01-01', end_dt='2024-12-31', bundle='tquant_future')
  ```

---

### **get_root_symbol_ohlcv**
- **Description**: Extracts specific data fields (e.g., close, volume) for a given root symbol from the OHLCV DataFrame.
- **Parameters**:
  - `df_ohlcv` (pd.DataFrame): DataFrame containing OHLCV data.
  - `get_field` (str): Field to extract (e.g., "close").
  - `get_root_symbol` (str): Root symbol to filter (e.g., "TX").
- **Example**:
  ```python
  df_close = get_root_symbol_ohlcv(df_ohlcv, get_field='close', get_root_symbol='TX')
  ```

---

### **get_continues_futures_price**
- **Description**: Generates continuous futures price data based on specified parameters.
- **Parameters**:
  - `root_symbol` (str): Futures root symbol (e.g., "TX").
  - `offset` (int): Offset for contract series (0 for near-month, 1 for next-month, etc.).
  - `roll_style` (str): Rolling method (e.g., "calendar").
  - `adjustment` (str): Adjustment method (e.g., "add", "mul", or None).
  - `field` (str): Data field (e.g., "close").
  - `start_dt` (str): Start date in `yyyy-mm-dd` format.
  - `end_dt` (str): End date in `yyyy-mm-dd` format.
  - `bundle` (str): Data source (e.g., "tquant-future").
- **Example**:
  ```python
  df_con_fut = get_continues_futures_price(root_symbol='TX', offset=0, roll_style='calendar', adjustment='add', field='volume', start_dt='2018-01-01', end_dt='2025-03-16', bundle='tquant_future')
  ```

---

### **get_futures_institutions_data**
- **Description**: Retrieves trading data for major institutions (e.g., foreign investors, investment trusts, dealers) in the futures market.
- **Parameters**:
  - `root_symbol` (list): List of root symbols (e.g., ["TX"]).
  - `start_dt` (str): Start date in `yyyy-mm-dd` format.
  - `end_dt` (str): End date in `yyyy-mm-dd` format.
- **Example**:
  ```python
  df_fut_inst = institution_future_data.get_futures_institutions_data(root_symbol=['TX'], st='2025-01-01')
  ```

---

### **get_futures_oi_trader_data**
- **Description**: Retrieves trading data for large traders in the futures market, including top 5 and top 10 traders.
- **Parameters**:
  - `root_symbol` (list): List of root symbols (e.g., ["TX"]).
  - `contract_code` (str): Contract code (e.g., "N" for near-month contracts, "A" for all contracts).
  - `start_dt` (str): Start date in `yyyy-mm-dd` format.
  - `end_dt` (str): End date in `yyyy-mm-dd` format.
- **Example**:
  ```python
  df_fut_repttrader = rept_trader_future_data.get_futures_oi_trader_data(root_symbol=['TX'], contract_code='A', st='2025-01-01')
  ```

---

### **Data Integration and Visualization**
- **Description**: Combines continuous futures price data with institutional and large trader data, and visualizes the results using Plotly.
- **Steps**:
  1. Fetch continuous futures price data.
  2. Fetch institutional data.
  3. Fetch large trader data.
  4. Combine the data into a single DataFrame.
  5. Visualize the data using subplots.
- **Example**:
  ```python
  df = pd.concat([cont_fut, df_fut_inst.set_index('mdate')[['oi_con_ls_net_finis', 'oi_con_ls_net_dealers', 'oi_con_ls_net_funds']]], axis=1).dropna()
  ```

---

## Notes
- The script uses `zipline` for data ingestion and `plotly` for visualization.
- Ensure that the required environment variables and dependencies are set up before running the script.

---

## References
- [Zipline Documentation](https://www.zipline.io/)
- [Plotly Documentation](https://plotly.com/python/)
