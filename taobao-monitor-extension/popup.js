// popup.js
function load() {
  chrome.storage.local.get(['monitor_products'], function(result) {
    var products = result.monitor_products || {};
    var list = document.getElementById('list');
    var count = document.getElementById('count');
    
    var arr = Object.values(products);
    count.textContent = arr.length;
    
    if (arr.length === 0) {
      list.innerHTML = '<div class="empty">暂无数据<br>请浏览商品详情页</div>';
      return;
    }
    
    var html = '';
    arr.slice(-10).reverse().forEach(function(p) {
      html += '<div class="list-item">' + (p.title || '未知').substring(0, 20) + '<br>' + (p.price || '?') + ' - ' + (p.sales || '?') + '</div>';
    });
    list.innerHTML = html;
  });
}

function exportMd() {
  console.log('[竞品监控-弹出窗] 开始导出MD...');
  
  chrome.storage.local.get(['monitor_products'], function(result) {
    var products = result.monitor_products || {};
    var today = new Date().toISOString().split('T')[0];
    var count = Object.keys(products).length;
    
    console.log('[竞品监控-弹出窗] 商品数量:', count);
    
    if (count === 0) {
      alert('暂无数据，请先浏览商品详情页');
      return;
    }
    
    var report = '# 竞品日报 - ' + today + '\n\n';
    report += '## 今日监控商品 (' + count + ')\n\n';
    
    Object.values(products).forEach(function(p) {
      report += '### ' + (p.title || '未知商品') + '\n';
      report += '- 链接: ' + p.url + '\n';
      report += '- 价格: ' + (p.price || '未知') + '\n';
      report += '- 月销量: ' + (p.sales || '未知') + '\n';
      report += '- 店铺: ' + (p.shopName || '未知') + '\n';
      if (p.mainImage) {
        report += '- 主图: ' + p.mainImage + '\n';
      }
      report += '\n';
    });
    
    console.log('[竞品监控-弹出窗] 报告内容长度:', report.length);
    
    var blob = new Blob([report], {type: 'text/markdown;charset=utf-8'});
    var url = URL.createObjectURL(blob);
    
    chrome.downloads.download({
      url: url, 
      filename: '竞品日报_' + today + '.md', 
      saveAs: false
    }, function(downloadId) {
      if (chrome.runtime.lastError) {
        console.error('[竞品监控-弹出窗] 下载失败:', chrome.runtime.lastError.message);
        alert('导出失败: ' + chrome.runtime.lastError.message);
      } else {
        console.log('[竞品监控-弹出窗] 下载成功, ID:', downloadId);
        alert('已导出到默认下载目录');
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', function() {
  load();
  document.getElementById('refreshBtn').addEventListener('click', load);
  document.getElementById('exportBtn').addEventListener('click', exportMd);
});
