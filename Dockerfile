FROM python:3.11-slim

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ruffのインストール（コード品質チェック用）
RUN pip install --no-cache-dir ruff==0.9.1

# アプリケーションのコピー
COPY . .

# 実行コマンド
CMD ["python", "-m", "src.main"]