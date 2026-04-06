#!/usr/bin/env python3
import asyncio
import random
from playwright.async_api import async_playwright


async def test_search():
    print("🚀 测试搜索方案...")
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            print(f"❌ 无法连接 Chrome: {e}")
            return
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        
        page = await context.new_page()
        
        # 测试1：天猫店铺搜索页面
        print("\n=== 测试1：天猫店铺搜索页面 ===")
        search_url = "https://rowongyxm.tmall.com/search.htm"
        print(f"访问: {search_url}")
        
        try:
            await page.goto(search_url, timeout=30000, wait_until='domcontentloaded')
            await asyncio.sleep(5)
            
            # 滚动
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # 提取链接
            links = await page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a[href*="item.htm"], a[href*="detail.tmall.com"]'));
                return links.map(a => a.href);
            }""")
            
            print(f"找到 {len(links)} 个商品链接:")
            for link in links[:5]:
                print(f"  - {link}")
                
        except Exception as e:
            print(f"❌ 失败: {e}")
        
        # 测试2：淘宝店铺搜索页面
        print("\n=== 测试2：淘宝店铺搜索页面 ===")
        search_url2 = "https://shop388597254.taobao.com/search.htm"
        print(f"访问: {search_url2}")
        
        try:
            await page.goto(search_url2, timeout=30000, wait_until='domcontentloaded')
            await asyncio.sleep(5)
            
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            links2 = await page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a[href*="item.htm"]'));
                return links.map(a => a.href);
            }""")
            
            print(f"找到 {len(links2)} 个商品链接:")
            for link in links2[:5]:
                print(f"  - {link}")
                
        except Exception as e:
            print(f"❌ 失败: {e}")
        
        # 测试3：淘宝全局搜索
        print("\n=== 测试3：淘宝全局搜索 ===")
        search_url3 = "https://s.taobao.com/search?q=肉王云小妹专卖店"
        print(f"访问: {search_url3}")
        
        try:
            await page.goto(search_url3, timeout=30000, wait_until='domcontentloaded')
            await asyncio.sleep(5)
            
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            links3 = await page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a[href*="item.htm"], a[href*="detail.tmall.com"]'));
                return links.map(a => a.href);
            }""")
            
            print(f"找到 {len(links3)} 个商品链接:")
            for link in links3[:5]:
                print(f"  - {link}")
                
        except Exception as e:
            print(f"❌ 失败: {e}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_search())
