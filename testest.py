# %%
import os
import tejapi

os.environ['TEJAPI_BASE'] = 'https://api.tej.com.tw'
os.environ['TEJAPI_KEY'] = 'YOUR KEY'

import TejToolAPI
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %% [markdown]
# ### **指定root_symbol、起訖期間，導入期貨價量資料**

# %%
os.environ['future'] = 'TX MTX TMF M1F E4F TE ZEF TF ZFF XIF SHF SOF BTF GTF G2F'
os.environ['mdate'] = '20130101 20250321'
!zipline ingest -b tquant_future

# %% [markdown]
# ### **導入 取得期貨合約價格、取得期貨連續月合約價格、取得期貨三大法人、取得其期貨大額交易人的函數**

# %%
from zipline.TQresearch.futures_price import get_futures_prices, get_root_symbol_ohlcv, get_continues_futures_price
from zipline.TQresearch.futures_smart_money_positions import institution_future_data,  rept_trader_future_data

# %% [markdown]
# ### <span style="color:#ff1493; font-weight:bold;">**get_futures_prices** </span>***`(start_dt: str, end_dt: str, bundle: str)`***
# - 獲取指定期間內 bundle 中所有期貨合約的開、高、低、收、量數據。
# 
# - `參數                                                                            `
#     - **start_dt** - 起始日期，格式為 "yyyy-mm-dd"，指定資料的查詢開始時間。
#     - **end_dt** - 結束日期，格式為 "yyyy-mm-dd"，指定資料的查詢結束時間。
#     - **bundle** - 指定提取數據的資料源，預設為 `tquant-future` 。
# 

# %%
df_ohlcv = get_futures_prices(start_dt='2020-01-01', end_dt='2024-12-31', bundle='tquant_future')
df_ohlcv.tail(3)

# %% [markdown]
# ### <span style="color:#ff1493; font-weight:bold;">**get_root_symbol_ohlcv** </span>***`(df_ohlcv: pd.DataFrame, get_field: str, get_root_symbol: str)`***
# 
# - 從輸入的期貨合約價量資料表（DataFrame）中，提取指定的期貨商品代碼與資料欄位(開,高,低,收,量)的數據。
#                       
# - `參數                                                                                                                `
#     - **df_ohlcv** - 期貨合約的價量數據表，包含 OHLCV（開、高、低、收、成交量）等資訊的 DataFrame。
#     - **get_field** - 指定要提取的數據欄位，例如 "close"、"volume" 等。
#     - **get_root_symbol** - 指定要篩選的期貨商品代碼（root symbol），例如 "TX" 表示台指期、"TE" 表示電子期、"TF" 表示金融期。
# 

# %%
df_close = get_root_symbol_ohlcv(df_ohlcv,get_field='close', get_root_symbol='TX')
df_close.tail(3)

# %% [markdown]
# ### <span style="color:#ff1493; font-weight:bold;">**get_continues_futures_price** </span>***`(root_symbol: str, offset: int, roll_style: str, adjustment: str, start_dt: str, end_dt: str, bundle: str)`***
#   
# - 生成連續期貨價格數據。根據指定的root_symbol，構建對應的期貨連續合約序列，並根據滾動規則與調整方式計算連續價格。
#                       
# - `參數                                                                                                                           `
#     - **root_symbol** - 期貨商品的root symbol，例如 "TX"（台指期）。
#     - **offset** - 期貨合約序列的偏移量，**0** 表示主連續合約（近月），**1** 表示次連續合約（次月），依此類推。
#     - **roll_style** - 期貨合約的滾動方式，目前支援 **"calendar"**，即根據日曆時間進行合約更替。
#     - **adjustment** - 連續合約的價格調整方式，可選 **"add"**（加法調整）、**"mul"**（乘法調整）或 **None**（無調整）。
#     - **field** - 建立連續合約的數據欄位，例如 **"open"**、**"high"**、**"low"**、**"close"**、**"volume"** 等。
#     - **start_dt** - 起始日期，格式為 **"yyyy-mm-dd"**，指定資料的查詢開始時間。
#     - **end_dt** - 結束日期，格式為 **"yyyy-mm-dd"**，指定資料的查詢結束時間。
#     - **bundle** - 指定數據來源，例如 **"tquant-future"**。

