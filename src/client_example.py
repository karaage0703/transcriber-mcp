#!/usr/bin/env python
"""
Transcriber MCPサーバーの動作確認用クライアント例
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path


def send_request(request_data):
    """
    MCPサーバーにリクエストを送信する

    Args:
        request_data: リクエストデータ（辞書）

    Returns:
        レスポンスデータ（辞書）
    """
    # JSON形式に変換
    request_json = json.dumps(request_data)

    # サーバープロセスにリクエストを送信
    print(f"送信リクエスト: {request_json}")

    # サブプロセスとしてサーバーを起動し、標準入力からリクエストを送信
    process = subprocess.Popen(
        ["python", "-m", "src.main"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # リクエストを送信
    stdout, stderr = process.communicate(input=request_json + "\n")

    if stderr:
        print(f"エラー: {stderr}")

    # レスポンスを解析
    for line in stdout.splitlines():
        try:
            response = json.loads(line)
            if "result" in response and response.get("id") is not None:
                return response
        except json.JSONDecodeError:
            print(f"JSONではない出力: {line}")

    return {"error": "レスポンスが受信できませんでした"}


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Transcriber MCPサーバーのテストクライアント")
    parser.add_argument("file_path", help="文字起こし対象の音声・動画ファイルパス")
    args = parser.parse_args()

    # ファイルの存在確認
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"エラー: ファイル '{file_path}' が存在しません")
        sys.exit(1)

    # リクエストの作成
    request = {"jsonrpc": "2.0", "id": 1, "method": "transcribe", "params": {"file_path": str(file_path.absolute())}}

    print(f"ファイル '{file_path}' の文字起こしを開始します...")

    # リクエストの送信
    response = send_request(request)

    # レスポンスの表示
    print("\n結果:")
    print(json.dumps(response, indent=2, ensure_ascii=False))

    # 成功した場合、結果ファイルの内容を表示
    if "result" in response and "result" in response["result"]:
        result_path = response["result"]["result"]
        try:
            with open(result_path, "r", encoding="utf-8") as f:
                print("\n文字起こし結果:")
                print("-" * 40)
                print(f.read())
                print("-" * 40)
        except Exception as e:
            print(f"結果ファイルの読み込みに失敗しました: {e}")


if __name__ == "__main__":
    main()
