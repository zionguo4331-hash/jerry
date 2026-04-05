# AI 日报自动化项目

> 每天定时抓取 AI 资讯，AI 生成摘要后推送到微信

## 项目概述

搭建一个自动化系统，每天北京时间 8:00 自动执行以下任务：
1. 抓取 10 位 AI 一线专家的最新动态
2. 抓取 GitHub Trending 增长最快的项目
3. 抓取 Product Hunt 热门产品
4. 调用智谱 GLM-4-flash 生成结构化摘要
5. 通过 Server酱 推送到微信

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
    └── 5. 通过 Server酱 推送到微信
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
├── fetch_github_trending_weekly.py # 周报：GitHub 周榜
├── fetch_producthunt.py          # Product Hunt 抓取
├── generate_summary.py           # 日报摘要生成
├── generate_weekly_summary.py    # 周报摘要生成
├── send_wechat.py                # Server酱推送
├── main.py                       # 日报入口
├── main_weekly.py                # 周报入口
└── requirements.txt              # Python 依赖

.github/workflows/
└── ai-daily.yml                  # GitHub Actions 定时任务
```

## 配置项

| 配置 | 值 | 说明 |
|------|-----|------|
| ZHIPU_API_KEY | `15a25c9ada...` | 智谱 API Key |
| SERVER_SEND_KEY | `SCT333682T...` | Server酱 SendKey |
| 执行时间 | 每天 8:00 (UTC 0:00) | cron: `0 0 * * *` |

## GitHub Secrets 配置

在 GitHub 仓库 Settings → Secrets → Actions 中添加：
- `ZHIPU_API_KEY`
- `SERVER_SEND_KEY`

## 使用方式

### 日报
```bash
cd ai-daily
python main.py
```

### 周报
```bash
cd ai-daily
python main_weekly.py
```

### 手动触发 GitHub Actions
GitHub → Actions → AI Daily → Run workflow

## 依赖安装

```bash
pip install -r ai-daily/requirements.txt
```

## 创建日期

2026-04-04