# %%
df_con_fut = get_continues_futures_price(root_symbol='TX',offset=0,roll_style='calendar',adjustment='add',field='volume', start_dt='2018-01-01', end_dt='2025-03-16',bundle='tquant_future')
df_con_fut.tail(3)

# %% [markdown]
# ### <span style="color:#ff1493; font-weight:bold;">**get_futures_institutions_data** </span>***`(root_symbol: list ,start_dt: str, end_dt: str)`***
#   
# - 獲取期貨市場主要機構（如外資、投信、自營商）的交易數據，包括交易量與未平倉口數，依據指定的 root_symbol 及時間範圍查詢。
#                       
# - `參數                                                                                                  `
#     - **root_symbol** - 期貨商品的 root symbol，例如 "TX"（台指期），可傳入多個合約代碼作批次查詢。
#     - **start_dt** - 起始日期，格式為 "yyyy-mm-dd"，指定資料的查詢開始時間。
#     - **end_dt** - 結束日期，格式為 "yyyy-mm-dd"，指定資料的查詢結束時間。
# ---
# <details>
#   <summary>root_symbol商品代碼查詢（點選展開）</summary>
#     
# | **商品代號 (root_symbol)** | **中文名稱 (Chinese Name)** |
# |------------------|---------------------------|
# | BTF  | 臺灣生技期貨 |
# | E4F  | 臺灣永續期貨 |
# | ETFF | ETF期貨 |
# | ETFO | ETF選擇權 |
# | ETFOC | ETF選擇權—C |
# | ETFOP | ETF選擇權—P |
# | F1F  | 英國富時100期貨 |
# | G2F  | 富櫃200期貨 |
# | GTF  | 櫃買期貨 |
# | M1F  | 臺灣中型100期貨 |
# | MTX  | 小型臺指期貨 |
# | SHF  | 航運期貨 |
# | SOF  | 半宏高30期貨 |
# | SPF  | 美國標普500期貨 |
# | SXF  | 美國賽城半宏高貨 |
# | TE   | 電子期貨 |
# | TEO  | 電子選擇權 |
# | TEOC | 電子選擇權—C |
# | TEOP | 電子選擇權—P |
# | TF   | 金融期貨 |
# | TFO  | 金融選擇權 |
# | TFOC | 金融選擇權—C |
# | TFOP | 金融選擇權—P |
# | TJF  | 東評期貨 |
# | TMF  | 微型臺指期貨 |
# | TX   | 臺股期貨 |
# | TXO  | 臺指選擇權 |
# | TXOC | 臺指選擇權—C |
# | TXOP | 臺指選擇權—P |
# | UDF  | 美國道瓊期貨 |
# | UNF  | 美國那斯達克100期貨 |
# | XIF  | 非金電期貨 |
# | ZEF  | 小型電子期貨 |
# | ZFF  | 小型金融期貨 |
# | derivatives | 期貨+選擇權總表 |
# | futures | 期貨總表 |
# | options | 選擇權總表 |
# 
# 

