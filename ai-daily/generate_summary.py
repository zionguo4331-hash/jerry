import requests
import json
from config import ZHIPU_API_KEY, ZHIPU_API_URL, ZHIPU_MODEL


def generate_summary(x_posts, github_trending, producthunt):
    """调用智谱 GLM-4-flash 生成 AI 日报摘要"""
    prompt = _build_prompt(x_posts, github_trending, producthunt)

    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": ZHIPU_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "你是一位专业的 AI 领域分析师，擅长将技术资讯整理成简洁清晰的中文日报。请用 Markdown 格式输出，重点突出、语言精炼。"
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


def _build_prompt(x_posts, github_trending, producthunt):
    """构建 LLM Prompt"""
    x_section = "\n".join([
        f"- @{p['author']} ({p['published']}): {p.get('title', '')} {p.get('summary', '')}"
        for p in x_posts[:20]
    ]) if x_posts else "（暂无内容）"

    github_section = "\n".join([
        f"- [{r['name']}]({r['url']}) {r.get('language', '')} | {r.get('stars_today', '')} | {r.get('description', '')}"
        for r in github_trending[:15]
    ]) if github_trending else "（暂无内容）"

    ph_section = "\n".join([
        f"- {p['name']} | {p.get('description', '')} | 投票: {p.get('votes', '')}"
        for p in producthunt[:15]
    ]) if producthunt else "（暂无内容）"

    return f"""请根据以下信息生成一份 AI 日报摘要，格式要求：

# AI 日报 - {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

## 一、AI 专家动态
（汇总 X 上专家的最新观点，提炼核心要点，每条 1-2 句话）
{x_section}

## 二、GitHub 热门项目
（列出增长最快的项目，说明项目用途和亮点）
{github_section}

## 三、Product Hunt 热门产品
（介绍今日热门产品，一句话说明功能）
{ph_section}

## 四、今日总结
（用 3-5 句话总结今天 AI 领域最值得关注的趋势和事件）

要求：
1. 中文输出
2. 语言精炼，避免废话
3. 重点突出，有洞察
4. 保留原文链接方便深入阅读
"""
