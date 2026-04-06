#!/usr/bin/env python3
"""
淘宝竞品监控 - 简化方案
不通过CDP，直接启动浏览器访问
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

DATA_DIR = Path("data")
REPORT_DIR = Path("reports")
DATA_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

async def main():
    print("🚀 淘宝竞品监控")
    print("=" * 50)
    print("注意: 如果弹出登录框，请手动登录")
    print("=" * 50)
    
    async with async_playwright() as p:
        # 启动非headless浏览器
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )
        
        page = await context.new_page()
        
        urls = [
            "https://item.taobao.com/item.htm?id=805955198283",
            "https://detail.tmall.com/item.htm?id=805955198283",
        ]
        
        results = []
        
        for url in urls:
            print(f"\n打开: {url}")
            try:
                await page.goto(url, timeout=30000, wait_until="networkidle")
                await asyncio.sleep(3)
                
                title = await page.title()
                print(f"  标题: {title[:50]}...")
                
                # 如果需要登录，提示用户
                if "登录" in title:
                    print("  ⚠️ 需要登录")
                    print("  请在浏览器中手动登录，然后按回车继续...")
                    input()
                    
                    await page.goto(url, timeout=30000)
                    await asyncio.sleep(5)
                    title = await page.title()
                
                # 提取数据
                data = {
                    "url": url,
                    "title": "",
                    "price": "",
                    "sales": "",
                    "shop": "",
                    "timestamp": datetime.now().isoformat()
                }
                
                # 尝试提取
                result = await page.evaluate('''
                    () => {
                        const r = {};
                        const el1 = document.querySelector('#itemTitle');
                        if (el1) r.title = el1.textContent.trim();
                        const el2 = document.querySelector('.price');
                        if (el2) {
                            const m = el2.textContent.match(/[\\d.]+/);
                            if (m) r.price = m[0];
                        }
                        const el3 = document.querySelector('.deal-count');
                        if (el3) {
                            const m = el3.textContent.match(/\\d+/);
                            if (m) r.sales = m[0];
                        }
                        return r;
                    }
                ''')
                
                if result.get('title'):
                    data.update(result)
                    print(f"  ✓ {data['title'][:30]} | ¥{data['price']}")
                    results.append(data)
                else:
                    print(f"  ✗ 未提取到数据")
                    
            except Exception as e:
                print(f"  错误: {e}")
        
        await browser.close()
        
        if results:
            today = datetime.now().strftime("%Y-%m-%d")
            
            data_file = DATA_DIR / f"{today}.json"
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            report = f"# 竞品日报 - {today}\n\n"
            for p in results:
                report += f"## {p['title']}\n"
                report += f"- 价格: ¥{p['price']}\n"
                report += f"- 销量: {p['sales']}\n"
                report += f"- 链接: {p['url']}\n\n"
            
            report_file = REPORT_DIR / f"竞品日报_{today}.md"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            
            print(f"\n✅ 完成!")
            print(f"📊 {data_file}")
            print(f"📄 {report_file}")

if __name__ == "__main__":
    asyncio.run(main())
