## ADDED Requirements

### Requirement: 查詢流程（快取優先）
Query Engine SHALL 依以下順序處理每次查詢：快取命中 → FTS 搜尋取得上下文 → Gemini API 呼叫 → 存快取。

#### Scenario: 快取命中
- **WHEN** 用戶查詢的詞（normalized: lower + strip）已存在於 `cache` 資料表
- **THEN** 直接回傳快取中的解釋，不呼叫 Gemini API，回應時間 < 200ms

#### Scenario: 快取未命中，有逐字稿上下文
- **WHEN** 快取未命中，且 transcript-indexer 找到包含此詞的句子
- **THEN** 將「查詢詞 + 逐字稿上下文句子」傳給 Gemini API，取得解釋後存入快取並回傳

#### Scenario: 快取未命中，無逐字稿上下文
- **WHEN** 快取未命中，且 transcript-indexer 未找到相關句子
- **THEN** 僅將「查詢詞」傳給 Gemini API（無上下文），取得解釋後存入快取並回傳，回覆末尾附註「（未在逐字稿中找到此詞）」

### Requirement: Gemini API 呼叫
Query Engine SHALL 使用固定 System Prompt 呼叫 Gemini 2.0 Flash，確保回覆格式一致且精簡。

#### Scenario: 成功呼叫 Gemini API
- **WHEN** 向 Gemini 2.0 Flash 傳送查詢
- **THEN** 回傳格式嚴格符合：「中文意思：...\n在此情境的用法：...（2-3 句）」

#### Scenario: Gemini API 速率限制（429）
- **WHEN** API 回傳 429 Too Many Requests
- **THEN** 等待 5 秒後重試一次；若再次失敗，向用戶回傳錯誤訊息

### Requirement: 快取資料表結構
系統 SHALL 使用以下結構建立 `cache` 資料表：

```sql
CREATE TABLE cache (
    query_key TEXT PRIMARY KEY,   -- lower(strip(input))
    original_query TEXT NOT NULL,
    explanation TEXT NOT NULL,
    context_sentence TEXT,        -- 使用的逐字稿句子（可為 NULL）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Scenario: 快取寫入
- **WHEN** Gemini API 成功回傳解釋
- **THEN** 以 `query_key = lower(strip(input))` 為主鍵寫入 `cache` 資料表

### Requirement: System Prompt 格式控制
Query Engine SHALL 使用固定 System Prompt 確保 Gemini 回覆格式一致。

#### Scenario: System Prompt 套用
- **WHEN** 每次呼叫 Gemini API
- **THEN** System Prompt 內容包含格式要求（中文意思一行、情境說明 2-3 句、不得超出此格式）
