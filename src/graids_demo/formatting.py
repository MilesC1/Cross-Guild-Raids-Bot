"""Reusable formatting helpers adapted from the GRAIDS message bridge.

Unlike the full bridge, these functions do not access Discord or user data.
The original code removes whitespace at chunk boundaries; this behavior is
preserved and documented here. The docstring was clarified accordingly.
"""
from __future__ import annotations


def edited_destination_content(
    content: str,
    trigger_raids: tuple[str, ...],
) -> str:
    """Build edit text without live role mentions, preventing repeat pings."""
    if not trigger_raids:
        return content
    prefix = " ".join(f"[{raid_name}]" for raid_name in trigger_raids)
    return f"{prefix}\n{content}" if content else prefix


def split_text(content: str, limit: int) -> list[str]:
    """Split text at natural boundaries; trim whitespace at those breaks."""
    if limit <= 0:
        raise ValueError("limit must be greater than zero")
    if len(content) <= limit:
        return [content]

    chunks: list[str] = []
    remaining = content
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break

        split_at = remaining.rfind("\n", 0, limit + 1)
        if split_at <= 0:
            split_at = remaining.rfind(" ", 0, limit + 1)
        if split_at <= 0:
            split_at = limit

        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()

    return chunks
