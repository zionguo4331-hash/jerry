import sys
from datetime import datetime

from fetch_x_posts_weekly import fetch_x_posts_weekly
from fetch_github_trending_weekly import fetch_github_trending_weekly
from fetch_producthunt import fetch_producthunt
from generate_weekly_summary import generate_weekly_summary
from send_wechat import send_wechat


def main():
    print(f"=== AI Weekly 开始运行 {datetime.now()} ===")

    print("\n[1/4] 抓取 X 专家一周动态...")
    x_posts = fetch_x_posts_weekly()
    print(f"  获取到 {len(x_posts)} 条内容")

    print("\n[2/4] 抓取 GitHub Trending 周榜...")
    github_trending = fetch_github_trending_weekly()
    print(f"  获取到 {len(github_trending)} 个项目")

    print("\n[3/4] 抓取 Product Hunt...")
    producthunt = fetch_producthunt()
    print(f"  获取到 {len(producthunt)} 个产品")

    print("\n[4/4] 生成周报摘要并推送...")
    summary = generate_weekly_summary(x_posts, github_trending, producthunt)

    now = datetime.now()
    week_start = now - __import__('datetime').timedelta(days=7)
    title = f"AI 周报 - {week_start.strftime('%m.%d')}~{now.strftime('%m.%d')}"
    send_wechat(title, summary)

    print(f"\n=== AI Weekly 完成 {datetime.now()} ===")
    return summary


if __name__ == "__main__":
    main()
