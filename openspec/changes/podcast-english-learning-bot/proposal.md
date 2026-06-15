## Why

用 Podcast 學英文時，遇到不懂的單字或句型，需要立即、精準的解釋，現有工具（如直接對話 Gemini）回覆過於冗長且缺乏 Podcast 情境。這個工具提供一個 Telegram Bot，結合 Podcast 逐字稿索引，讓用戶輸入單字或片語即可取得精簡且情境準確的中文解釋，並能儲存單字供日後複習。

## What Changes

- 建立 Telegram Bot，接受用戶輸入的英文單字或片語，回傳翻譯 + 使用情境說明（控制在 3-4 行內）
- 實作逐字稿解析器：將 .txt 格式的 Podcast 逐字稿切成句子，存入 SQLite FTS（Full Text Search）索引
- 實作查詢快取：查過的單字/片語結果存入 SQLite，下次查詢直接回傳，不再呼叫 AI API
- 實作單字本：儲存用戶查過的單字，支援 `/list` 指令查看歷史
- 支援透過 Telegram 傳送 .txt 逐字稿檔案，Bot 自動解析並建立索引
- 使用 Gemini 2.0 Flash API（Google AI Studio 免費 tier）作為 AI 後端
- 部署為 systemd service，在 GCP Compute Engine VM 上長駐執行（long polling 模式）

## Capabilities

### New Capabilities

- `telegram-bot`: Telegram Bot 核心，處理用戶訊息、指令路由、檔案接收
- `transcript-indexer`: 解析 .txt 逐字稿，切句，存入 SQLite FTS 索引
- `query-engine`: 查詢流程，FTS 取得句子上下文 → 快取命中檢查 → Gemini API 呼叫 → 存快取
- `vocabulary-store`: 單字本 CRUD，支援 `/list`、`/export` 指令

### Modified Capabilities

（無，全新專案）

## Impact

- **新依賴**：`python-telegram-bot`、`google-generativeai`（Gemini SDK）、SQLite（Python 內建）
- **基礎設施**：GCP Compute Engine VM，需要 Telegram Bot Token 與 Google AI Studio API Key
- **部署**：systemd service 設定檔
- **儲存**：單一 SQLite 檔案（逐字稿索引 + 快取 + 單字本）
