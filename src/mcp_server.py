"""
MCPサーバーモジュール

Model Context Protocol (MCP)に準拠したサーバーを提供します。
JSON-RPC over stdioを使用してクライアントからのリクエストを処理します。
"""

import sys
import json
import logging
from typing import Dict, Any, List
from pathlib import Path

from src.transcriber import Transcriber


class MCPServer:
    """
    Model Context Protocol (MCP)に準拠したサーバークラス

    JSON-RPC over stdioを使用してクライアントからのリクエストを処理します。

    Attributes:
        transcriber: Transcriberのインスタンス
        logger: ロガー
    """

    def __init__(self, model_size="base", output_dir=None):
        """
        MCPServerのコンストラクタ

        Args:
            model_size: 使用するモデルサイズ ("tiny", "base", "small", "medium", "large")
            output_dir: 文字起こし結果の出力ディレクトリ（指定がない場合は一時ディレクトリを使用）
        """
        self.transcriber = Transcriber(model_size=model_size, output_dir=output_dir)

        # ロガーの設定
        self.logger = logging.getLogger("mcp_server")
        self.logger.setLevel(logging.INFO)

        # ファイルハンドラの設定
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "mcp_server.log")
        file_handler.setLevel(logging.INFO)

        # フォーマッタの設定
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # ハンドラの追加
        self.logger.addHandler(file_handler)

    def start(self):
        """
        サーバーを起動し、stdioからのリクエストをリッスンします。
        """
        self.logger.info("MCPサーバーを起動しました")

        # サーバー情報を出力
        self._send_response(
            {
                "jsonrpc": "2.0",
                "method": "server/info",
                "params": {
                    "name": "transcribe",
                    "version": "0.1.0",
                    "description": "音声・動画ファイルをテキストに変換するMCPサーバー",
                    "tools": self._get_tools(),
                    "resources": self._get_resources(),
                },
            }
        )

        # ツール情報を出力
        self._send_response(
            {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {
                    "tools": self._get_tools(),
                },
            }
        )

        # リクエストをリッスン
        while True:
            try:
                # 標準入力からリクエストを読み込む
                request_line = sys.stdin.readline()
                if not request_line:
                    break

                # リクエストをパース
                request = json.loads(request_line)
                self.logger.info(f"リクエストを受信しました: {request}")

                # リクエストを処理
                self._handle_request(request)

            except json.JSONDecodeError:
                self.logger.error("JSONのパースに失敗しました")
                self._send_error(-32700, "Parse error", None)

            except Exception as e:
                self.logger.error(f"エラーが発生しました: {str(e)}")
                self._send_error(-32603, f"Internal error: {str(e)}", None)

    def _handle_request(self, request: Dict[str, Any]):
        """
        リクエストを処理します。

        Args:
            request: JSONリクエスト
        """
        # リクエストのバリデーション
        if "jsonrpc" not in request or request["jsonrpc"] != "2.0":
            self._send_error(-32600, "Invalid Request", request.get("id"))
            return

        if "method" not in request:
            self._send_error(-32600, "Method not specified", request.get("id"))
            return

        # メソッドの取得
        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id")

        # メソッドの処理
        if method == "initialize":
            self._handle_initialize(params, request_id)
        elif method == "tools/list":
            self._handle_tools_list(request_id)
        elif method == "tools/call":
            self._handle_tools_call(params, request_id)
        elif method == "transcribe":
            self._handle_transcribe(params, request_id)
        else:
            self._send_error(-32601, f"Method not found: {method}", request_id)

    def _handle_initialize(self, params: Dict[str, Any], request_id: Any):
        """
        initializeメソッドを処理します。

        Args:
            params: リクエストパラメータ
            request_id: リクエストID
        """
        # クライアント情報を取得（オプション）
        client_name = params.get("client_name", "unknown")
        client_version = params.get("client_version", "unknown")

        self.logger.info(f"クライアント '{client_name} {client_version}' が接続しました")

        # サーバーの機能を返す
        response = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "transcribe",
                "version": "0.1.0",
                "description": "音声・動画ファイルをテキストに変換するMCPサーバー。",
            },
            "capabilities": {"tools": {"listChanged": False}, "resources": {"listChanged": False, "subscribe": False}},
            "instructions": "transcribeを使用する際の注意点:\n1. file_pathパラメータには絶対パスを使用してください。相対パスを使用すると正しく処理できない場合があります。",
        }

        self._send_result(response, request_id)

        # ツール情報を送信
        self._send_response(
            {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {
                    "tools": self._get_tools(),
                },
            }
        )

    def _handle_transcribe(self, params: Dict[str, Any], request_id: Any):
        """
        transcribeメソッドを処理します。

        Args:
            params: リクエストパラメータ
            request_id: リクエストID
        """
        # パラメータのバリデーション
        if "file_path" not in params:
            self._send_error(-32602, "Invalid params: file_path is required", request_id)
            return

        file_path = params["file_path"]
        output_path = params.get("output_path")

        try:
            # 文字起こしを実行
            result_path = self.transcriber.transcribe(file_path, output_path)

            # レスポンスを送信
            self._send_result({"result": result_path}, request_id)

        except FileNotFoundError:
            self._send_error(-32602, f"File not found: {file_path}", request_id)

        except Exception as e:
            self._send_error(-32603, f"Failed to transcribe: {str(e)}", request_id)

    def _send_result(self, result: Any, request_id: Any):
        """
        成功レスポンスを送信します。

        Args:
            result: レスポンス結果
            request_id: リクエストID
        """
        response = {"jsonrpc": "2.0", "result": result, "id": request_id}

        self._send_response(response)

    def _send_error(self, code: int, message: str, request_id: Any):
        """
        エラーレスポンスを送信します。

        Args:
            code: エラーコード
            message: エラーメッセージ
            request_id: リクエストID
        """
        response = {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": request_id}

        self._send_response(response)

    def _send_response(self, response: Dict[str, Any]):
        """
        レスポンスを標準出力に送信します。

        Args:
            response: レスポンス
        """
        response_json = json.dumps(response)
        print(response_json, flush=True)
        self.logger.info(f"レスポンスを送信しました: {response_json}")

    def _get_tools(self) -> List[Dict[str, Any]]:
        """
        サーバーが提供するツールの一覧を取得します。

        Returns:
            ツールの一覧
        """
        return [
            {
                "name": "transcribe",
                "description": "音声・動画ファイル（mp3, mp4, wav, mov, avi）をテキストに変換します。文字起こし、音声認識、テキスト化などの機能を提供します。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "文字起こし対象の音声・動画ファイルパス。絶対パスを使用してください。",
                        },
                        "output_path": {
                            "type": "string",
                            "description": "文字起こし結果の出力先ファイルパス。絶対ファイルで指定してください。",
                        },
                    },
                    "required": ["file_path"],
                },
            },
        ]

    def _handle_tools_call(self, params: Dict[str, Any], request_id: Any):
        """
        tools/callメソッドを処理します。

        Args:
            params: リクエストパラメータ
            request_id: リクエストID
        """
        # パラメータのバリデーション
        if "name" not in params:
            self._send_error(-32602, "Invalid params: name is required", request_id)
            return

        if "arguments" not in params:
            self._send_error(-32602, "Invalid params: arguments is required", request_id)
            return

        tool_name = params["name"]
        arguments = params["arguments"]

        # ツールの処理
        if tool_name == "transcribe":
            try:
                output_path = self.transcriber.transcribe(arguments["file_path"], arguments.get("output_path"))
                self._send_result(
                    {
                        "content": [
                            {"type": "text", "text": f"音声・動画ファイルの文字起こしが完了しました。出力先: {output_path}"}
                        ]
                    },
                    request_id,
                )
            except FileNotFoundError:
                self._send_result(
                    {
                        "content": [{"type": "text", "text": f"ファイルが見つかりません: {arguments.get('file_path')}"}],
                        "isError": True,
                    },
                    request_id,
                )
            except Exception as e:
                self._send_result(
                    {
                        "content": [{"type": "text", "text": f"文字起こしに失敗しました: {str(e)}"}],
                        "isError": True,
                    },
                    request_id,
                )
        else:
            self._send_result(
                {"content": [{"type": "text", "text": f"ツールが見つかりません: {tool_name}"}], "isError": True}, request_id
            )

    def _handle_tools_list(self, request_id: Any):
        """
        tools/listメソッドを処理します。

        Args:
            request_id: リクエストID
        """
        tools = self._get_tools()
        self._send_result({"tools": tools}, request_id)

    def _get_resources(self) -> List[Dict[str, Any]]:
        """
        サーバーが提供するリソースの一覧を取得します。

        Returns:
            リソースの一覧
        """
        return []