# %% [markdown]
# 
# <details>
#   <summary>中英文欄位名稱對照表說明（點選展開）</summary>
# 
# | **英文欄位名稱**                        | *中文欄位名稱**                       |
# |----------------------------------------|-----------------------------------------------|
# | mdate                                  | 年月日                                         |
# | root_symbol                            | 名稱                                           |
# | oi_amt_long_dealers                    | 自營商多方未平倉契約金額                        |
# | oi_amt_long_finis                      | 外資多方未平倉契約金額                        |
# | oi_amt_long_funds                      | 投信多方未平倉契約金額                        |
# | oi_amt_long_major_inst                 | 三大法人多方未平倉契約金額                    |
# | oi_amt_ls_net_dealers                  | 自營商多空未平倉契約淨額                      |
# | oi_amt_ls_net_finis                    | 外資多空未平倉契約淨額                        |
# | oi_amt_ls_net_funds                    | 投信多空未平倉契約淨額                        |
# | oi_amt_ls_net_major_inst               | 三大法人多空未平倉契約淨額                    |
# | oi_amt_short_dealers                   | 自營商空方未平倉契約金額                      |
# | oi_amt_short_finis                     | 外資空方未平倉契約金額                        |
# | oi_amt_short_funds                     | 投信空方未平倉契約金額                        |
# | oi_amt_short_major_inst                | 三大法人空方未平倉契約金額                    |
# | oi_con_long_dealers                    | 自營商多方未平倉口數                          |
# | oi_con_long_finis                      | 外資多方未平倉口數                          |
# | oi_con_long_funds                      | 投信多方未平倉口數                          |
# | oi_con_long_major_inst                 | 三大法人多方未平倉口數                      |
# | oi_con_long_pct_dealers                | 自營商多方未平倉口數持有比                    |
# | oi_con_long_pct_finis                  | 外資多方未平倉口數持有比                    |
# | oi_con_long_pct_funds                  | 投信多方未平倉口數持有比                    |
# | oi_con_long_pct_major_inst             | 三大法人多方未平倉口數持有比                  |
# | oi_con_ls_net_dealers                  | 自營商多空未平倉口數淨額                    |
# | oi_con_ls_net_finis                    | 外資多空未平倉口數淨額                      |
# | oi_con_ls_net_funds                    | 投信多空未平倉口數淨額                      |
# | oi_con_ls_net_major_inst               | 三大法人多空未平倉口數淨額                  |
# | oi_con_short_dealers                   | 自營商空方未平倉口數                          |
# | oi_con_short_finis                     | 外資空方未平倉口數                          |
# | oi_con_short_funds                     | 投信空方未平倉口數                          |
# | oi_con_short_major_inst                | 三大法人空方未平倉口數                      |
# | oi_con_short_pct_dealers               | 自營商空方未平倉口數持有比                    |
# | oi_con_short_pct_finis                 | 外資空方未平倉口數持有比                    |
# | oi_con_short_pct_funds                 | 投信空方未平倉口數持有比                    |
# | oi_con_short_pct_major_inst            | 三大法人空方未平倉口數持有比                  |
# | volume_amt_long_dealers                | 自營商多方交易契約金額                        |
# | volume_amt_long_finis                  | 外資多方交易契約金額                        |
# | volume_amt_long_funds                  | 投信多方交易契約金額                        |
# | volume_amt_long_major_inst             | 三大法人多方交易契約金額                    |
# | volume_amt_ls_net_dealers              | 自營商多空交易契約金額淨額                  |
# | volume_amt_ls_net_finis                | 外資多空交易契約金額淨額                    |
# | volume_amt_ls_net_funds                | 投信多空交易契約金額淨額                    |
# | volume_amt_ls_net_major_inst           | 三大法人多空交易契約金額淨額                |
# | volume_amt_short_dealers               | 自營商空方交易契約金額                        |
# | volume_amt_short_finis                 | 外資空方交易契約金額                        |
# | volume_amt_short_funds                 | 投信空方交易契約金額                        |
# | volume_amt_short_major_inst            | 三大法人空方交易契約金額                    |
# | volume_con_long_dealers                | 自營商多方交易口數                          |
# | volume_con_long_finis                  | 外資多方交易口數                          |
# | volume_con_long_funds                  | 投信多方交易口數                          |
# | volume_con_long_major_inst             | 三大法人多方交易口數                        |
# | volume_con_long_pct_dealers            | 自營商多方交易口數比重                      |
# | volume_con_long_pct_finis              | 外資多方交易口數比重                        |
# | volume_con_long_pct_funds              | 投信多方交易口數比重                        |
# | volume_con_long_pct_major_inst         | 三大法人多方交易口數比重                    |
# | volume_con_ls_net_dealers              | 自營商多空交易口數淨額                      |
# | volume_con_ls_net_finis                | 外資多空交易口數淨額                        |
# | volume_con_ls_net_funds                | 投信多空交易口數淨額                        |
# | volume_con_ls_net_major_inst           | 三大法人多空交易口數淨額                    |
# | volume_con_short_dealers               | 自營商空方交易口數                          |
# | volume_con_short_finis                 | 外資空方交易口數                          |
# | volume_con_short_funds                 | 投信空方交易口數                          |
# | volume_con_short_major_inst            | 三大法人空方交易口數                        |
# | volume_con_short_pct_dealers           | 自營商空方交易口數比重                      |
# | volume_con_short_pct_finis             | 外資空方交易口數比重                        |
# | volume_con_short_pct_funds             | 投信空方交易口數比重                        |
# | volume_con_short_pct_major_inst        | 三大法人空方交易口數比重                    |
# 

