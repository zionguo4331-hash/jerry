#!/usr/bin/env python3
import asyncio
import json
import re
from playwright.async_api import async_playwright


async def test_network():
    print("🚀 测试网络拦截方案...")
    
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
        captured_responses = []
        
        async def handle_response(response):
            url = response.url
            if any(keyword in url.lower() for keyword in ['item', 'product', 'goods', 'shop', 'search', 'list', 'api']):
                try:
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type or 'javascript' in content_type:
                        try:
                            body = await response.text()
                            if len(body) > 100 and len(body) < 50000:
                                captured_responses.append({
                                    'url': url[:100],
                                    'type': content_type,
                                    'size': len(body),
                                    'has_item': 'item.htm' in body,
                                    'has_detail': 'detail.tmall.com' in body,
                                    'preview': body[:200]
                                })
                        except:
                            pass
                except:
                    pass
        
        page.on("response", handle_response)
        
        print("\n=== 测试：天猫店铺搜索页面 ===")
        search_url = "https://rowongyxm.tmall.com/search.htm"
        print(f"访问: {search_url}")
        
        try:
            await page.goto(search_url, timeout=30000, wait_until='domcontentloaded')
            await asyncio.sleep(8)
            
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)
            
            print(f"\n捕获到 {len(captured_responses)} 个相关响应:")
            for resp in captured_responses:
                print(f"\nURL: {resp['url']}")
                print(f"类型: {resp['type']}")
                print(f"大小: {resp['size']} 字节")
                print(f"包含item.htm: {resp['has_item']}")
                print(f"包含detail.tmall.com: {resp['has_detail']}")
                print(f"预览: {resp['preview'][:100]}...")
                
        except Exception as e:
            print(f"❌ 失败: {e}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_network())
