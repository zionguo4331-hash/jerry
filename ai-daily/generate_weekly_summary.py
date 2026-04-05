import requests
from datetime import datetime, timezone, timedelta
from config import ZHIPU_API_KEY, ZHIPU_API_URL, ZHIPU_MODEL


def generate_weekly_summary(x_posts, github_trending, producthunt):
    """调用智谱 GLM-4-flash 生成 AI 周报摘要"""
    prompt = _build_weekly_prompt(x_posts, github_trending, producthunt)

    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": ZHIPU_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "你是一位资深的 AI 领域分析师，擅长将一周的技术资讯整理成有深度、有洞察的中文周报。请用 Markdown 格式输出，重点突出、语言精炼，要有趋势分析和观点总结。"
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.7,
        "max_tokens": 5000,
    }

    resp = requests.post(ZHIPU_API_URL, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()

    return data["choices"][0]["message"]["content"]


def _build_weekly_prompt(x_posts, github_trending, producthunt):
    """构建 LLM 周报 Prompt"""
    now = datetime.now(timezone(timedelta(hours=8)))
    week_start = now - timedelta(days=7)

    x_section = "\n".join([
        f"- @{p['author']} ({p['published']}): {p.get('title', '')} {p.get('summary', '')}"
        for p in x_posts[:30]
    ]) if x_posts else "（暂无内容）"

    github_section = "\n".join([
        f"- [{r['name']}]({r['url']}) {r.get('language', '')} | {r.get('stars_this_week', '')} | {r.get('description', '')}"
        for r in github_trending[:20]
    ]) if github_trending else "（暂无内容）"

    ph_section = "\n".join([
        f"- {p['name']} | {p.get('description', '')} | 投票: {p.get('votes', '')}"
        for p in producthunt[:20]
    ]) if producthunt else "（暂无内容）"

    return f"""请根据以下信息生成一份 AI 周报摘要（{week_start.strftime('%Y-%m-%d')} 至 {now.strftime('%Y-%m-%d')}），格式要求：

# AI 周报 - {week_start.strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')}

## 一、AI 专家观点汇总
（按专家分类，汇总一周内的核心观点，提炼出最重要的趋势和信号）
{x_section}

## 二、GitHub 本周热门项目 Top 20
（按 stars 排序，说明项目用途、技术栈和为什么火）
{github_section}

## 三、Product Hunt 本周值得关注的产品
（分类介绍，如：AI 工具、开发者工具、效率工具等）
{ph_section}

## 四、本周 AI 领域三大趋势
（从以上信息中提炼出 3 个最重要的趋势或信号，每个趋势用 2-3 句话说明）

## 五、下周值得关注什么
（基于本周动态，预测下周可能的热点和值得关注的方向）

要求：
1. 中文输出
2. 语言精炼，有深度和洞察
3. 不要简单罗列，要有分析和观点
4. 保留重要链接方便深入阅读
5. 格式清晰，适合手机阅读
"""