# %%
# 取得期貨三大法人資料 
df_fut_inst = institution_future_data.get_futures_institutions_data(root_symbol=['TX'], st='2025-01-01')
df_fut_inst.tail(3)  

# %% [markdown]
# ### <span style="color:#ff1493; font-weight:bold;">**get_futures_oi_trader_data** </span>***`(root_symbol: list ,start_dt: str, end_dt: str)`***
#   
# - 獲取期貨市場大額交易人（包含前五大、十大交易人，前五大、十大特定法人）的交易數據，包括交易量與未平倉口數，依據指定的 root_symbol 及時間範圍查詢。
#                       
# - `參數                                                                                                  `
#     - **root_symbol** - 期貨商品的 root symbol，例如 "TX"（台指期），可傳入多個合約代碼作批次查詢。
#     - **contact_code** - 期貨商品的近月或所有合約代碼，例如 輸入 **`N`** 為取得近月期貨合約大額交易人未沖銷部位；輸入 **`A`** 為所有期貨合約。
#     - **start_dt** - 起始日期，格式為 "yyyy-mm-dd"，指定資料的查詢開始時間。
#     - **end_dt** - 結束日期，格式為 "yyyy-mm-dd"，指定資料的查詢結束時間。
# - `Note                                                                                                  `
#     - coid 欄位說明
#         - Z + root_symbol + _N  : 該期貨合約近月的大額交易人未沖銷部位。
#         - Z + root_symbol + _A : 該期貨合約近月與所有遠月的大額交易人未沖銷部位。 
# ---

