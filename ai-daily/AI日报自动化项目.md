# AI 日报自动化项目

> 每天定时抓取 AI 资讯，AI 生成摘要后推送到微信，同时同步到 Obsidian

## 项目概述

搭建一个自动化系统，每天北京时间 8:00 自动执行以下任务：
1. 抓取 10 位 AI 一线专家的最新动态
2. 抓取 GitHub Trending 增长最快的项目
3. 抓取 Product Hunt 热门产品
4. 调用智谱 GLM-4-flash 生成结构化摘要
5. 通过 Server酱 推送到微信
6. 保存到 Obsidian 笔记库

## 关注的 AI 专家

| # | X 账号 | 身份 |
|---|--------|------|
| 1 | @karpathy | Andrej Karpathy, AI 教育/前 Tesla AI 总监 |
| 2 | @ylecun | Yann LeCun, Meta 首席AI科学家 |
| 3 | @ilyasut | Ilya Sutskever, OpenAI 联合创始人 |
| 4 | @DrJimFan | Jim Fan, NVIDIA 科学家 |
| 5 | @fchollet | François Chollet, Keras 作者 |
| 6 | @demishassabis | Demis Hassabis, DeepMind CEO |
| 7 | @AndrewYNg | 吴恩达, AI 教育先驱 |
| 8 | @hwchase17 | Harrison Chase, LangChain 创始人 |
| 9 | @drfeifei | 李飞飞, Stanford 教授 |
| 10 | @geoffreyhinton | Geoffrey Hinton, AI 教父 |

## 技术架构

```
GitHub Actions (每日 8:00 触发)
    ├── 1. 抓取 AI 专家动态 (Google News RSS)
    ├── 2. 抓取 GitHub Trending (HTML 解析)
    ├── 3. 抓取 Product Hunt (RSS 源)
    ├── 4. 调用智谱 GLM-4-flash 生成摘要
    ├── 5. 通过 Server酱 推送到微信
    └── 6. 保存到 Obsidian
```

## 数据源

| 模块 | 数据源 | 说明 |
|------|--------|------|
| X 专家 | Google News RSS | 搜索专家相关新闻，比 RSSHub 更稳定 |
| GitHub Trending | github.com/trending | 解析 HTML 获取日榜/周榜 |
| Product Hunt | producthunt.com/feed | RSS 源 + 网页解析备用 |
| AI 摘要 | 智谱 GLM-4-flash | 成本低，中文能力强 |
| 推送 | Server酱 v3 | 推送到微信 |

## 项目结构

```
ai-daily/
├── config.py                     # 配置常量
├── fetch_x_posts.py              # 日报：抓取 AI 专家动态
├── fetch_x_posts_weekly.py       # 周报：抓取一周动态
├── fetch_github_trending.py      # 日报：GitHub 日榜
├── fetch_github_trending_weekly.py # 周榜：GitHub 周榜
├── fetch_producthunt.py          # Product Hunt 抓取
├── generate_summary.py           # 日报摘要生成
├── generate_weekly_summary.py    # 周报摘要生成
├── send_wechat.py                # Server酱推送
├── save_obsidian.py              # 保存到 Obsidian
├── main.py                       # 日报入口
├── main_weekly.py                # 周报入口
└── requirements.txt              # Python 依赖

.github/workflows/
└── ai-daily.yml                  # GitHub Actions 定时任务

AI日报/                           # Obsidian 日报目录
└── AI日报-YYYY-MM-DD.md         # 每日生成的日报
```

## Prompt 系统（核心）

`generate_summary.py` 中使用的高级技术情报分析师 Prompt：

```
你是一位服务于资深开发者的「高级技术情报分析师」。请阅读我提供的原始抓取数据（包含 AI 专家推文、GitHub 趋势、Product Hunt 产品），为其撰写每日情报内参。

【核心原则】
1. 严禁使用重复的 Emoji 表情符号，并用采用极简、严肃的纯文字排版。
2. 拒绝过度精简。必须保留专家观点中的"技术细节/推演逻辑"和开源项目中的"底层技术栈/核心特性"。
3. 必须在开头增加「今日情报总览」，用一段话高度凝练今天最重要的行业风向。
4. 剔除问候语和结尾的客套废话，直接输出正文。

【排版与内容输出规范（严格按此格式生成）】

# 每日科技与 AI 情报内参 (YYYY-MM-DD)

### 📌 今日情报总-overview
（请基于今天的所有数据，用 80-150 字的高度凝练语言，总结出今天科技圈/开源界最核心的 1-2 个技术演进趋势或重大突破，让我一眼看透全局脉络。）

---
### 一、 专家前沿洞察
（挑选出具有行业增量信息的 4-7 条推文）

【专家姓名】
- 核心论点：（提炼观点）
- 深度解析：（保留逻辑推演、数据支撑或深层影响）

---
### 二、 GitHub 潜力开源库
（挑选出最具实用价值的 4-5 个项目）

【项目名称】 | [编程语言/技术标签]
- 解决痛点：（具体解决了开发场景中的什么问题？）
- 核心特性：（列出技术文档中提到的硬核功能或底层架构亮点）

---
### 三、 Product Hunt 趋势产品
（挑选 3-5 个最具商业启发的产品）

【产品名称】
- 产品形态：（例如：基于 Electron 的本地客户端 / 浏览器插件）
- 核心场景：（切中了什么具体的用户需求或商业模式？）
```

## 配置项

| 配置 | 值 | 说明 |
|------|-----|------|
| ZHIPU_API_KEY | `15a25c9ada...` | 智谱 API Key |
| SERVER_SEND_KEY | `SCT333682T...` | Server酱 SendKey |
| GH_TOKEN | (可选) | GitHub Token，用于自动提交日报到仓库 |
| 执行时间 | 每天 8:00 (UTC 0:00) | cron: `0 0 * * *` |

## GitHub Secrets 配置

在 GitHub 仓库 Settings → Secrets → Actions 中添加：
- `ZHIPU_API_KEY`（必须）
- `SERVER_SEND_KEY`（必须）
- `GH_TOKEN`（可选，用于自动提交日报）

## 使用方式

### 本地运行
```bash
cd ai-daily
python main.py
```

### 手动触发 GitHub Actions
GitHub → Actions → AI Daily → Run workflow

## 依赖安装

```bash
pip install -r ai-daily/requirements.txt
```

## 创建日期

2026-04-04

## 更新日志

### 2026-04-06
- 优化 Prompt 为「高级技术情报分析师」风格
- 增加今日情报总览功能
- 增加保存到 Obsidian 功能
- 极简严肃纯文字排版
