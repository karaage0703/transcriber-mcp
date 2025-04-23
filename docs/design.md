
# 要件・設計書

## 1. 要件定義

### 1.1 基本情報

- **ソフトウェア名称**: Transcriber MCP
- **リポジトリ名**: transcriber-mcp

### 1.2 プロジェクト概要

本プロジェクトは、音声・動画ファイルをテキストに変換する機能を提供する「MCP（Model Context Protocol）」準拠のサーバ「Transcriber MCP」を開発することを目的としています。fastwhisperを利用し、CPU環境で動作する軽量かつ実用的な文字起こしサーバを構築します。

### 1.3 機能要件

#### 1.3.1 基本機能

- MCPプロトコルに準拠したサーバの実装
- 音声・動画ファイル（mp3, mp4, wav, mov, avi）を受け取り、文字起こしを実施
- 結果をテキストファイル形式で出力
- MCPクライアントとの通信インターフェースを提供

#### 1.3.2 拡張機能（将来的な対応予定）

- タイムスタンプ付き文字起こし
- 多言語対応
- モデル切り替え機能

### 1.4 非機能要件

- CPU上でリアルタイム処理が可能な軽量設計
- 同時に複数リクエストを処理できる構成
- 入力ファイルの安全性検証
- MCP仕様に則ったインターフェース

### 1.5 制約条件

- Python 3.8以上を使用
- 音声認識エンジンはfastwhisper
- MCPプロトコルに完全準拠
- パッケージ管理は`uv`を使用

### 1.6 開発環境

- 言語: Python
- 音声認識: fastwhisper
- パッケージ管理: uv
- 開発ツール: VSCode
- 仕様ライブラリ: python-sdk (Model Context Protocol)
- MCP仕様: [Model Context Protocol](https://modelcontextprotocol.io/llms-full.txt)

### 1.7 成果物

- ソースコード
- 設計書
- ユニットテストコード
- README
- 要件定義書

## 2. システム設計

### 2.1 システム概要設計

#### 2.1.1 アーキテクチャ構成

```
[MCPクライアント] <-> [Transcriber MCP サーバ] <-> [fastwhisper]
```

#### 2.1.2 コンポーネント

1. Transcriber MCP サーバ
   - MCPリクエスト受付
   - メディアファイルの検証・保存・処理
2. fastwhisper モジュール
   - CPU上での文字起こし処理

### 2.2 詳細設計

#### 2.2.1 クラス設計

```python
class TranscriberMCPServer:
    def __init__(self):
        self.transcriber = FastWhisperTranscriber()

    def handle_request(self, request):
        # ファイル受け取り、形式検証
        # 文字起こし処理実行
        # テキストファイル出力
        # 結果のパス返却
```

```python
class FastWhisperTranscriber:
    def __init__(self):
        # fastwhisper初期化
        pass

    def transcribe(self, file_path):
        # fastwhisperを用いて文字起こしを行う
        return transcript_text
```

#### 2.2.2 データフロー

1. クライアントがメディアファイル付きで`transcribe`リクエストを送信
2. サーバが受信し、検証後fastwhisperにて文字起こし
3. 結果をテキストファイルとして保存
4. 出力パスをレスポンスとして返却

### 2.3 インターフェース設計

- プロトコル: MCP（JSON-RPC 2.0）
- エンドポイント: `/transcribe`
- リクエスト: `{ "method": "transcribe", "params": { "file_path": "xxx.mp4" } }`
- レスポンス: `{ "result": "transcribed.txt" }`

### 2.4 セキュリティ設計

- 対応形式外ファイルの拒否
- パスの無害化（パストラバーサル防止）
- ログ監視

### 2.5 テスト設計

- ユニットテスト
  - ファイル読み込み、形式検証、fastwhisperの出力確認
- 統合テスト
  - MCP経由のエンドツーエンドのテスト
- エラーテスト
  - 無効ファイル、処理失敗などのケース