# %% [markdown]
# <details>
#   <summary>root_symbol商品代碼查詢（點選展開）</summary>
#     
# | **商品代號 (root_symbol)** | **現貨標的代碼/名稱** |
# |-------|---------------------------------|
# | CA    | 1303                            |
# | CB    | 2002                            |
# | CC    | 2303                            |
# | CD    | 2330                            |
# | CE    | 2881                            |
# | CF    | 1301                            |
# | CG    | 2324                            |
# | CH    | 2409                            |
# | CJ    | 2880                            |
# | CK    | 2882                            |
# | CL    | 2886                            |
# | CM    | 2887                            |
# | CN    | 2891                            |
# | CQ    | 1216                            |
# | CR    | 1402                            |
# | CS    | 1605                            |
# | CU    | 2323                            |
# | CW    | 2352                            |
# | CX    | 2371                            |
# | CY    | 2408                            |
# | CZ    | 2603                            |
# | DA    | 2609                            |
# | DB    | 2610                            |
# | DC    | 2801                            |
# | DD    | 2888                            |
# | DE    | 2890                            |
# | DF    | 1101                            |
# | DG    | 1326                            |
# | DH    | 2317                            |
# | DI    | 2337                            |
# | DJ    | 2357                            |
# | DK    | 2382                            |
# | DL    | 2412                            |
# | DN    | 2884                            |
# | DO    | 2885                            |
# | DP    | 2892                            |
# | DQ    | 3481                            |
# | DS    | 2353                            |
# | DV    | 2454                            |
# | DW    | 2915                            |
# | DX    | 3231                            |
# | DY    | 1102                            |
# | DZ    | 1210                            |
# | EE    | 1312                            |
# | EG    | 1314                            |
# | EH    | 1319                            |
# | EK    | 1440                            |
# | EM    | 1504                            |
# | EP    | 1590                            |
# | EY    | 1718                            |
# | EZ    | 1722                            |
# | FB    | 2006                            |
# | FC    | 2014                            |
# | FE    | 2027                            |
# | FF    | 2049                            |
# | FG    | 2059                            |
# | FK    | 2105                            |
# | FN    | 2201                            |
# | FQ    | 2301                            |
# | FR    | 2308                            |
# | FS    | 2312                            |
# | FT    | 2313                            |
# | FV    | 2331                            |
# | FW    | 2332                            |
# | FY    | 2340                            |
# | FZ    | 2344                            |
# | GA    | 2347                            |
# | GC    | 2354                            |
# | GH    | 2376                            |
# | GI    | 2377                            |
# | GJ    | 2379                            |
# | GK    | 2385                            |
# | GL    | 2392                            |
# | GM    | 2393                            |
# | GN    | 2401                            |
# | GO    | 2404                            |
# | GR    | 2449                            |
# | GU    | 2455                            |
# | GV    | 2457                            |
# | GW    | 2458                            |
# | GX    | 2474                            |
# | GY    | 2481                            |
# | GZ    | 2485                            |
# | HA    | 2489                            |
# | HB    | 2492                            |
# | HC    | 2498                            |
# | HH     | 2515                           |
# | HI     | 2520                           |
# | HL     | 2542                           |
# | HO     | 2548                           |
# | HQ     | 2605                           |
# | HS     | 2618                           |
# | IA     | 2834                           |
# | IH     | 2913                           |
# | II     | 3006                           |
# | IJ     | 3008                           |
# | IM     | 3019                           |
# | IO     | 3034                           |
# | IP     | 3035                           |
# | IQ     | 3036                           |
# | IR     | 3037                           |
# | IT     | 3042                           |
# | IX     | 3189                           |
# | IY     | 3376                           |
# | IZ     | 3380                           |
# | JB     | 3443                           |
# | JF     | 3533                           |
# | JM     | 3653                           |
# | JN     | 3673                           |
# | JP     | 3702                           |
# | JS     | 4938                           |
# | JW     | 5534                           |
# | JX     | 6005                           |
# | JZ     | 6153                           |
# | KA     | 6176                           |
# | KB     | 6213                           |
# | KC     | 6239                           |
# | KD     | 6271                           |
# | KE     | 6278                           |
# | KF     | 6282                           |
# | KG     | 6285                           |
# | KI     | 8039                           |
# | KK     | 8163                           |
# | KL     | 9904                           |
# | KO     | 9939                           |
# | KP     | 9945                           |
# | KS     | 1477                           |
# | KU     | 1802                           |
# | KW     | 2328                           |
# | LB     | 3044                           |
# | LC     | 3045                           |
# | LE     | 3406                           |
# | LI     | 6269                           |
# | LM     | 9914                           |
# | LO     | 5880                           |
# | LQ     | 2356                           |
# | LR     | 2883                           |
# | LT     | 4904                           |
# | LU     | 4958                           |
# | LV     | 5871                           |
# | LW     | 1476                           |
# | LX     | 2327                           |
# | LY     | 8046                           |
# | MA     | 1707                           |
# | MB     | 2355                           |
# | MJ     | 2360                           |
# | MK     | 2439                           |
# | MQ     | 6257                           |
# | MV     | 9938                           |
# | MY     | 1565                           |
# | NA     | 3105                           |
# | NB     | 3152                           |
# | ND     | 3260                           |
# | NE     | 3264                           |
# | NG     | 3691                           |
# | NI     | 4123                           |
# | NJ     | 5009                           |
# | NL     | 5347                           |
# | NM     | 5371                           |
# | NO     | 5483                           |
# | NQ     | 6121                           |
# | NS     | 6147                           |
# | NU     | 8044                           |
# | NV     | 8069                           |
# | NW     | 8299                           |
# | NY     | 0050                           |
# | OA     | 006205                         |
# | OB     | 006206                         |
# | OD     | 2231                           |
# | OE     | 6116                           |
# | OH     | 6279                           |
# | OJ     | 00636                          |
# | OK     | 00639                          |
# | OL     | 3008                           |
# | OM     | 1565                           |
# | OO     | 00643                          |
# | OP     | 2345                           |
# | OQ     | 6414                           |
# | OR     | 1536                           |
# | OS     | 1909                           |
# | OT     | 3081                           |
# | OU     | 3552                           |
# | OV     | 6274                           |
# | OW     | 6488                           |
# | OX     | 6510                           |
# | OY     | 6510                           |
# | OZ     | 3711                           |
# | PA     | 3227                           |
# | PB     | 6488                           |
# | PC     | 4162                           |
# | PD     | 4736                           |
# | PE     | 5425                           |
# | PF     | 0056                           |
# | PG     | 2633                           |
# | PH     | 5269                           |
# | PI     | 3529                           |
# | PJ     | 2383                           |
# | PK     | 6173                           |
# | PL     | 6182                           |
# | PM     | 8436                           |
# | PN     | 5269                           |
# | PP     | 5457                           |
# | PQ     | 8358                           |
# | PR     | 8086                           |
# | PS     | 3706                           |
# | PT     | 3324                           |
# | PU     | 2454                           |
# | PV     | 6669                           |
# | PW     | 6669                           |
# | PX     | 3293                           |
# | PY     | 3293                           |
# | PZ     | 5274                           |
# | QA     | 5274                           |
# | QB     | 3714                           |
# | QC     | 2606                           |
# | QD     | 3532                           |
# | QE     | 2327                           |
# | QF     | 2330                           |
# | QG     | 2379                           |
# | QH     | 3034                           |
# | QI     | 3105                           |
# | QJ     | 3406                           |
# | QK     | 1907                           |
# | QL     | 3374                           |
# | QM     | 2049                           |
# | QN     | 8299                           |
# | QO     | 1717                           |
# | QP     | 1904                           |
# | QQ     | 3078                           |
# | QR     | 2357                           |
# | QS     | 8046                           |
# | QT     | 2441                           |
# | QU     | 8150                           |
# | QV     | 2338                           |
# | QW     | 2388                           |
# | QX     | 2615                           |
# | QY     | 6547                           |
# | QZ     | 6770                           |
# | RA     | 3017                           |
# | RB     | 5388                           |
# | RC     | 2634                           |
# | RD     | 4128                           |
# | RE     | 4919                           |
# | RF     | 3533                           |
# | RG     | 3653                           |
# | RI     | 00878                          |
# | RJ     | 1609                           |
# | RK     | 2368                           |
# | RL     | 6443                           |
# | RM     | 8454                           |
# | RN     | 4743                           |
# | RO     | 6245                           |
# | RP     | 5904                           |
# | RQ     | 8454                           |
# | RR     | 5904                           |
# | RS     | 3529                           |
# | RU     | 9958                           |
# | RV     | 2308                           |
# | RW     | 3443                           |
# | RX     | 00885                          |
# | RY     | 00923                          |
# | RZ     | 00679B                         |
# | SA     | 1795                           |
# | SB     | 1905                           |
# | SC     | 1477                           |
# | SD     | 1513                           |
# | SE     | 2345                           |
# | SF     | 2383                           |
# | SG     | 00893                          |
# | SI     | 00719B                         |
# | SJ     | 3005                           |
# | SK     | 8112                           |
# | SL     | 2376                           |
# | SM     | 00919                          |
# | SN     | 00929                          |
# | SQ     | 00772B                         |
# | SR     | 0050                           |
# | SS     | 0056                           |
# | SU     | 00940                          |
# | SV     | 2059                           |
# | SW     | 9958                           |
# | SY     | 3680                           |
# | SZ     | 3680                           |
# | UA     | 1503                           |
# | UB     | 6139                           |
# | UC     | 6188                           |
# | UE     | 5876                           |
# | UF     | 6505                           |
# | UG     | 6526                           |
# | UH     | 3017                           |
# | UI     | 6526                           |
# | UJ     | 00937B                         |
# | UK     | 00687B                         |
# | UL     | 3324                           |
# | UM     | 3661                           |
# | UO     | 3661                           |
# | UP     | 6472                           |
# | UQ     | 6472                           |
# | UR     | 00757                          |
# | US     | 00757                          |
# | BRF    | Brent_Crude_Oil               |
# | BTF    | Taiwan_Biotechnology_Index    |
# | E4F    | Taiwan_Sustainability_Index    |
# | F1F    | UK_FTSE100_Index              |
# | G2F    | Taiwan_OTC200_Index           |
# | GDF    | Gold_US                        |
# | GTF    | Taiwan_OTC_Index              |
# | M1F    | Taiwan_Midcap100_Index        |
# | RHF    | USDCNY                         |
# | RTF    | Mini_USDCNY                    |
# | SHF    | Taiwan_Shipping_Index         |
# | SOF    | Taiwan_Semiconductor30_Index  |
# | SPF    | US_S&P500_Index                |
# | SXF    | US_Philadelphia_Semiconductor_Index |
# | TE     | Taiwan_Electron_Index         |
# | TF     | Taiwan_Finance_Index          |
# | TGF    | Gold_TWD                       |
# | TJF    | Tokyo_Stock_Price_Index       |
# | TX     | Taiwan_Stock_Index_Futures    |
# | UDF    | US_Dow_Jones_Index            |
# | UNF    | US_Nasdaq100_Index            |
# | XAF    | AUDUSD                         |
# | XBF    | GBPUSD                         |
# | XEF    | EURUSD                         |
# | XIF    | Taiwan_Non_Financial_Electronics_Index |
# | XJF    | USDJPY                         |
# 

