// Background: simple report generation and export for Obsidian
const MONITOR_KEY = 'monitor_products';
const FILENAME_PREFIX = '竞品日报_';

function formatDateKey() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

async function generateReport() {
  const res = await chrome.storage.local.get([MONITOR_KEY]);
  const data = res[MONITOR_KEY] || {};
  const products = Object.values(data);
  const today = formatDateKey();
  let report = `# 竞品日报 - ${today}\n\n`;
  if (products.length > 0) {
    report += `## 今日监控商品 (${products.length})\n\n`;
    products.forEach(p => {
      report += `### ${p.title || '未知商品'}\n`;
      report += `- 链接: ${p.url}\n`;
      report += `- 价格: ${p.price || '未知'}\n`;
      report += `- 月销量: ${p.sales || '未知'}\n`;
      report += `- 店铺: ${p.shopName || '未知'}\n`;
      report += `- 主图: ${p.mainImage || ''}\n\n`;
    });
  } else {
    report += `## 今日无变动\n`;
  }
  // 简单最近历史占位（未来可扩展）
  // 落盘路径设置为 Obsidian Vault 子目录，确保落盘后可直接导入 Obsidian。
  // 注意：下载时请确保浏览器默认下载目录指向 Obsidian Vault 的根目录，
  // 或在此处使用子目录。这里使用子目录 'obsidian' 作为示例。
  return { report, filename: `obsidian/竞品日报_${today}.md` };
}

async function exportMd() {
  const r = await generateReport();
  const blob = new Blob([r.report], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  chrome.downloads.download({ url: url, filename: r.filename, saveAs: false });
}

function handleExtractedData(data) {
  // This handler is kept for compatibility; actual storage is managed by content.js
  // We simply acknowledge receipt.
  console.log('[竞品监控-BG] Received data payload for reporting', data ? Object.keys(data).length : 0);
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'getReport') {
    generateReport().then(r => sendResponse(r));
    return true;
  }
  if (message.action === 'exportMd') {
    exportMd().then(() => sendResponse({ status: 'ok', filename: '竞品日报.md' }));
    return true;
  }
  if (message.action === 'exportData') {
    // Simple JSON export of monitor data
    chrome.storage.local.get([MONITOR_KEY], result => {
      const data = result[MONITOR_KEY] || {};
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      chrome.downloads.download({ url: url, filename: `竞品数据_${formatDateKey()}.json`, saveAs: true });
      sendResponse({ status: 'ok' });
    });
    return true;
  }
  if (message.action === 'clearData') {
    chrome.storage.local.remove([MONITOR_KEY], () => sendResponse({ status: 'ok' }));
    return true;
  }
  return true;
});
