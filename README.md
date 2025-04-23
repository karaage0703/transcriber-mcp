# Transcriber MCP

音声・動画ファイルをテキストに変換するMCP（Model Context Protocol）準拠のサーバー「Transcriber MCP」です。faster-whisperを利用し、CPU環境で動作する軽量かつ実用的な文字起こしサーバーを提供します。

## 機能

- MCPプロトコルに準拠したサーバーの実装
- 音声・動画ファイル（mp3, mp4, wav, mov, avi）を受け取り、文字起こしを実施
- 結果をテキストファイル形式で出力
- MCPクライアントとの通信インターフェースを提供

## インストール方法

### 必要条件

- Python 3.8以上
- faster-whisper
- ffmpeg（音声・動画ファイル処理用）

### インストール手順

1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/transcriber-mcp.git
cd transcriber-mcp
```

2. 仮想環境の作成と依存パッケージのインストール

```bash
# uvを使用して仮想環境を作成
uv venv

# 依存パッケージをインストール
uv pip install -r requirements.txt
```

## 使用方法

### サーバーの起動

```bash
# uvを使用してサーバーを起動
uv run -m src.main
```

### クライアント例を使用した動作確認

```bash
# テスト用の音声ファイルを作成
uv pip install gtts
uv run -c "from gtts import gTTS; tts = gTTS('これはテスト用の音声ファイルです。文字起こしが正しく機能するかを確認します。', lang='ja'); tts.save('test_audio.mp3')"

# 文字起こしを実行
uv run -m src.client_example test_audio.mp3
```

### MCPクライアントからの利用

MCPプロトコルに準拠したクライアントから以下のようにリクエストを送信します：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "transcribe",
  "params": {
    "file_path": "/path/to/your/audio_or_video_file.mp3"
  }
}
```

### レスポンス例

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "result": "/path/to/output/audio_or_video_file_transcribed.txt"
  }
}
```

## Clineでの設定方法

Clineと連携して使用することで、LLMとの対話を通じて文字起こしを実行できます。

### Clineの設定

Clineの設定ファイル（通常は`~/.config/cline/settings/mcp_settings.json`）に以下の設定を追加します：

```json
{
  "transcribe": {
    "command": "uv",
    "args": [
      "run",
      "--directory",
      "/path/to/transcriber-mcp",
      "python",
      "-m",
      "src.main"
    ]
  }
}
```

※ `--directory`のパスは実際の環境に合わせて変更してください。

## サポートするファイル形式

- 音声ファイル: mp3, wav
- 動画ファイル: mp4, mov, avi


## モデルサイズの変更

文字起こしの精度を向上させるために、モデルサイズを変更することができます。

```python
# src/transcriber.py を編集
self.model_size = "medium"  # tiny, base, small, medium, large から選択
```

より大きなモデルを使用すると精度が向上しますが、メモリ使用量とロード時間が増加します。

## 将来的な拡張予定

- タイムスタンプ付き文字起こし
- 多言語対応
- モデル切り替え機能

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。