# %% [markdown]
# 
# <details>
#   <summary>中英文欄位名稱對照表說明（點選展開）</summary>
# 
# | 英文名稱                            | 中文名稱                         |
# |-------------------------------------|----------------------------------|
# | coid                                | 期貨名稱                         |
# | mdate                               | 日期                             |
# | expired_month                       | 到期月                           |
# | total_mkt_oi                        | 全市場未沖銷部位                 |
# | top_5_trader_long_oi                | 前五大買方未沖銷部位-交易人       |
# | top_5_trader_short_oi               | 前五大賣方未沖銷部位-交易人       |
# | top_10_trader_long_oi               | 前十大買方未沖銷部位-交易人       |
# | top_10_trader_short_oi              | 前十大賣方未沖銷部位-交易人       |
# | top_5_trader_long_oi_pct            | 前五大買方未沖銷部位%-交易人      |
# | top_5_trader_short_oi_pct           | 前五大賣方未沖銷部位%-交易人      |
# | top_10_trader_long_oi_pct           | 前十大買方未沖銷部位%-交易人      |
# | top_10_trader_short_oi_pct          | 前十大賣方未沖銷部位%-交易人      |
# | top_5_institution_long_oi           | 前五大買方未沖銷部位-特定法人     |
# | top_5_institution_short_oi          | 前五大賣方未沖銷部位-特定法人     |
# | top_10_institution_long_oi          | 前十大買方未沖銷部位-特定法人     |
# | top_10_institution_short_oi         | 前十大賣方未沖銷部位-特定法人     |
# | top_5_institution_long_oi_pct       | 前五大買方未沖銷部位%-特定法人    |
# | top_5_institution_short_oi_pct      | 前五大賣方未沖銷部位%-特定法人    |
# | top_10_institution_long_oi_pct      | 前十大買方未沖銷部位%-特定法人    |
# | top_10_institution_short_oi_pct     | 前十大賣方未沖銷部位%-特定法人    |
# 
# 

