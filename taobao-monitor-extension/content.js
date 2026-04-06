// content.js - 调试版本，带详细日志
(function() {
  'use strict';
  
  console.log('===== 竞品监控脚本加载 =====');
  console.log('URL:', location.href);
  console.log('Title:', document.title);
  
  if (window._taobaoMonitorDone) {
    console.log('[竞品监控] 已执行过，跳过');
    return;
  }
  window._taobaoMonitorDone = true;

  // 检测是否商品详情页
  var url = location.href;
  var isProductPage = url.includes('item.htm') || url.includes('detail.tmall.com');
  
  console.log('[竞品监控] 是否商品页:', isProductPage);
  
  if (!isProductPage) {
    console.log('[竞品监控] 非商品详情页，跳过');
    return;
  }

  console.log('[竞品监控] 开始提取，2秒后执行...');

  // 等待2秒确保页面渲染完成
  setTimeout(function() {
    console.log('[竞品监控] 开始提取数据...');
    
    var data = { 
      url: url, 
      title: '', 
      price: '', 
      sales: '', 
      shopName: '', 
      mainImage: '', 
      timestamp: Date.now() 
    };

    // 提取标题 - 尝试多个选择器
    var titleSelectors = ['#itemTitle', '.tb-item-title', 'h1', '.goods-title', '[class*="title"]'];
    for (var i = 0; i < titleSelectors.length; i++) {
      var el = document.querySelector(titleSelectors[i]);
      if (el && el.textContent && el.textContent.trim()) {
        data.title = el.textContent.trim().substring(0, 100);
        console.log('[竞品监控] 找到标题 (' + titleSelectors[i] + '):', data.title);
        break;
      }
    }
    if (!data.title) console.log('[竞品监控] 未找到标题');

    // 提取价格
    var priceSelectors = ['.price', '#price', '.tm-price', '.goods-price', '[class*="price"]'];
    for (var i = 0; i < priceSelectors.length; i++) {
      var el = document.querySelector(priceSelectors[i]);
      if (el && el.textContent) {
        var text = el.textContent.trim();
        var match = text.match(/[\d.]+/);
        if (match) {
          data.price = match[0];
          console.log('[竞品监控] 找到价格 (' + priceSelectors[i] + '):', data.price);
          break;
        }
      }
    }
    if (!data.price) console.log('[竞品监控] 未找到价格');

    // 提取销量
    var salesSelectors = ['.sale-count', '.deal-count', '.tm-sale-count', '.goods-sold', '[class*="sold"]'];
    for (var i = 0; i < salesSelectors.length; i++) {
      var el = document.querySelector(salesSelectors[i]);
      if (el && el.textContent) {
        var text = el.textContent.trim();
        var match = text.match(/\d+/);
        if (match) {
          data.sales = match[0];
          console.log('[竞品监控] 找到销量 (' + salesSelectors[i] + '):', data.sales);
          break;
        }
      }
    }
    if (!data.sales) console.log('[竞品监控] 未找到销量');

    // 提取店铺名
    var shopSelectors = ['.shop-name', '.shop-title', '#shopName', '.seller-nick'];
    for (var i = 0; i < shopSelectors.length; i++) {
      var el = document.querySelector(shopSelectors[i]);
      if (el && el.textContent && el.textContent.trim()) {
        data.shopName = el.textContent.trim().substring(0, 50);
        console.log('[竞品监控] 找到店铺 (' + shopSelectors[i] + '):', data.shopName);
        break;
      }
    }
    if (!data.shopName) {
      // 从页面标题提取
      var title = document.title;
      var parts = title.split('-');
      if (parts.length >= 2 && parts[1]) {
        data.shopName = parts[1].trim();
        console.log('[竞品监控] 从标题提取店铺:', data.shopName);
      }
    }

    // 提取主图
    var imgSelectors = ['#mainPic', '.tb-pic-img img', '.goods-img img', '[class*="mainpic"] img'];
    for (var i = 0; i < imgSelectors.length; i++) {
      var el = document.querySelector(imgSelectors[i]);
      if (el) {
        var src = el.src || el.getAttribute('data-src');
        if (src && !src.includes('loading')) {
          data.mainImage = src;
          console.log('[竞品监控] 找到主图');
          break;
        }
      }
    }

    console.log('[竞品监控] 完整数据:', JSON.stringify(data));

    // 保存数据
    if (data.title || data.price) {
      console.log('[竞品监控] 准备保存...');
      chrome.storage.local.get(['monitor_products'], function(result) {
        var products = result.monitor_products || {};
        products[url] = data;
        chrome.storage.local.set({ monitor_products: products }, function() {
          var count = Object.keys(products).length;
          console.log('[竞品监控] ★ 保存成功! 商品数:', count);
          alert('竞品监控: 已保存 ' + (data.title || '商品') + '，共 ' + count + ' 个商品');
        });
      });
    } else {
      console.log('[竞品监控] ✗ 未提取到有效数据');
      alert('竞品监控: 未提取到数据，请检查页面');
    }
  }, 2000);
})();
