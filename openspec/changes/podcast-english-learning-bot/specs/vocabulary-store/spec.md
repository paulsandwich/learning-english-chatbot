## ADDED Requirements

### Requirement: 自動儲存查詢紀錄至單字本
每次成功查詢後，系統 SHALL 自動將查詢詞與解釋儲存至 `vocabulary` 資料表。

#### Scenario: 查詢成功後自動儲存
- **WHEN** query-engine 成功回傳解釋（快取命中或 API 呼叫）
- **THEN** 將 (word, explanation, queried_at) 寫入 `vocabulary` 資料表；若同一詞已存在，更新 `queried_at` 時間戳記

### Requirement: 查看單字本（/list）
系統 SHALL 支援查詢最近 50 筆單字本紀錄。

#### Scenario: 回傳單字清單
- **WHEN** 用戶執行 `/list`
- **THEN** 從 `vocabulary` 資料表取出最近 50 筆，依 `queried_at` 降冪排序，格式為每行「單字 — 中文意思」

### Requirement: 匯出單字本（/export）
系統 SHALL 支援匯出所有單字本紀錄為純文字格式。

#### Scenario: 匯出所有紀錄
- **WHEN** 用戶執行 `/export`
- **THEN** 回傳所有 `vocabulary` 紀錄，每筆格式為「[查詢時間] 單字\n中文意思\n---」

### Requirement: vocabulary 資料表結構
系統 SHALL 使用以下結構建立 `vocabulary` 資料表：

```sql
CREATE TABLE vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    query_key TEXT NOT NULL UNIQUE,  -- lower(strip(word))，防止重複
    explanation TEXT NOT NULL,
    queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Scenario: 資料表初始化
- **WHEN** 資料庫首次初始化
- **THEN** `vocabulary` 資料表成功建立，`query_key` 欄位有 UNIQUE 約束
