import requests
import json
from datetime import datetime
from config import ZHIPU_API_KEY, ZHIPU_API_URL, ZHIPU_MODEL


def generate_summary(x_posts, github_trending, producthunt):
    """调用智谱 GLM-4-flash 生成 AI 日报摘要"""
    today = datetime.now().strftime('%Y-%m-%d')
    prompt = _build_prompt(x_posts, github_trending, producthunt, today)

    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": ZHIPU_MODEL,
        "messages": [
            {
                "role": "system",
                "content": f"""你是一位服务于资深开发者的「高级技术情报分析师」。请阅读我提供的原始抓取数据（包含 AI 专家推文、GitHub 趋势、Product Hunt 产品），为其撰写每日情报内参。

【核心原则】
1. 严禁使用重复的 Emoji 表情符号，并用采用极简、严肃的纯文字排版。
2. 拒绝过度精简。必须保留专家观点中的"技术细节/推演逻辑"和开源项目中的"底层技术栈/核心特性"。
3. 必须在开头增加「今日情报总览」，用一段话高度凝练今天最重要的行业风向。
4. 剔除问候语和结尾的客套废话，直接输出正文。

【排版与内容输出规范（严格按此格式生成）】

# 每日科技与 AI 情报内参 ({today})

### 📌 今日情报总览
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
- 核心场景：（切中了什么具体的用户需求或商业模式？）"""
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
    }

    resp = requests.post(ZHIPU_API_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    return data["choices"][0]["message"]["content"]


def _build_prompt(x_posts, github_trending, producthunt, today):
    """构建 LLM Prompt"""
    x_section = "\n".join([
        f"- @{p['author']}: {p.get('title', '')} {p.get('summary', '')}"
        for p in x_posts[:30]
    ]) if x_posts else "（暂无内容）"

    github_section = "\n".join([
        f"- {r['name']} | {r.get('language', '')} | {r.get('stars_today', '')} | {r.get('description', '')}"
        for r in github_trending[:20]
    ]) if github_trending else "（暂无内容）"

    ph_section = "\n".join([
        f"- {p['name']} | {p.get('description', '')} | 投票: {p.get('votes', '')}"
        for p in producthunt[:20]
    ]) if producthunt else "（暂无内容）"

    return f"""【原始数据 - 日期：{today}】

## AI 专家推文
{x_section}

## GitHub 趋势
{github_section}

## Product Hunt
{ph_section}

请严格按照上述格式要求生成今日情报内参。日期必须是 {today}，格式如：# 每日科技与 AI 情报内参 ({today})"""