#!/usr/bin/env python3
"""lhg-pr 硬门：极限词拦截。

触发：PreToolUse / Edit|Write。扫描本次写入/编辑的文件内容，
若命中绝对化用语（第一/唯一/首家/首创/独家/行业第一等极限词），
以 exit code 2 拦截该操作，并给出改写指引。

逃生方式（按推荐度排序）：
  1. LHG_PR_ABS_OFF=1（环境变量，当前会话有效；关闭后
     极限词拦截不再触发，但审计脚本的 PR-ABS-001
     仍会在 pr-check 时报 warning）。
  2. /plugin disable lhg-pr（整个插件停用，hooks 不再触发）。

设计原则：只有"命中极限词"才拦截；内部出错一律 fail-open
（直接放行，不报错）；零第三方依赖。

注意：本 hook 只做关键词层面的硬拦截，真正的合规判断
（上下文、语气）仍由 agent 按 skill 规范负责。
"""

import json
import os
import sys

# 绝对化用语/极限词表（原创整理：新闻稿常见违禁表述）
ABSOLUTE_WORDS = [
    "第一", "唯一", "首家", "首创", "独家", "第一家",
    "全球首", "全国首", "行业第一", "市场第一",
    "领导者", "龙头", "之最", "绝无仅有",
]

REWRITE_GUIDE = (
    "改写指引：删除极限词，用可验证的事实替代——"
    "“第一”→ 具体排名与数据来源；“唯一”→ 具体差异点描述；"
    "“首家”→ 具体时间+具体事项；无法验证就删掉。"
)


def extract_text(tool_input):
    """从 Edit/Write 的输入中抽取待写入文本。"""
    parts = []
    for key in ("content", "new_string", "old_string", "file_text"):
        v = tool_input.get(key)
        if isinstance(v, str) and v:
            parts.append(v)
    return "\n".join(parts)


def find_hits(text):
    hits = []
    for kw in ABSOLUTE_WORDS:
        if kw in text:
            hits.append(kw)
    return hits


def main() -> int:
    if os.environ.get("LHG_PR_ABS_OFF") == "1":
        return 0  # 逃生开关

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # 输入解析失败：fail-open

    tool_input = payload.get("tool_input", {}) or {}
    text = extract_text(tool_input)
    if not text:
        return 0

    try:
        hits = find_hits(text)
    except Exception:
        return 0  # 内部错误：fail-open

    if not hits:
        return 0

    msg = (
        "⛔ 极限词硬门（lhg-pr）：本次写入内容命中绝对化用语：%s。\n"
        "新闻通稿应避免无法验证的极限词。\n%s\n"
        "确认为合规内容但被误拦：export LHG_PR_ABS_OFF=1 后重试。"
        % ("、".join(hits), REWRITE_GUIDE)
    )
    sys.stderr.write(msg + "\n")
    return 2  # exit 2 = 拦截本次工具调用


if __name__ == "__main__":
    sys.exit(main())
