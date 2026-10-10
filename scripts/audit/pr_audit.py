#!/usr/bin/env python3
"""lhg-pr 确定性审计：扫描目标目录下的新闻通稿文件。

输入约定（--target 目录）：*.md 通稿文件（须含 标题/导语/正文/结尾 结构段）

检查：
  PR-STRUCT-001  缺结构段（标题/导语/正文/结尾）（blocker）
  PR-5W1H-001    5W1H 要素缺失（warning，列出缺失项）
  PR-QUOTE-001   有引言但无出处（warning）
  PR-ABS-001     绝对化用语（第一/唯一/首家等极限词）（warning）
  PR-PUNCT-001   半角标点混入中文（warning）
  PR-LEAD-001    导语超过 150 字（warning）

用法：
    python3 pr_audit.py --target <目录> [--format json|text] [--fail-on blocker|warning]

exit code：0=无命中（按 --fail-on 口径），2=有 blocker，1=仅 warning（且 --fail-on=warning）。
零第三方依赖。规则文案均为本项目原创。
"""

import argparse
import json
import os
import re
import sys

VERSION = "1.0.0"
TOOL = "lhg-pr/pr-audit"

STRUCT_SECTIONS = ["标题", "导语", "正文", "结尾"]
W1H_PATTERNS = {
    "何时": r"\d{4}年|\d+月\d+日|今日|昨日|将于|即将",
    "何地": r"北京|上海|广州|深圳|杭州|南京|[省市自治区县区]",
    "何人": r"公司|集团|宣布|有限",
    "何事": r"发布|推出|上线|举行|成立|签约",
    "为何": r"旨在|为了|将助力|推动|意味着",
    "如何": r"通过|采用|依托|基于",
}
QUOTE_RE = re.compile(r"[“”\"]")
ATTRIB_RE = re.compile(r"表示|称|指出|认为|强调|说道|谈到")
ABSOLUTE_WORDS = [
    "第一", "唯一", "首家", "首创", "独家", "第一家",
    "全球首", "全国首", "行业第一", "市场第一",
    "领导者", "龙头", "之最",
]
HALFWIDTH_RE = re.compile(r"[\u4e00-\u9fff][,.:;!?()\[\]]|[,.:;!?()\[\]][\u4e00-\u9fff]")
LEAD_LIMIT = 150


class Finding:
    __slots__ = ("rule_id", "severity", "category", "title", "file", "line", "snippet", "detail")

    def __init__(self, rule_id, severity, category, title, file, line=0, snippet="", detail=""):
        self.rule_id = rule_id
        self.severity = severity
        self.category = category
        self.title = title
        self.file = file
        self.line = line
        self.snippet = snippet
        self.detail = detail

    def to_dict(self):
        return {"rule_id": self.rule_id, "severity": self.severity,
                "category": self.category, "title": self.title,
                "file": self.file, "line": self.line,
                "snippet": self.snippet, "detail": self.detail}


findings = []


def add(rule_id, severity, category, title, file, line=0, snippet="", detail=""):
    findings.append(Finding(rule_id, severity, category, title, file, line, snippet, detail))


def read_text(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def lead_text(text):
    """抽取导语段文本：从“导语”起，到下一个 ## 或文件 1/3 处止。"""
    idx = text.find("导语")
    if idx < 0:
        return ""
    seg = text[idx:]
    m = re.search(r"\n## ", seg[2:])
    if m:
        seg = seg[:m.start() + 2]
    seg = re.sub(r"^#+\s*导语\s*\n?", "", seg).strip()
    return seg


def check_draft(path):
    text = read_text(path)

    # 结构
    missing = [s for s in STRUCT_SECTIONS if s not in text]
    if missing:
        add("PR-STRUCT-001", "blocker", "结构", "通稿缺结构段",
            path, detail="缺少结构段：%s；通稿须含 标题/导语/正文/结尾 四段" % "、".join(missing))

    # 5W1H
    missing_w = [k for k, pat in W1H_PATTERNS.items() if not re.search(pat, text)]
    if missing_w:
        add("PR-5W1H-001", "warning", "要素", "5W1H 要素缺失",
            path, detail="缺失要素：%s；导语中应回答何时/何地/何人/何事/为何/如何"
                         % "、".join(missing_w))

    # 引言出处
    if QUOTE_RE.search(text) and not ATTRIB_RE.search(text):
        idx = QUOTE_RE.search(text).start()
        line = text.count("\n", 0, idx) + 1
        add("PR-QUOTE-001", "warning", "引言", "引言无出处",
            path, line=line,
            detail="第 %d 行附近有引号内容，但全文无“表示/称/指出/认为/强调”等"
                   "出处表述；每段引言都须注明说话人身份与姓名" % line)

    # 绝对化用语
    for kw in ABSOLUTE_WORDS:
        idx = text.find(kw)
        if idx >= 0:
            line = text.count("\n", 0, idx) + 1
            add("PR-ABS-001", "warning", "用语", "绝对化用语",
                path, line=line, snippet=kw,
                detail="第 %d 行命中极限词“%s”；改为可验证的事实表述或删除" % (line, kw))
            break  # 每文件报一次即可

    # 半角标点
    m = HALFWIDTH_RE.search(text)
    if m:
        line = text.count("\n", 0, m.start()) + 1
        add("PR-PUNCT-001", "warning", "标点", "半角标点混入中文",
            path, line=line, snippet=m.group(0),
            detail="第 %d 行“%s”：中文文本请用全角标点（，。；：！？）" % (line, m.group(0)))

    # 导语长度
    lead = lead_text(text)
    n = len(re.sub(r"\s+", "", lead))
    if n > LEAD_LIMIT:
        add("PR-LEAD-001", "warning", "导语", "导语过长",
            path, snippet="导语 %d 字" % n,
            detail="导语共 %d 字，超过 %d 字上限；导语只回答 5W1H，细节移到正文" % (n, LEAD_LIMIT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--format", default="json", choices=["json", "text"])
    ap.add_argument("--fail-on", default="blocker", choices=["blocker", "warning"])
    args = ap.parse_args()

    target = os.path.abspath(args.target)
    if os.path.isdir(target):
        files = [os.path.join(target, f) for f in sorted(os.listdir(target))]
    else:
        files = [target]

    for p in files:
        if os.path.isfile(p) and os.path.basename(p).endswith(".md"):
            check_draft(p)

    n_blocker = sum(1 for f in findings if f.severity == "blocker")
    n_warning = sum(1 for f in findings if f.severity == "warning")
    summary = {"tool": TOOL, "version": VERSION, "target": target,
               "blocker": n_blocker, "warning": n_warning,
               "total": len(findings)}

    if args.format == "json":
        out = {"summary": summary,
               "findings": [f.to_dict() for f in findings]}
        sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        lines = ["[%s] %s blocker=%d warning=%d" % (TOOL, target, n_blocker, n_warning)]
        for f in findings:
            lines.append("%s %s %s:%s %s" % (f.severity.upper(), f.rule_id, f.file, f.line, f.title))
            if f.detail:
                lines.append("    " + f.detail)
        sys.stdout.write("\n".join(lines) + "\n")

    if n_blocker:
        return 2
    if n_warning and args.fail_on == "warning":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
