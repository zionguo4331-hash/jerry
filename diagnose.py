#!/usr/bin/env python3
"""
淘宝竞品监控工具 - 诊断模式
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

DATA_DIR = Path("data")
REPORT_DIR = Path("reports")

async def diagnose_page(page):
    """诊断页面内容"""
    print(f"\n页面 URL: {page.url}")
    print(f"页面标题: {await page.title()}")
    
    # 获取页面 HTML 长度
    html = await page.content()
    print(f"HTML 长度: {len(html)} 字符")
    
    # 尝试多种选择器
    selectors_to_try = [
        ('#itemTitle', '标题'),
        ('.tb-item-title', '标题-备用'),
        ('h1', 'H1标签'),
        ('.price', '价格'),
        ('#price', '价格-ID'),
        ('.tm-price', '价格-天猫'),
        ('.deal-count', '销量'),
        ('.sale-count', '销量-备用'),
        ('.shop-name', '店铺'),
        ('.shop-title', '店铺-备用'),
        ('#mainPic', '主图'),
        ('.tb-pic-img img', '主图-备用'),
    ]
    
    print("\n选择器检测:")
    for selector, name in selectors_to_try:
        try:
            el = page.locator(selector)
            count = await el.count()
            if count > 0:
                text = await el.first.text_content()
                src = await el.first.get_attribute('src') if 'img' in selector else None
                if text:
                    print(f"  ✓ {name}: {text.strip()[:30]}")
                elif src:
                    print(f"  ✓ {name}: 图片 src={src[:30]}...")
                else:
                    print(f"  ? {name}: 找到但无内容")
            else:
                print(f"  ✗ {name}: 未找到")
        except Exception as e:
            print(f"  ✗ {name}: 错误 {e}")
    
    # 直接用 JS 提取
    print("\nJavaScript 提取测试:")
    try:
        result = await page.evaluate('''
            () => {
                const r = {};
                
                // 尝试多个标题选择器
                const titles = ['#itemTitle', '.tb-item-title', 'h1', '[class*="title"]'];
                for (const s of titles) {
                    const el = document.querySelector(s);
                    if (el && el.textContent) {
                        r.title = el.textContent.trim();
                        break;
                    }
                }
                
                // 价格
                const prices = ['.price', '#price', '.tm-price'];
                for (const s of prices) {
                    const el = document.querySelector(s);
                    if (el && el.textContent) {
                        const match = el.textContent.match(/[\\d.]+/);
                        if (match) { r.price = match[0]; break; }
                    }
                }
                
                // 销量
                const saleses = ['.deal-count', '.sale-count', '.tm-sale-count'];
                for (const s of saleses) {
                    const el = document.querySelector(s);
                    if (el && el.textContent) {
                        const match = el.textContent.match(/\\d+/);
                        if (match) { r.sales = match[0]; break; }
                    }
                }
                
                // 店铺
                const shops = ['.shop-name', '.shop-title'];
                for (const s of shops) {
                    const el = document.querySelector(s);
                    if (el && el.textContent) {
                        r.shop = el.textContent.trim();
                        break;
                    }
                }
                
                // 主图
                const imgs = ['#mainPic', '.tb-pic-img img'];
                for (const s of imgs) {
                    const el = document.querySelector(s);
                    if (el) {
                        r.image = el.src || el.getAttribute('data-src');
                        break;
                    }
                }
                
                return r;
            }
        ''')
        print(f"  结果: {json.dumps(result, ensure_ascii=False)}")
    except Exception as e:
        print(f"  JS错误: {e}")
    
    return page

async def main():
    print("🚀 淘宝竞品监控 - 诊断模式")
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ 已连接 Chrome")
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return
        
        # 获取所有页面
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        pages = context.pages
        
        # 找商品页
        product_pages = [p for p in pages if 'item.htm' in p.url or 'detail.tmall.com' in p.url]
        
        if not product_pages:
            print("\n没有找到商品详情页")
            print("请先在 Chrome 中打开淘宝/天猫商品页")
            return
        
        print(f"\n找到 {len(product_pages)} 个商品页")
        
        for i, page in enumerate(product_pages, 1):
            print(f"\n{'='*50}")
            print(f"商品页 {i}:")
            await diagnose_page(page)

if __name__ == "__main__":
    asyncio.run(main())
