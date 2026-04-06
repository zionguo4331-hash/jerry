import os
import shutil
from datetime import datetime
from pathlib import Path


def save_to_obsidian_local(summary):
    """保存日报到本地 Obsidian 目录"""
    obsidian_dir = "/Users/guoruijie/Documents/知识库/opencode工作区/笔记库/AI日报"
    os.makedirs(obsidian_dir, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"AI日报-{today}.md"
    filepath = os.path.join(obsidian_dir, filename)

    content = f"""# 每日科技与 AI 情报内参 - {today}

> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{summary}
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  已保存到 Obsidian: {filepath}")
    return filepath


def save_to_obsidian(summary, github_token=None):
    """保存到 Obsidian（优先 GitHub 提交，本地备用）"""
    github_token = github_token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    
    if github_token:
        save_to_obsidian_github(summary, github_token)
    else:
        save_to_obsidian_local(summary)
        print("  注意：未配置 GitHub Token，仅保存到本地")


def save_to_obsidian_github(summary, github_token):
    """通过 GitHub API 提交到仓库"""
    import requests
    
    repo = "zionguo4331-hash/jerry"
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"AI日报-{today}.md"
    filepath = f"AI日报/{filename}"
    
    content = f"""# 每日科技与 AI 情报内参 - {today}

> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{summary}
"""
    
    import base64
    import json
    
    url = f"https://api.github.com/repos/{repo}/contents/{filepath}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }
    
    get_resp = requests.get(url, headers=headers)
    if get_resp.status_code == 200:
        sha = get_resp.json()["sha"]
        data = {"message": f"更新 AI 日报 {today}", "content": base64.b64encode(content.encode()).decode(), "sha": sha}
    else:
        data = {"message": f"添加 AI 日报 {today}", "content": base64.b64encode(content.encode()).decode()}
    
    resp = requests.put(url, headers=headers, json=data)
    if resp.status_code in [200, 201]:
        print(f"  已保存到 GitHub: {filename}")
    else:
        print(f"  GitHub 提交失败: {resp.status_code}")
        save_to_obsidian_local(summary)
