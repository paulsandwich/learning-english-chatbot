## 1. 專案初始化與環境設定

- [x] 1.1 建立專案目錄結構：`bot/`（主程式）、`data/`（SQLite 存放）、`transcripts/`（暫存上傳檔案）
- [x] 1.2 建立 `requirements.txt`，列出依賴：`python-telegram-bot>=20.0`、`google-generativeai`、`python-dotenv`
- [x] 1.3 建立 `.env.example`，列出必要環境變數：`TELEGRAM_BOT_TOKEN`、`GEMINI_API_KEY`
- [x] 1.4 建立 `.gitignore`，排除 `.env`、`data/`、`transcripts/`

## 2. 資料庫初始化（SQLite）

- [x] 2.1 實作 `bot/db.py`：建立資料庫連線，初始化 `sentences`（FTS5）、`cache`、`vocabulary` 三張資料表
- [x] 2.2 實作 `sentences` FTS5 資料表（`episode_name`、`sentence_index`、`sentence_text`，tokenize=unicode61）
- [x] 2.3 實作 `cache` 資料表（`query_key` PRIMARY KEY、`original_query`、`explanation`、`context_sentence`、`created_at`）
- [x] 2.4 實作 `vocabulary` 資料表（`id`、`word`、`query_key` UNIQUE、`explanation`、`queried_at`）
- [x] 2.5 提供 `init_db()` 函式，`if not exists` 建立全部資料表

## 3. 逐字稿索引器（transcript-indexer）

- [x] 3.1 實作 `bot/indexer.py`：讀取 .txt 檔案，以句號/問號/驚嘆號分句，過濾空句
- [x] 3.2 實作重複上傳處理：先刪除同 `episode_name` 的舊索引，再寫入新句子
- [x] 3.3 實作 `search_context(query: str) -> str | None`：FTS5 MATCH 搜尋，回傳前句+匹配句+後句合併字串（最多取第一個匹配結果）

## 4. 查詢引擎（query-engine）

- [x] 4.1 實作 `bot/query.py`：定義 `explain(word: str) -> str` 函式，實作快取優先查詢流程
- [x] 4.2 實作快取命中：`SELECT explanation FROM cache WHERE query_key = ?`，命中直接回傳
- [x] 4.3 實作 Gemini API 呼叫：使用 `google-generativeai` SDK，載入固定 System Prompt，支援有/無逐字稿上下文兩種 prompt
- [x] 4.4 實作 System Prompt：要求中文意思一行 + 情境說明 2-3 句，嚴格格式限制
- [x] 4.5 實作 Gemini API 429 重試邏輯：等待 5 秒後重試一次
- [x] 4.6 成功取得解釋後，寫入 `cache` 資料表

## 5. 單字本（vocabulary-store）

- [x] 5.1 實作 `bot/vocab.py`：`save_word(word, explanation)` — INSERT OR REPLACE 寫入 `vocabulary`
- [x] 5.2 實作 `list_words(limit=50) -> list` — 依 `queried_at` 降冪取最近 50 筆
- [x] 5.3 實作 `export_all() -> str` — 取全部紀錄，格式化為純文字字串

## 6. Telegram Bot 主程式（telegram-bot）

- [x] 6.1 實作 `bot/main.py`：初始化 `python-telegram-bot` Application，註冊 handlers
- [x] 6.2 實作 `/start` handler：回傳使用說明文字
- [x] 6.3 實作 `/list` handler：呼叫 `vocab.list_words()`，格式化回傳
- [x] 6.4 實作 `/export` handler：呼叫 `vocab.export_all()`，回傳完整單字本
- [x] 6.5 實作文字訊息 handler：呼叫 `query.explain()`，成功後呼叫 `vocab.save_word()`，回傳結果
- [x] 6.6 實作文件接收 handler：驗證副檔名為 .txt，下載至 `transcripts/`，呼叫 `indexer`，回傳索引結果
- [x] 6.7 實作全域錯誤 handler：捕捉未預期錯誤，回傳「查詢暫時失敗，請稍後再試」

## 7. 部署設定

- [x] 7.1 建立 `install.sh`：安裝 Python 依賴、建立 `data/` 目錄、初始化 SQLite DB
- [x] 7.2 建立 `podcast-bot.service`（systemd unit 檔）：設定 WorkingDirectory、ExecStart、Restart=always、EnvironmentFile
- [x] 7.3 撰寫 `README.md` 部署步驟：clone repo → 設定 .env → 執行 install.sh → 啟用 systemd service
