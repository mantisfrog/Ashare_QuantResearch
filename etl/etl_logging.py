from __future__ import annotations

import os
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import TypeVar


PROGRESS_BAR_WIDTH = 28
T = TypeVar("T")


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, remaining = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{remaining:02d}s"
    return f"{minutes}m{remaining:02d}s"


def print_progress(
    label: str,
    current: int,
    total: int,
    detail: str = "",
) -> None:
    if total > 0:
        ratio = min(max(current / total, 0), 1)
        filled = int(PROGRESS_BAR_WIDTH * ratio)
        bar = "#" * filled + "-" * (PROGRESS_BAR_WIDTH - filled)
        text = f"\r{label} [{bar}] {current}/{total} {ratio:6.2%}"
    else:
        text = f"\r{label} {current}"
    if detail:
        text += f" {detail}"
    print(text, end="", flush=True)
    if total > 0 and current >= total:
        print(flush=True)


def append_summary(component: str, message: str) -> None:
    log_path = os.environ.get("ETL_SUMMARY_LOG")
    if not log_path:
        return

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp} [{component}] {message}\n")


def output_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def capture_output(
    function: Callable[..., T],
    *args: object,
    **kwargs: object,
) -> tuple[T, list[str]]:
    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = function(*args, **kwargs)
    except Exception as error:
        captured = output_lines(stdout.getvalue()) + output_lines(stderr.getvalue())
        setattr(error, "_captured_output", captured)
        raise
    captured = output_lines(stdout.getvalue()) + output_lines(stderr.getvalue())
    return result, captured


def captured_output_from_error(error: Exception) -> list[str]:
    captured = getattr(error, "_captured_output", [])
    if isinstance(captured, list):
        return [str(line) for line in captured]
    return []


def truncate_message(message: str, limit: int = 160) -> str:
    if len(message) <= limit:
        return message
    return message[: limit - 3] + "..."


def summarize_messages(
    messages: Iterable[str] | Mapping[str, int],
    limit: int = 5,
) -> str:
    counter: Counter[str]
    if isinstance(messages, Mapping):
        counter = Counter({str(key): int(value) for key, value in messages.items()})
    else:
        counter = Counter(str(message) for message in messages)

    if not counter:
        return ""

    parts: list[str] = []
    shown_total = 0
    for message, count in counter.most_common(limit):
        shown_total += count
        prefix = f"{count}x " if count > 1 else ""
        parts.append(prefix + truncate_message(message))

    remaining = sum(counter.values()) - shown_total
    if remaining:
        parts.append(f"{remaining} more line(s)")

    return "; ".join(parts)


def report_captured_output(
    component: str,
    messages: Mapping[str, int],
    label: str = "suppressed output",
) -> None:
    total = sum(int(value) for value in messages.values())
    if total <= 0:
        return

    detail = summarize_messages(messages)
    print(f"{label}: lines={total}; {detail}", flush=True)
    append_summary(component, f"{label} lines={total} {detail}")
