# Ha Finance Record（財務紀錄）

Home Assistant 自訂整合元件，用於個人財務追蹤。管理多個帳戶、記錄交易、設定定期計畫，並透過 HA 側邊欄查看財務概覽。

[English README](README.md)

## 功能特色

- **多帳戶管理** — 建立並管理多個財務帳戶，各自擁有獨立的餘額、交易紀錄與定期計畫。
- **快速記帳** — 輸入金額與備註，按下「確認記錄」即可立即登記收入或支出。
- **定期計畫** — 設定每日、每週、每月或每年自動執行的收入/支出計畫。
- **側邊欄面板** — 基於 Lit Element 的儀表板，位於 HA 側邊欄中，提供交易紀錄、圖表與帳戶管理功能。
- **雙語介面** — 支援英文與繁體中文（zh-Hant），依據 HA 語言設定自動切換。
- **自動化事件** — 於交易記錄、定期執行、餘額調整及低餘額警示時觸發事件，可用於 HA 自動化流程。

## 安裝方式

### HACS（手動新增儲存庫）

1. 在 Home Assistant 中開啟 HACS。
2. 前往 **整合** → 右上角三點選單 → **自訂儲存庫**。
3. 新增 `https://github.com/woowtech-ai-coder/ha_finance`，類型選擇 **Integration**。
4. 搜尋「Finance Record」並安裝。
5. 重新啟動 Home Assistant。

### 手動安裝

1. 將 `custom_components/ha_finance/` 資料夾複製到 Home Assistant 的 `config/custom_components/` 目錄下。
2. 重新啟動 Home Assistant。

## 設定

1. 前往 **設定** → **裝置與服務** → **新增整合**。
2. 搜尋 **Finance Record**。
3. 輸入帳戶名稱、選填帳戶 ID，以及初始餘額。
4. 若需新增更多帳戶，重複上述步驟 — 每個設定項目會建立獨立帳戶。

### 選項設定

設定完成後，點選整合項目上的 **設定** 可以：

- 新增或管理定期計畫（收入/支出排程）
- 編輯帳戶設定
- 刪除帳戶

## 實體

每個帳戶會建立以下實體：

| 平台 | 實體 | 說明 |
|------|------|------|
| `number` | 餘額（Balance） | 目前帳戶餘額 |
| `number` | 快速金額（Quick Amount） | 快速記帳的金額輸入 |
| `text` | 快速備註（Quick Note） | 快速記帳的備註輸入 |
| `button` | 確認記錄（Confirm Record） | 按下以記錄快速交易 |
| `sensor` | 餘額顯示（Balance Display） | 格式化的餘額感測器 |
| `sensor` | 最近交易（Last Transaction） | 最近一筆交易的金額 |
| `sensor` | 最近備註（Last Note） | 最近一筆交易的備註 |
| `sensor` | 最近時間（Last Time） | 最近一筆交易的時間戳記 |

每個定期計畫會新增：

| 平台 | 實體 | 說明 |
|------|------|------|
| `number` | 金額（Amount） | 計畫金額（正數 = 收入，負數 = 支出） |
| `number` | 執行日（Execution Day） | 每週/每月/每年的執行日 |
| `select` | 頻率（Frequency） | 每日 / 每週 / 每月 / 每年 |
| `switch` | 啟用（Active） | 啟用或停用計畫 |
| `sensor` | 下次日期（Next Date） | 下次排程執行日期 |
| `sensor` | 上次執行（Last Executed） | 計畫上次執行時間 |

## 事件

可在自動化中使用以下事件：

| 事件 | 說明 |
|------|------|
| `ha_finance_transaction_added` | 手動記帳時觸發 |
| `ha_finance_recurring_executed` | 定期計畫執行時觸發 |
| `ha_finance_balance_adjusted` | 手動調整餘額時觸發 |
| `ha_finance_low_balance` | 餘額低於設定門檻時觸發 |

## 側邊欄面板

新增至少一個帳戶後，HA 側邊欄會出現 **財務紀錄** 面板，提供：

- 交易紀錄與日期篩選
- 收入/支出圖表
- 帳戶總覽與管理
- 快速記帳功能

## 授權

本專案以現狀提供，供個人使用。
