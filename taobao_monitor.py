#!/usr/bin/env python3
import asyncio
import json
import random
import time
import os
import re
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, Playwright


DATA_DIR = Path("data")
REPORT_DIR = Path("reports")
DATA_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)


def load_last_data():
    data_files = sorted(DATA_DIR.glob("*.json"), reverse=True)
    if data_files:
        with open(data_files[0], encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_current_data(data):
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = DATA_DIR / f"{today}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_report(current_data, last_data):
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORT_DIR / f"竞品动态日报_{today}.md"
    
    changes = []
    for shop_name, products in current_data.items():
        if shop_name not in last_data:
            changes.append(f"## 🆕 {shop_name} (新增店铺)")
            for p in products:
                changes.append(f"- {p['title'][:50]} | {p['price']} | {p.get('sales', 'N/A')}")
            continue
        
        last_products = {p["url"]: p for p in last_data[shop_name]}
        current_products = {p["url"]: p for p in products}
        
        all_urls = set(last_products.keys()) | set(current_products.keys())
        
        for url in all_urls:
            p = current_products.get(url)
            old = last_products.get(url)
            
            if not old:
                changes.append(f"## 🆕 {shop_name} - 新增商品")
                changes.append(f"- {p['title'][:50]} | {p['price']} | {p.get('sales', 'N/A')}")
            elif not p:
                changes.append(f"## ❌ {shop_name} - 下架商品")
                changes.append(f"- {old['title'][:50]}")
            else:
                price_changed = old.get("price") != p.get("price")
                img_changed = old.get("main_image") != p.get("main_image")
                
                if price_changed or img_changed:
                    changes.append(f"## 🔄 {shop_name}")
                    changes.append(f"- **{p['title'][:40]}**")
                    if price_changed:
                        changes.append(f"  - 💰 {old.get('price')} → {p.get('price')}")
                    if img_changed:
                        changes.append(f"  - 🖼️ 主图变动")
    
    if not changes:
        report_content = f"# 竞品动态日报 - {today}\n\n✅ 今日无变动"
    else:
        report_content = f"# 竞品动态日报 - {today}\n\n" + "\n".join(changes)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    return report_path


async def random_scroll(page):
    for _ in range(random.randint(2, 4)):
        await page.evaluate(f"window.scrollBy(0, {random.randint(300, 800)})")
        await asyncio.sleep(random.uniform(0.5, 1.5))


async def check_captcha(page):
    try:
        captcha = page.locator('iframe[src*="captcha"]')
        if await captcha.count() > 0:
            return True
        captcha_div = page.locator('.nc_wrapper, #nc_1_n1z, .tcaptcha-drag-area')
        if await captcha_div.count() > 0:
            return True
    except:
        pass
    return False


async def extract_product_info(page):
    info = {}
    
    try:
        price_elem = page.locator('.price-value, .price, #price, .tm-price, .tb-rmb-num, .Price--priceWrap--nKQ6VYV')
        if await price_elem.count() > 0:
            info['price'] = await price_elem.first.inner_text()
    except:
        pass
    
    try:
        sales_elem = page.locator('.sale-count, .deal-count, #dealCount, .tm-sale-count, .ItemCounter--counterWrap--qZqZqZ, .tb-sold-count')
        if await sales_elem.count() > 0:
            info['sales'] = await sales_elem.first.inner_text()
    except:
        pass
    
    try:
        img_elem = page.locator('#mainPic, .tb-pic-img, .main-image img, .Magnifier--magnifierRoot--qZqZqZ img')
        if await img_elem.count() > 0:
            info['main_image'] = await img_elem.first.get_attribute('src')
    except:
        pass
    
    try:
        title_elem = page.locator('.tb-item-title, #itemTitle, h1, .ItemHeader--title--qZqZqZ')
        if await title_elem.count() > 0:
            info['title'] = await title_elem.first.inner_text()
    except:
        pass
    
    try:
        reviews = []
        review_elem = page.locator('.reviews-list .item, .J_KgVRate_List .kg-rate-list-item, .Rate--rateContent--qZqZqZ .Rate--item--qZqZqZ')
        count = await review_elem.count()
        for i in range(min(count, 5)):
            text = await review_elem.nth(i).inner_text()
            reviews.append(text.strip())
        if reviews:
            info['reviews'] = reviews
    except:
        pass
    
    try:
        questions = []
        q_elem = page.locator('.question-list .question-item, .qna-list .item, .AskAnswer--askList--qZqZqZ .AskAnswer--item--qZqZqZ')
        count = await q_elem.count()
        for i in range(min(count, 5)):
            text = await q_elem.nth(i).inner_text()
            questions.append(text.strip())
        if questions:
            info['questions'] = questions
    except:
        pass
    
    return info


async def get_shop_name(page):
    try:
        title = await page.title()
        if title:
            parts = title.split('-')
            if len(parts) >= 2:
                shop_name = parts[1].strip()
                if shop_name and shop_name != '首页':
                    return shop_name
            return parts[0].strip() if parts else "未知店铺"
    except:
        pass
    return "未知店铺"


async def extract_product_links_from_shop(page):
    product_urls = []
    shop_url = page.url
    captured_urls = []
    
    async def handle_response(response):
        try:
            url = response.url
            if any(keyword in url for keyword in ['list.htm', 'search.htm', 'itemlist', 'shoplist', 'query', 'api']):
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type or 'application/json' in content_type:
                    try:
                        body = await response.text()
                        if 'item.htm' in body or 'detail.tmall.com' in body:
                            found = re.findall(r'href=["\']?(https?://[^"\' >]*item\.htm[^"\' >]*)', body)
                            found += re.findall(r'href=["\']?(https?://[^"\' >]*detail\.tmall\.com[^"\' >]*)', body)
                            found += re.findall(r'"url"\s*:\s*"(https?://[^"]*item\.htm[^"]*)"', body)
                            found += re.findall(r'"url"\s*:\s*"(https?://[^"]*detail\.tmall\.com[^"]*)"', body)
                            for f in found:
                                if f not in captured_urls:
                                    captured_urls.append(f)
                    except:
                        pass
        except:
            pass
    
    page.on("response", handle_response)
    
    await random_scroll(page)
    await asyncio.sleep(3)
    
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(2)
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(2)
    
    all_links = await page.evaluate("""() => {
        const links = Array.from(document.querySelectorAll('a[href*="item.htm"], a[href*="detail.tmall.com"]'));
        return links.map(a => a.href);
    }""")
    for link in all_links:
        if link not in product_urls:
            product_urls.append(link)
    
    if captured_urls:
        product_urls.extend(captured_urls)
        print(f"   通过 API 拦截找到 {len(captured_urls)} 个链接")
    
    if len(product_urls) >= 5:
        print(f"   通过 JS 评估找到 {len(product_urls)} 个链接")
        return list(set(product_urls))[:20]
    
    frames = page.frames
    print(f"   页面有 {len(frames)} 个 frame")
    for frame in frames:
        try:
            frame_url = frame.url
            print(f"   Frame: {frame_url[:80]}")
            if 'shop' in frame_url.lower() or 'search' in frame_url.lower() or 'list' in frame_url.lower():
                frame_links = await frame.evaluate("""() => {
                    const links = Array.from(document.querySelectorAll('a[href*="item.htm"], a[href*="detail.tmall.com"]'));
                    return links.map(a => a.href);
                }""")
                for link in frame_links:
                    if link not in product_urls:
                        product_urls.append(link)
                if len(product_urls) > 5:
                    break
        except Exception as e:
            print(f"     -> 错误: {e}")
    
    if len(product_urls) < 5:
        html = await page.content()
        item_links = re.findall(r'href="([^"]*item\.htm[^"]*)"', html)
        detail_links = re.findall(r'href="([^"]*detail\.tmall\.com[^"]*)"', html)
        for link in item_links + detail_links:
            if link not in product_urls:
                product_urls.append(link)
        print(f"   通过正则找到 {len(product_urls)} 个链接")
    
    if len(product_urls) < 5:
        print("   尝试访问'所有商品'页面...")
        search_urls = []
        
        if 'tmall.com' in shop_url:
            shop_id_match = re.search(r'shop/(\d+)', shop_url)
            if shop_id_match:
                shop_id = shop_id_match.group(1)
                search_urls = [
                    f"https://{shop_url.split('/')[2]}/search.htm",
                    f"https://{shop_url.split('/')[2]}/list.htm",
                ]
        elif 'taobao.com' in shop_url:
            shop_id_match = re.search(r'shop(\d+)', shop_url)
            if shop_id_match:
                shop_id = shop_id_match.group(1)
                search_urls = [
                    f"https://shop{shop_id}.taobao.com/search.htm",
                    f"https://shop{shop_id}.taobao.com/list.htm",
                ]
        
        for search_url in search_urls:
            try:
                print(f"   尝试: {search_url}")
                await page.goto(search_url, timeout=15000)
                await asyncio.sleep(5)
                await random_scroll(page)
                await asyncio.sleep(3)
                
                js_links = await page.evaluate("""() => {
                    const links = Array.from(document.querySelectorAll('a[href*="item.htm"], a[href*="detail.tmall.com"]'));
                    return links.map(a => a.href);
                }""")
                for link in js_links:
                    if link not in product_urls:
                        product_urls.append(link)
                
                html = await page.content()
                print(f"   搜索页面长度: {len(html)} 字符")
                
                item_links = re.findall(r'href="(https?://[^"]*item\.htm[^"]*)"', html)
                detail_links = re.findall(r'href="(https?://[^"]*detail\.tmall\.com[^"]*)"', html)
                for link in item_links + detail_links:
                    if link not in product_urls:
                        product_urls.append(link)
                
                if len(product_urls) >= 5:
                    print(f"   成功找到 {len(product_urls)} 个链接")
                    break
            except Exception as e:
                print(f"   搜索页面失败: {e}")
                continue
    
    if len(product_urls) < 5 and captured_urls:
        product_urls.extend(captured_urls)
    
    return list(set(product_urls))[:20]
    
    frames = page.frames
    print(f"   页面有 {len(frames)} 个 frame")
    for frame in frames:
        try:
            frame_url = frame.url
            print(f"   Frame: {frame_url[:80]}")
            if 'shop' in frame_url.lower() or 'search' in frame_url.lower() or 'list' in frame_url.lower():
                links = frame.locator('a[href*="item.htm"]')
                count = await links.count()
                print(f"     -> 找到 {count} 个商品链接")
                for i in range(count):
                    href = await links.nth(i).get_attribute('href')
                    if href and href not in product_urls:
                        product_urls.append(href)
                if len(product_urls) > 5:
                    break
        except Exception as e:
            print(f"     -> 错误: {e}")
    
    if len(product_urls) < 5:
        html = await page.content()
        item_links = re.findall(r'href="([^"]*item\.htm[^"]*)"', html)
        detail_links = re.findall(r'href="([^"]*detail\.tmall\.com[^"]*)"', html)
        for link in item_links + detail_links:
            if link not in product_urls:
                product_urls.append(link)
        print(f"   通过正则找到 {len(product_urls)} 个链接")
    
    if len(product_urls) < 5:
        print("   尝试访问'所有商品'页面...")
        search_urls = []
        
        if 'tmall.com' in shop_url:
            shop_id_match = re.search(r'shop/(\d+)', shop_url)
            if shop_id_match:
                shop_id = shop_id_match.group(1)
                search_urls = [
                    f"https://{shop_url.split('/')[2]}/search.htm",
                    f"https://{shop_url.split('/')[2]}/list.htm",
                ]
        elif 'taobao.com' in shop_url:
            shop_id_match = re.search(r'shop(\d+)', shop_url)
            if shop_id_match:
                shop_id = shop_id_match.group(1)
                search_urls = [
                    f"https://shop{shop_id}.taobao.com/search.htm",
                    f"https://shop{shop_id}.taobao.com/list.htm",
                ]
        
        for search_url in search_urls:
            try:
                print(f"   尝试: {search_url}")
                await page.goto(search_url, timeout=15000)
                await asyncio.sleep(5)
                await random_scroll(page)
                await asyncio.sleep(3)
                
                html = await page.content()
                print(f"   搜索页面长度: {len(html)} 字符")
                
                item_links = re.findall(r'href="(https?://[^"]*item\.htm[^"]*)"', html)
                detail_links = re.findall(r'href="(https?://[^"]*detail\.tmall\.com[^"]*)"', html)
                for link in item_links + detail_links:
                    if link not in product_urls:
                        product_urls.append(link)
                
                if len(product_urls) >= 5:
                    print(f"   成功找到 {len(product_urls)} 个链接")
                    break
            except Exception as e:
                print(f"   搜索页面失败: {e}")
                continue
    
    if len(product_urls) < 5 and captured_urls:
        product_urls.extend(captured_urls)
    
    return list(set(product_urls))[:20]


async def crawl_shop(shop_url, browser, context):
    results = []
    shop_name = "未知店铺"
    
    page = await context.new_page()
    
    try:
        try:
            await page.goto(shop_url, timeout=30000, wait_until='networkidle')
        except:
            await page.goto(shop_url, timeout=30000, wait_until='domcontentloaded')
        await page.wait_for_load_state('domcontentloaded')
        await asyncio.sleep(random.uniform(5, 8))
        
        if await check_captcha(page):
            print(f"⚠️ 检测到验证码，请手动完成滑动后按回车继续...")
            input()
        
        shop_name = await get_shop_name(page)
        current_url = page.url
        print(f"🏪 抓取店铺: {shop_name}")
        print(f"   当前URL: {current_url}")
        
        title = await page.title()
        print(f"   页面标题: {title}")
        
        product_links = await extract_product_links_from_shop(page)
        print(f"   找到 {len(product_links)} 个商品链接")
        
        for idx, product_url in enumerate(product_links):
            try:
                await page.goto(product_url, timeout=30000)
                await random_scroll(page)
                await asyncio.sleep(random.uniform(1, 3))
                
                if await check_captcha(page):
                    print(f"⚠️ 检测到验证码，请手动完成滑动后按回车继续...")
                    input()
                
                info = await extract_product_info(page)
                info['url'] = product_url
                
                if not info.get('title'):
                    info['title'] = f"商品{idx+1}"
                
                results.append(info)
                print(f"   [{idx+1}/{len(product_links)}] {info.get('title', '')[:30]}")
                
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"   ❌ 商品 {idx+1} 失败: {e}")
                continue
        
    except Exception as e:
        print(f"❌ 店铺抓取失败: {e}")
    
    await page.close()
    return shop_name, results


