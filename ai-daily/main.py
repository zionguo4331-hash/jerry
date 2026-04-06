import sys
from datetime import datetime

from fetch_x_posts import fetch_x_posts
from fetch_github_trending import fetch_github_trending
from fetch_producthunt import fetch_producthunt
from generate_summary import generate_summary
from send_wechat import send_wechat
from save_obsidian import save_to_obsidian


def main():
    print(f"=== AI Daily 开始运行 {datetime.now()} ===")

    print("\n[1/4] 抓取 X 专家动态...")
    x_posts = fetch_x_posts()
    print(f"  获取到 {len(x_posts)} 条推文")

    print("\n[2/4] 抓取 GitHub Trending...")
    github_trending = fetch_github_trending()
    print(f"  获取到 {len(github_trending)} 个项目")

    print("\n[3/4] 抓取 Product Hunt...")
    producthunt = fetch_producthunt()
    print(f"  获取到 {len(producthunt)} 个产品")

    print("\n[4/4] 生成摘要并推送...")
    summary = generate_summary(x_posts, github_trending, producthunt)

    title = f"AI 日报 - {datetime.now().strftime('%Y-%m-%d')}"
    send_wechat(title, summary)

    print("\n[5/5] 保存到 Obsidian...")
    save_to_obsidian(summary)

    print(f"\n=== AI Daily 完成 {datetime.now()} ===")
    return summary


if __name__ == "__main__":
    main()
