#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

ENV_FILE = ".env"


def load_env_file(path: str = ENV_FILE) -> None:
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def send_message(token: str, chat_id: str, text: str) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    load_env_file()
    parser = argparse.ArgumentParser(description="Send a Telegram message.")
    parser.add_argument("--token", default=os.environ.get("TELEGRAM_BOT_TOKEN"), help="Bot token")
    parser.add_argument("--chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"), help="Target chat id")
    parser.add_argument("--text", default="Hi!", help="Message text")
    args = parser.parse_args()

    if not args.token:
        print("Missing bot token. Use --token or TELEGRAM_BOT_TOKEN.", file=sys.stderr)
        return 1
    if not args.chat_id:
        print("Missing chat id. Use --chat-id or TELEGRAM_CHAT_ID.", file=sys.stderr)
        return 1

    result = send_message(args.token, args.chat_id, args.text)
    if not result.get("ok"):
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print("Message sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
