#!/usr/bin/env python
"""
Transcriber MCP

音声・動画ファイルをテキストに変換するMCP（Model Context Protocol）準拠のサーバー
"""

import os
import sys
import argparse
import logging
from pathlib import Path

from src.mcp_server import MCPServer


def setup_logging():
    """ロギングの設定"""
    # ロガーの設定
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # コンソールハンドラの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # フォーマッタの設定
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    # ハンドラの追加
    logger.addHandler(console_handler)

    # ファイルハンドラの設定
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "transcriber_mcp.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # ハンドラの追加
    logger.addHandler(file_handler)

    return logger


def main():
    """
    メイン関数

    コマンドライン引数を解析し、MCPサーバーを起動します。
    """
    # ロギングの設定
    logger = setup_logging()

    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="Transcriber MCP - 音声・動画ファイルをテキストに変換するMCPサーバー")
    parser.add_argument(
        "--model-size",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="使用するモデルサイズ (デフォルト: base)",
    )
    parser.add_argument("--output-dir", help="文字起こし結果の出力ディレクトリ（指定されない場合は一時ディレクトリを使用）")
    args = parser.parse_args()

    try:
        # MCPサーバーの起動
        logger.info("Transcriber MCPサーバーを起動します...")
        server = MCPServer()
        server.start()

    except KeyboardInterrupt:
        logger.info("サーバーを終了します。")
        sys.exit(0)

    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
