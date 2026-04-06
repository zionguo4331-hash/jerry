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

    return f"""你是一个专业的科技主编。请每天阅读原始抓取数据（包含 AI 专家推文、GitHub 趋势、Product Hunt 产品）。
你需要剔除闲聊、无意义的转发和技术细节，提取出最有价值的信息，并严格按照以下 Markdown 格式生成微信早报。

要求：
1. 语气简练、专业、客观，绝对不要有废话。
2. 每一个条目必须包含：名称、一句话解释核心价值/观点、对受众的意义。
3. 请使用 Emoji 作为视觉分隔。
4. 总字数控制在 800 字以内，适合手机端快速阅读。

【原始数据】：

## AI 专家动态
{x_section}

## GitHub Trending
{github_section}

## Product Hunt
{ph_section}

【输出格式】：
# 🌅 每日 AI 与科技速递 {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

## 🧠 专家前沿洞察 (挑选最有价值的 3-5 条)
* 🗣️ **[专家姓名]**：[一句话提炼观点或他推荐的新技术]
  - 💡 **价值点**：[这对行业或开发者意味着什么]

## 💻 GitHub 飙升开源库 (挑选最有潜力的 3-5 个)
* 🔥 **[项目名称]** (语言/主要技术标签)
  - 🛠️ **一句话简介**：[这个项目到底能用来解决什么问题？]
  - 🌟 **亮点**：[例如：取代了传统的 XXX / 体积只有几 KB]

## 🚀 Product Hunt 热门新奇特 (挑选最创新的 3 个)
* 🦄 **[产品名称]** - 🎯 **一句话简介**：[它满足了什么具体场景的需求？]"""

