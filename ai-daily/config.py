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

# 智谱 API（从环境变量读取，GitHub Actions 中由 secrets 注入）
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY") or os.environ.get("ZHIPU_API_KEY_SECRET")
if not ZHIPU_API_KEY:
    print("⚠️  警告: ZHIPU_API_KEY 未配置，请检查 GitHub Secrets")
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
ZHIPU_MODEL = "glm-4-flash"

# Server酱 - 支持多个微信（兼容新旧 secret 名称）
SERVER_SEND_KEY = os.environ.get("SERVER_SEND_KEYS") or os.environ.get("SERVER_SEND_KEY", "")
SERVER_SEND_KEYS = os.environ.get("SERVER_SEND_KEYS", SERVER_SEND_KEY) or "SCT333682T5018PLxaMo2NjVXF7qPihAek,SCT336623Tzt38wyz3BK1FOPiMimjS39NT"
if isinstance(SERVER_SEND_KEYS, str):
    SERVER_SEND_KEYS = [k.strip() for k in SERVER_SEND_KEYS.split(",") if k.strip()]
SERVER_API_URL = "https://sctapi.ftqq.com"
