import feedparser
import requests
from datetime import datetime, timezone, timedelta
from config import X_EXPERTS

# X 专家对应的 Google News 搜索关键词
EXPERT_SEARCH = {
    "karpathy": "Andrej Karpathy",
    "ylecun": "Yann LeCun",
    "ilyasut": "Ilya Sutskever",
    "DrJimFan": "Jim Fan AI",
    "fchollet": "Francois Chollet",
    "demishassabis": "Demis Hassabis",
    "AndrewYNg": "Andrew Ng",
    "hwchase17": "Harrison Chase LangChain",
    "drfeifei": "Fei-Fei Li",
    "geoffreyhinton": "Geoffrey Hinton",
}


def fetch_x_posts():
    """通过 Google News RSS 抓取 AI 专家最新动态"""
    all_posts = []
    now = datetime.now(timezone(timedelta(hours=8)))
    cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)

    for expert, search_term in EXPERT_SEARCH.items():
        posts = _fetch_expert_posts(expert, search_term, cutoff)
        all_posts.extend(posts)

    all_posts.sort(key=lambda x: x.get("published", ""), reverse=True)
    return all_posts


def _fetch_expert_posts(expert, search_term, cutoff):
    """从 Google News RSS 抓取单个专家相关新闻"""
    posts = []

    try:
        query = search_term.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })

        if resp.status_code != 200:
            return posts

        feed = feedparser.parse(resp.text)
        for entry in feed.entries[:5]:
            pub_time = _parse_time(entry)
            posts.append({
                "author": expert,
                "title": _clean_title(entry.get("title", "")),
                "summary": _clean_summary(entry.get("summary", "")),
                "link": entry.get("link", ""),
                "published": pub_time.strftime("%Y-%m-%d %H:%M") if pub_time else "",
            })
            if len(posts) >= 3:
                break

    except Exception as e:
        print(f"  抓取 {expert} 失败: {e}")

    return posts


def _parse_time(entry):
    """解析条目时间"""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        from time import mktime
        return datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone(timedelta(hours=8)))
    return None


def _clean_title(text):
    """清理标题"""
    import re
    text = re.sub(r'\s*-\s*Google\s+News\s*$', '', text)
    return text.strip()[:200]


def _clean_summary(text):
    """清理摘要文本"""
    import re
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n+', ' ', text)
    return text.strip()[:500]
