## Context

使用者透過 Podcast 學英文，需要在聆聽過程中快速查詢陌生單字或片語的意思與用法。工具以 Telegram Bot 為介面，運行於 GCP Compute Engine VM 上，使用 Gemini 2.0 Flash API（Google AI Studio 免費 tier）提供 AI 解釋，SQLite 作為單一儲存層（逐字稿索引、查詢快取、單字本）。

## Goals / Non-Goals

**Goals:**
- 輸入單字/片語後，在 3 秒內回傳翻譯 + 使用情境說明（控制在 3-4 行）
- 回覆精準且有 Podcast 原始情境（來自 FTS 搜尋出的逐字稿句子）
- 重複查詢同一詞不再呼叫 AI（快取命中）
- 透過 Telegram 傳送 .txt 逐字稿檔案，Bot 自動建立索引
- 儲存查詢紀錄，支援 `/list` 和 `/export` 指令

**Non-Goals:**
- 多用戶支援（個人工具，單一 Telegram 用戶）
- 語音輸入或音頻處理
- 自動從 Podcast 平台抓取逐字稿
- Web 介面或其他 Bot 平台（LINE、Discord 等）
- SRT/時間戳記格式支援（僅純文字 .txt）

## Decisions

### Long Polling vs Webhook
選擇 **Long Polling**。
Webhook 需要公開 HTTPS endpoint（domain + SSL），增加部署複雜度。Long polling 透過 `python-telegram-bot` 的 `Application.run_polling()` 實作，Telegram 連線維持最長 30 秒等待，訊息到達時立即回應，延遲感知上與 webhook 相同。個人工具不需要 webhook 的擴展性優勢。

### SQLite vs 外部資料庫
選擇 **SQLite**。
單一用戶、低並發、無需跨機器共享資料。SQLite FTS5 原生支援全文搜尋，滿足逐字稿查詢需求。整個儲存層只有一個 `.db` 檔案，備份和部署極為簡單。

### AI 模型選擇
選擇 **Gemini 2.0 Flash（Google AI Studio 免費 tier）**。
使用者已有 Google 帳號，可直接取得免費 API key（每日 1,500 次請求）。Flash 系列速度快（< 1 秒），中英文解釋品質足夠。透過 System Prompt 精確控制回覆格式，解決之前 Gemini 回覆過長的問題。

### System Prompt 設計
使用固定 System Prompt 約束回覆格式：
```
你是英文學習助手。用戶輸入一個英文單字或片語，以及它在 Podcast 中出現的句子（上下文）。
回覆格式（嚴格遵守）：
1. 中文意思：（一行，精簡）
2. 在此情境的用法：（2-3句，說明在這個對話中的含義和語氣）
不可超出以上格式。不加其他說明或補充。
```

### 逐字稿分句策略
以句號、問號、驚嘆號作為分隔符，每句保留前後一句作為上下文視窗（context window），FTS 搜尋時一併回傳，讓 Gemini 看到更完整的對話情境。

### 快取鍵設計
以 `lower(strip(input))` 作為快取鍵。同一個詞的不同大小寫或前後空格視為同一查詢。

## Risks / Trade-offs

- **FTS 搜尋無法找到詞的變形**（run/running/ran 視為不同詞）→ 使用者需輸入原形，或未來可加入詞形還原（lemmatization）作為改進
- **Gemini 免費 API 有速率限制**（15 RPM）→ 快取機制可大幅降低 API 呼叫次數；極端情況下加入重試退避邏輯
- **逐字稿品質影響搜尋結果**→ 如果 Podcast 逐字稿有錯字，FTS 會找不到句子，此時 Bot 仍會呼叫 Gemini，只是沒有情境句（降級處理）
- **Long polling 需要 VM 持續運行** → systemd service 設定自動重啟，VM 重開後自動恢復

## Migration Plan

1. 在 GCP VM 上安裝 Python 3.11+、pip 依賴
2. 建立 `.env` 檔案存放 `TELEGRAM_BOT_TOKEN` 和 `GEMINI_API_KEY`
3. 初始化 SQLite DB（執行 `python -m bot.db init`）
4. 設定 systemd service 檔案，enable 並 start
5. 透過 Telegram 傳送第一份逐字稿 .txt 進行測試

Rollback：停止 systemd service 即可，無外部資料庫需要回滾。

## Open Questions

- 單字本的 `/list` 是否需要分頁（若單字數量超過 Telegram 訊息長度限制）？ → 初版先截斷至最近 50 筆，未來再擴充
- 是否需要刪除單字功能（`/delete <word>`）？ → 初版不實作，保持簡單
