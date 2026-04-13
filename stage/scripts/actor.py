#!/usr/bin/env python3
"""
Stage System — Actor Script
LM Studio OpenAI互換API経由でローカルLLMに演技させる。

Usage:
    python actor.py --persona personas/psyche.md --role "アルベルト（14歳、公爵家嫡出三男）" --worksheet workspace/12-1_take1.md
    python actor.py --persona personas/dominator.md --role "ハインリヒ" --worksheet workspace/12-1_take1.md --scene scene_detail.md
    python actor.py --persona personas/psyche.md --role "アルベルト" --worksheet workspace/12-1_take1.md --temperature 1.0 --max-tokens 1500
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path

DEFAULT_API_URL = "http://192.168.50.24:1234/v1/chat/completions"
DEFAULT_MODEL = "gemma4-26b"
DEFAULT_TEMPERATURE = 0.8
DEFAULT_MAX_TOKENS = 1000


def read_file(path: str) -> str:
    """UTF-8でファイルを読み込む。"""
    return Path(path).read_text(encoding="utf-8")


def build_messages(
    persona: str,
    role: str,
    worksheet: str,
    scene: str | None = None,
    direction: str | None = None,
) -> list[dict]:
    """LLMに渡すメッセージを構築する。"""
    system_prompt = f"""あなたは演劇の役者です。以下のペルソナに基づいて、指定された役を演じてください。

## あなたのペルソナ
{persona}

## あなたの役
{role}

## 演技ルール
- パフォーマンス一体型で出力する（散文に近い形式）
- セリフは「」で囲む
- 内心は（内心：...）で表記する
- 身体の動き・仕草は地の文として書く
- 前の演技（ワークシート）の流れを受けて、自然に応答する
- メタコメント・挨拶・解説は一切禁止。演技のみ出力する
- あなたの担当キャラクターのパートのみ演じる。他キャラクターの行動は書かない"""

    if direction:
        system_prompt += f"\n\n## 監督からの演出指示\n{direction}"

    user_content = ""
    if scene:
        user_content += f"## シーン設定\n{scene}\n\n"
    user_content += f"## ワークシート（ここまでの演技）\n{worksheet}\n\n"
    user_content += "あなたの番です。上の流れを受けて演じてください。"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]


def call_api(
    messages: list[dict],
    api_url: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    """LM StudioのOpenAI互換APIを呼び出す。"""
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.URLError as e:
        print(f"Error: LM Studioに接続できません ({api_url}): {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"Error: APIレスポンスの解析に失敗: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Stage Actor — ローカルLLM演技スクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--persona", required=True, help="ペルソナファイルのパス")
    parser.add_argument("--role", required=True, help="演じる役（キャラ名＋補足）")
    parser.add_argument("--worksheet", required=True, help="ワークシートファイルのパス")
    parser.add_argument("--scene", default=None, help="シーン設定ファイルのパス（任意）")
    parser.add_argument("--direction", default=None, help="監督からの演出指示（任意）")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"モデル名 (default: {DEFAULT_MODEL})")
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE, help=f"温度 (default: {DEFAULT_TEMPERATURE})")
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help=f"最大トークン数 (default: {DEFAULT_MAX_TOKENS})")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help=f"LM Studio API URL (default: {DEFAULT_API_URL})")

    args = parser.parse_args()

    persona = read_file(args.persona)
    worksheet = read_file(args.worksheet)
    scene = read_file(args.scene) if args.scene else None

    messages = build_messages(persona, args.role, worksheet, scene, args.direction)
    result = call_api(messages, args.api_url, args.model, args.temperature, args.max_tokens)

    # 演技結果のみを標準出力に出す（監督がワークシートに追記する）
    print(result)


if __name__ == "__main__":
    main()
