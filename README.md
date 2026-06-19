# Podcast English Learning Bot

Telegram Bot，用於 Podcast 英文學習。輸入單字或片語，取得精簡的中文翻譯與情境說明。支援上傳 Podcast 逐字稿建立索引，讓 AI 回覆更貼近原始對話情境。

## 需求

- Python 3.11+
- GCP Compute Engine VM（或任何可執行 Python 的 Linux 環境）
- Telegram Bot Token（從 [@BotFather](https://t.me/BotFather) 取得）
- Gemini API Key（從 [Google AI Studio](https://aistudio.google.com) 免費取得）

## 部署步驟

### 1. Clone 專案

```bash
git clone <your-repo-url>
cd learning-english-chatbot
```

### 2. 設定環境變數

```bash
cp .env.example .env
nano .env  # 填入 TELEGRAM_BOT_TOKEN 和 GEMINI_API_KEY
```

### 3. 安裝依賴並初始化資料庫

```bash
bash install.sh
```

### 4. 設定 systemd service

```bash
sudo cp podcast-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable podcast-bot
sudo systemctl start podcast-bot
```

### 5. 確認運行狀態

```bash
sudo systemctl status podcast-bot
```

## 使用方式

- **查詢單字/片語**：直接在 Telegram 輸入文字
- **上傳逐字稿**：傳送 `.txt` 檔案給 Bot，自動建立索引
- `/list` — 查看最近查過的 50 個單字
- `/export` — 匯出完整單字本
- `/start` — 顯示使用說明

## 逐字稿處理流程

### 1. 接收檔案

把 `.txt` 逐字稿傳給 Bot，程式會驗證副檔名、下載到 `transcripts/` 目錄，並用檔名（去掉 `.txt`）作為這集的識別名稱。例如 `ep123.txt` → episode 名稱 `ep123`。

### 2. 分句與建立索引

程式將逐字稿依 `.`、`?`、`!` 切成一句一句，存入 SQLite FTS5（全文搜尋）索引：

```
逐字稿原文：
"I wanted to turn the tables. He was surprised. It worked out well."

切句後存入 SQLite：
episode | index | sentence
ep123   | 0     | I wanted to turn the tables.
ep123   | 1     | He was surprised.
ep123   | 2     | It worked out well.
```

重複上傳同一集時，舊索引會先刪除再重建。

### 3. 查詢時自動帶入情境

輸入 `turn the tables` 後，Bot 會先用 FTS5 搜尋找出包含這個詞的句子，再取前後各一句組成上下文視窗，一起傳給 Gemini：

```
傳給 Gemini 的內容：
  單字/片語："turn the tables"
  Podcast 原句上下文：I wanted to turn the tables. He was surprised.
```

Gemini 看到的是這個詞在 Podcast 裡的真實用法，因此解釋比單純查字典更精準，會說明在這段對話的語氣與含義。

### 4. 快取

查詢結果會存入 SQLite `cache` 資料表。同一個詞再次查詢時直接回傳快取，不再呼叫 Gemini API。

## 專案結構

```
bot/
  __init__.py
  db.py          # SQLite 連線與初始化
  indexer.py     # 逐字稿解析與 FTS 索引
  query.py       # 查詢引擎（快取 + Gemini API）
  vocab.py       # 單字本 CRUD
  main.py        # Telegram Bot 主程式
data/            # SQLite 資料庫（自動建立）
transcripts/     # 上傳逐字稿暫存（自動建立）
```
