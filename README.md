<!-- About 简介（推送后填写到仓库 About 栏）：
PR发稿专家：事件→通稿三版本→媒体清单→发布节奏表 ｜ 一键安装：/plugin marketplace add lhg-plugs/lhg-pr
-->
<!-- topics（推送后打）：claude-code, claude-plugin, agent-skills, pr, press-release, media-relations -->

# lhg-pr：PR发稿专家，事件到发布一条龙

> **一句话介绍**：给 AI 编程助手装上"PR发稿专家"——事件信息输入 → 通稿结构（标题/导语/正文/引言/结尾）→ 多版本输出（短讯版/长稿版/社交媒体版）→ 媒体清单 → 发布节奏表；**5W1H 缺失、引言无出处、极限词、错别字四重自查，确定性审计 + 极限词硬门双保险**。
>
> **一键安装**：在 Claude Code 里运行
> ```
> /plugin marketplace add lhg-plugs/lhg-pr
> /plugin install lhg-pr@lhg-plugs
> ```

## 它是什么

`lhg-pr` 是一个 Claude Code 插件（plugin 为主、skill 为辅）：

- **3 个命令**（小白入口）：`pr` 发稿一条龙（三版通稿+媒体清单+节奏表），`pr-media` 媒体清单与发布节奏，`pr-check` 通稿四重自查
- **4 个平台中立 skill**（方法论，可移植到豆包/Workbuddy 等 agent 平台）：新闻通稿写作五步法、标题导语技巧、媒体清单管理、发布节奏规划
- **2 个专家 agent**：通稿写手、审稿编辑
- **1 个极限词硬门 hook**：写入文件命中绝对化用语（第一/唯一/首家/首创/独家/行业第一等）直接拦截，可一键关闭
- **6 条确定性审计规则**：纯 Python 标准库、零第三方依赖，含 5W1H 缺失检测、引言无出处告警、极限词检测、半角标点与导语长度检查

## 四重自查

1. **5W1H 是否齐全**：导语必须回答何时/何地/何人/何事/为何/如何，缺项即告警。
2. **引言是否有出处**：每段引号内容必须有"XX（姓名+职务）表示"类出处，无实录不许编。
3. **极限词**：第一/唯一/首家等绝对化用语，hook 写入时拦截、审计兜底告警。
4. **错别字与标点**：半角标点混入中文告警；"的/地/得""在/再"人工复核。

## 3 个命令用法

| 命令 | 作用 | 示例 |
|---|---|---|
| `/lhg-pr:pr` | 事件→三版通稿→媒体清单→发布节奏表 | `/lhg-pr:pr "10月11日蓝鲸科技在北京发布智能客服系统"` |
| `/lhg-pr:pr-media` | 媒体三级清单 + T-3/T0/T+1/T+7 节奏表 | `/lhg-pr:pr-media "智能客服发布，目标电商金融媒体"` |
| `/lhg-pr:pr-check` | 四重自查：结构/要素/引言/用语/标点 | `/lhg-pr:pr-check ./通稿目录` |

## 目录结构

```
lhg-pr/
├── .claude-plugin/          # plugin.json（插件清单）+ marketplace.json（本仓即市场）
├── commands/                # 3 个命令：pr / pr-media / pr-check
├── skills/                  # 4 个平台中立 skill（通稿写作/标题导语/媒体清单/发布节奏）
├── agents/                  # 2 个专家 agent（writer / editor）
├── hooks/                   # 极限词拦截 hook（fail-open，可一键关闭）
├── scripts/audit/           # 确定性审计：pr_audit.py（零第三方依赖）
├── fixtures/                # 好/坏对照用例
├── smoke_test.py            # 冒烟测试
├── ATTRIBUTION.md           # 灵感来源声明
└── LICENSE                  # MIT
```

## 什么时候用 / 什么时候不用（FAQ）

**Q：它能保证稿子被媒体采用吗？**
A：不能。发稿是概率工作，本插件保证的是"稿子质量"（结构/要素/用语/标点），不承诺转载量和头条。承诺结果属于虚假承诺。

**Q：没有发言人原话，能写引言段吗？**
A：不能。没有录音或文字实录，引言段就空着——编造"创始人表示"是新闻红线，审计会告警。

**Q：极限词被 hook 拦了，但我是"全球首家"有数据支撑，怎么办？**
A：两种处理：① 把"全球首家"改成可验证的事实表述（具体时间+具体事项+数据来源）；② 确认合规后 `export LHG_PR_ABS_OFF=1` 关闭本次拦截。

**Q：一定要用 Claude Code 吗？**
A：`skills/` 下的方法论是平台中立的纯 Markdown，可直接搬到豆包、Workbuddy 等 agent 平台用。只有 commands/agents/hooks 需要 Claude Code。

**Q：媒体联系人电话可以帮我找吗？**
A：不可以编造。不知道的联系方式一律留"待补充"占位，发布前必须拨测确认。

**Q：hook 把我正常的内容拦了怎么办？**
A：两种处理：① 确认内容确实合规后，`export LHG_PR_ABS_OFF=1` 关闭本次拦截；② 到本仓库提 issue（标题前缀 `[hook]`），我们优化关键词表。

## 自迭代

- 每个 skill 末尾有「自检与反馈」节：质检门 + 标准冒烟用例 + 一键提 issue。
- 发现规则误报/漏报、方法论不合理：到本仓库提 issue（标题带对应 skill 前缀，如 `[lhg-pr-news]`），附通稿类型与期望行为。

## 出品：刘洪光

刘洪光（https://github.com/lhg-skills）出品，lhg-plugs「小白专家插件」系列之一。
灵感来源见 [ATTRIBUTION.md](./ATTRIBUTION.md)（借鉴思路，实现与文案均为原创）。
