import os

# X 专家列表
X_EXPERTS = [
    "karpathy",
    "ylecun",
    "ilyasut",
    "DrJimFan",
    "fchollet",
    "demishassabis",
    "AndrewYNg",
    "hwchase17",
    "drfeifei",
    "geoffreyhinton",
]

# RSSHub 实例列表（主用 + 备用）
RSSHUB_INSTANCES = [
    "https://rsshub.app",
    "https://rsshub.rssforever.com",
    "https://rss.shab.fun",
    "https://hub.slarker.me",
    "https://rsshub.pseudoyu.com",
]

# GitHub Trending URL
GITHUB_TRENDING_URL = "https://github.com/trending?since=daily&spoken_language_code="

# Product Hunt URL
PRODUCTHUNT_URL = "https://www.producthunt.com/"

# 智谱 API
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "")
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
ZHIPU_MODEL = "glm-4-flash"

# Server酱
SERVER_SEND_KEY = os.environ.get("SERVER_SEND_KEY", "SCT333682T5018PLxaMo2NjVXF7qPihAek")
SERVER_API_URL = "https://sctapi.ftqq.com"