async def main(shop_urls):
    print("🚀 启动浏览器连接...")
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            print(f"❌ 无法连接 Chrome: {e}")
            print("请确保 Chrome 已开启调试端口: --remote-debugging-port=9222")
            return
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        all_data = {}
        
        for shop_url in shop_urls:
            print(f"\n{'='*50}")
            print(f"开始抓取: {shop_url}")
            
            shop_name, products = await crawl_shop(shop_url, browser, context)
            all_data[shop_name] = products
            
            delay = random.uniform(5, 10)
            print(f"⏳ 等待 {delay:.1f} 秒后继续...")
            await asyncio.sleep(delay)
        
        await browser.close()
    
    save_current_data(all_data)
    
    print(f"\n{'='*50}")
    print("📊 对比历史数据...")
    
    last_data = load_last_data()
    report_path = generate_report(all_data, last_data)
    
    print(f"✅ 报告生成: {report_path}")
    
    with open(report_path, encoding="utf-8") as f:
        print("\n" + "="*50)
        print(f.read())


if __name__ == "__main__":
    urls = """https://rowongyxm.tmall.com/shop/view_shop.htm?spm=a21n57.shop_search.0.0.154956c3LAW6qD
https://fukecryp.tmall.com/shop/view_shop.htm?spm=a21n57.shop_search.0.0.154956c3LAW6qD
https://jiyubuluo.tmall.com/shop/view_shop.htm?spm=a21n57.shop_search.0.0.154956c3LAW6qD
https://shop388597254.taobao.com/?spm=a21n57.shop_search.0.0.154956c3LAW6qD
https://shop382568351.taobao.com/?spm=a21n57.shop_search.0.0.154956c3LAW6qD"""
    
    url_list = [u.strip() for u in urls.replace(",", " ").split() if u.strip()]
    
    print(f"\n准备抓取 {len(url_list)} 个店铺")
    asyncio.run(main(url_list))
