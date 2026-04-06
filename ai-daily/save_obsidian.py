import os
import requests
from datetime import datetime
from pathlib import Path


OBSIDIAN_REPO = "zionguo4331-hash/jerry"
OBSIDIAN_DIR = "AI日报"


def save_to_obsidian(summary, github_token=None):
    """将日报保存到 GitHub 仓库（会自动同步到 Obsidian）"""
    github_token = github_token or os.environ.get("GITHUB_TOKEN")
    if not github_token:
        github_token = os.environ.get("GH_TOKEN")
    
    if not github_token:
        print("  未配置 GitHub Token，跳过保存到 Obsidian")
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"AI日报-{today}.md"
    filepath = f"{OBSIDIAN_DIR}/{filename}"

    content = f"""# AI 日报 - {today}

> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{summary}
"""

    url = f"https://api.github.com/repos/{OBSIDIAN_REPO}/contents/{filepath}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }

    get_resp = requests.get(url, headers=headers)
    if get_resp.status_code == 200:
        sha = get_resp.json()["sha"]
        data = {"message": f"更新 AI 日报 {today}", "content": content, "sha": sha}
    else:
        data = {"message": f"添加 AI 日报 {today}", "content": content}

    resp = requests.put(url, headers=headers, json=data)
    if resp.status_code in [200, 201]:
        print(f"  已保存到 Obsidian: {filename}")
        return filepath
    else:
        print(f"  保存失败: {resp.text}")
        return None