# %%
# 取得期貨大額交易人資料
df_fut_repttrader = rept_trader_future_data.get_futures_oi_trader_data(root_symbol=['TX'],contract_code='A',st='2025-01-01')
df_fut_repttrader.tail(3)

# %% [markdown]
# ### 整合期貨連續月合約價格與三大法人籌碼指標

# %% [markdown]
# - 資料整併

# %%
# 參數設定
start_dt = '2024-01-02'
end_dt = pd.Timestamp.now().date().isoformat()
root_symbol = 'TX'

offset = 0
roll_style = 'calendar' 
adjustment = 'add' 
field = 'close'

# 取得台指期貨連續價格資料
cont_fut = get_continues_futures_price(root_symbol, offset, roll_style, adjustment,field, start_dt, end_dt, bundle='tquant_future')
# 取得期貨三大法人資料
df_fut_inst = institution_future_data.get_futures_institutions_data(root_symbol=[root_symbol],st=start_dt)
# 取得期貨大額交易人資料
df_fut_repttrader = rept_trader_future_data.get_futures_oi_trader_data(root_symbol=[root_symbol],st=start_dt,contract_code='A')

df = pd.concat([cont_fut,df_fut_inst.set_index('mdate')[['oi_con_ls_net_finis','oi_con_ls_net_dealers','oi_con_ls_net_funds']],],axis=1).dropna()
df = df.reset_index().rename(columns={'index':'date'})

