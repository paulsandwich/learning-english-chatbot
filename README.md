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
