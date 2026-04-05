import requests
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from config import GITHUB_TRENDING_URL


def fetch_github_trending_weekly():
    """抓取 GitHub Trending 周榜"""
    try:
        url = "https://github.com/trending?since=weekly&spoken_language_code="
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        repos = []

        for article in soup.select("article.Box-row")[:25]:
            repo_info = _parse_repo(article)
            if repo_info:
                repos.append(repo_info)

        return repos
    except Exception as e:
        print(f"GitHub Trending 周榜抓取失败: {e}")
        return []


def _parse_repo(article):
    try:
        h2 = article.select_one("h2 a")
        if not h2:
            return None

        repo_name = h2.get("href", "").strip("/")
        description_el = article.select_one("p.col-9")
        description = description_el.get_text(strip=True) if description_el else ""

        stars_this_week = ""
        stars_span = article.select_one("span.d-inline-block.float-sm-right")
        if stars_span:
            stars_this_week = stars_span.get_text(strip=True)

        language = ""
        lang_el = article.select_one("span[itemprop='programmingLanguage']")
        if lang_el:
            language = lang_el.get_text(strip=True)

        return {
            "name": repo_name,
            "description": description[:200],
            "language": language,
            "stars_this_week": stars_this_week,
            "url": f"https://github.com/{repo_name}",
        }
    except Exception:
        return None