# %% [markdown]
# - 視覺化圖表

# %%
import plotly.io as pio
pio.renderers.default = "notebook_connected"

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# 創建四個子圖：主圖和三個附圖
fig = make_subplots(
    rows=4, cols=1, 
    shared_xaxes=True,
    vertical_spacing=0.05,  # 調整子圖間距
    row_heights=[0.55, 0.15, 0.15, 0.15],  # 設置主圖和附圖的高度比例
    subplot_titles=("ContinuousFuture (Line Chart)", "oi_con_ls_net_finis", "oi_con_ls_net_dealers", "oi_con_ls_net_funds"),
    shared_yaxes=True
)

# 主圖：折線圖 - ContinuousFuture
fig.add_trace(go.Scatter(x=df["date"], y=df[df.columns[1]], mode='lines', name="ContinuousFuture"),
              row=1, col=1)

# 附圖1：條形圖 - oi_con_ls_net_finis
fig.add_trace(go.Bar(x=df["date"], y=df["oi_con_ls_net_finis"], name="oi_con_ls_net_finis"),
              row=2, col=1)

# 附圖2：條形圖 - top10_trader_oi_net
fig.add_trace(go.Bar(x=df["date"], y=df["oi_con_ls_net_dealers"], name="oi_con_ls_net_dealers"),
              row=3, col=1)

# 附圖3：條形圖 - top10_inst_oi_net
fig.add_trace(go.Bar(x=df["date"], y=df["oi_con_ls_net_funds"], name="oi_con_ls_net_funds"),
              row=4, col=1)

# 更新布局
fig.update_layout(
    title="Plotly Subplots: Main Line Chart and Other Bar Charts",
    xaxis_title="Date",
    yaxis_title="ContinuousFuture",
    xaxis=dict(tickformat="%Y-%m-%d"),
    barmode="group",  # 設置條形圖組合方式
    height=600  # 設置圖表總高度
)

fig.show()

# %%


# %%


# %%



