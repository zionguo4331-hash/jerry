import requests
from bs4 import BeautifulSoup

# 使用 Product Hunt 的 RSS 源和备用方案
PRODUCTHUNT_RSS = "https://www.producthunt.com/feed"
PRODUCTHUNT_URL = "https://www.producthunt.com/"


def fetch_producthunt():
    """抓取 Product Hunt 当日热门产品"""
    products = _fetch_rss()
    if not products:
        products = _fetch_web()
    return products


def _fetch_rss():
    """通过 RSS 抓取"""
    try:
        import feedparser
        resp = requests.get(PRODUCTHUNT_RSS, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        resp.raise_for_status()

        feed = feedparser.parse(resp.text)
        products = []
        for entry in feed.entries[:15]:
            products.append({
                "name": entry.get("title", ""),
                "description": entry.get("summary", "")[:200],
                "votes": "",
                "url": entry.get("link", ""),
            })
        return products
    except Exception as e:
        print(f"  Product Hunt RSS 失败: {e}")
        return []


def _fetch_web():
    """通过网页抓取（备用）"""
    try:
        resp = requests.get(PRODUCTHUNT_URL, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        products = []

        links = soup.select("a[href*='/posts/']")
        seen = set()
        for link in links[:20]:
            text = link.get_text(strip=True)
            if text and len(text) < 80 and text not in seen:
                seen.add(text)
                href = link.get("href", "")
                if href and not href.startswith("http"):
                    href = f"https://www.producthunt.com{href}"
                products.append({
                    "name": text,
                    "description": "",
                    "votes": "",
                    "url": href,
                })
        return products
    except Exception as e:
        print(f"  Product Hunt Web 失败: {e}")
        return []
