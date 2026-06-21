## Requirements

### Requirement: 接受文字查詢
Bot SHALL 接受任意英文文字輸入（非指令），將其視為查詢詞，並透過 query-engine 取得解釋後回傳給用戶。

#### Scenario: 用戶輸入單字
- **WHEN** 用戶傳送純文字訊息（如 "turn the tables"）
- **THEN** Bot 回傳翻譯 + 使用情境說明，格式為：「中文意思：...\n在此情境的用法：...」

#### Scenario: 用戶輸入空白訊息
- **WHEN** 用戶傳送空白或只有空格的訊息
- **THEN** Bot 回傳提示：「請輸入一個英文單字或片語」

### Requirement: 接收逐字稿檔案
Bot SHALL 接受用戶上傳的 .txt 檔案，並觸發 transcript-indexer 進行解析與索引。

#### Scenario: 用戶上傳 .txt 檔案
- **WHEN** 用戶傳送一個 .txt 格式的文件檔案
- **THEN** Bot 回覆「處理中...」，完成後回傳「✅ 已完成索引，共 N 句」

#### Scenario: 用戶上傳非 .txt 檔案
- **WHEN** 用戶傳送非 .txt 格式的檔案（如 .pdf、.docx）
- **THEN** Bot 回傳：「目前只支援 .txt 格式的逐字稿」

### Requirement: /list 指令
Bot SHALL 支援 `/list` 指令，顯示用戶最近查詢過的單字/片語。

#### Scenario: 有查詢紀錄
- **WHEN** 用戶傳送 `/list`
- **THEN** Bot 回傳最近 50 筆查詢紀錄，每筆格式為「單字 — 中文意思」

#### Scenario: 無查詢紀錄
- **WHEN** 用戶傳送 `/list` 且單字本為空
- **THEN** Bot 回傳：「單字本是空的，開始查詢後會記錄在這裡」

### Requirement: /export 指令
Bot SHALL 支援 `/export` 指令，以純文字格式匯出所有單字本內容。

#### Scenario: 匯出單字本
- **WHEN** 用戶傳送 `/export`
- **THEN** Bot 回傳一份文字訊息，包含所有查詢紀錄（單字、中文意思、查詢時間）

### Requirement: /start 指令
Bot SHALL 支援 `/start` 指令，顯示使用說明。

#### Scenario: 用戶首次啟動
- **WHEN** 用戶傳送 `/start`
- **THEN** Bot 回傳使用說明，說明如何查詢單字、上傳逐字稿、查看單字本

### Requirement: 錯誤處理
Bot SHALL 在發生錯誤時回傳友善的錯誤訊息，不暴露技術細節。

#### Scenario: AI API 呼叫失敗
- **WHEN** Gemini API 呼叫失敗（網路錯誤、速率限制等）
- **THEN** Bot 回傳：「查詢暫時失敗，請稍後再試」
