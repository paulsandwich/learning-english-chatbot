## Requirements

### Requirement: 解析 .txt 逐字稿並建立 FTS 索引
Indexer SHALL 讀取 .txt 純文字檔案，依句號/問號/驚嘆號分句，並將每句存入 SQLite FTS5 資料表。

#### Scenario: 成功解析並索引
- **WHEN** 收到一個有效的 .txt 檔案路徑
- **THEN** 將檔案內容分割成句子，每句以 (episode_name, sentence_index, sentence_text) 存入 `sentences` FTS5 資料表，回傳已索引的句子數量

#### Scenario: 空白檔案
- **WHEN** 收到的 .txt 檔案內容為空
- **THEN** 回傳錯誤：「檔案內容為空，無法建立索引」

#### Scenario: 重複上傳同一集
- **WHEN** 上傳的檔案名稱與已索引的 episode 相同
- **THEN** 刪除舊索引，重新建立新索引，回傳「已更新 N 句」

### Requirement: FTS 搜尋句子上下文
Indexer SHALL 根據查詢詞，從 FTS 索引中找到最相關的句子及其前後各一句（上下文視窗）。

#### Scenario: 搜尋到包含查詢詞的句子
- **WHEN** 查詢詞在逐字稿中存在
- **THEN** 回傳最多 3 個匹配結果，每個結果包含：前一句 + 匹配句 + 後一句（合併為一段文字）

#### Scenario: 搜尋不到查詢詞
- **WHEN** 查詢詞在所有已索引逐字稿中均不存在
- **THEN** 回傳空結果（None），query-engine 降級為無情境模式呼叫 AI

### Requirement: SQLite FTS5 資料表結構
系統 SHALL 使用以下結構建立 `sentences` 資料表：

```sql
CREATE VIRTUAL TABLE sentences USING fts5(
    episode_name,
    sentence_index UNINDEXED,
    sentence_text,
    tokenize = 'unicode61'
);
```

#### Scenario: 資料表初始化
- **WHEN** 資料庫首次初始化
- **THEN** `sentences` FTS5 資料表成功建立，unicode61 tokenizer 啟用
