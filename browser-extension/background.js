// 背景脚本 - 处理右键菜单和搜索引擎
chrome.runtime.onInstalled.addListener(() => {
  // 初始化默认搜索引擎
  initializeDefaultSearchEngines();
  
  // 创建右键菜单
  createContextMenus();
});

// 初始化默认搜索引擎
async function initializeDefaultSearchEngines() {
  const result = await chrome.storage.sync.get(['searchEngines']);
  if (!result.searchEngines) {
    const defaultEngines = [
      {
        id: 'google',
        name: 'Google 图片搜索',
        url: 'https://www.google.com/searchbyimage?image_url=',
        enabled: true
      },
      {
        id: 'baidu',
        name: '百度识图',
        url: 'https://graph.baidu.com/s?sign=&rt=upload&rn=10&ct=1&tn=baiduimage&objurl=',
        enabled: true
      },
      {
        id: 'yandex',
        name: 'Yandex 图片搜索',
        url: 'https://yandex.com/images/search?rpt=imageview&url=',
        enabled: true
      },
      {
        id: 'tineye',
        name: 'TinEye 反向搜索',
        url: 'https://www.tineye.com/search?url=',
        enabled: true
      }
    ];
    await chrome.storage.sync.set({ searchEngines: defaultEngines });
  }
}

// 创建右键菜单
async function createContextMenus() {
  // 清除现有菜单
  chrome.contextMenus.removeAll();
  
  // 获取启用的搜索引擎
  const result = await chrome.storage.sync.get(['searchEngines']);
  const searchEngines = result.searchEngines || [];
  
  // 创建图片搜索菜单
  chrome.contextMenus.create({
    id: 'imageSearch',
    title: '搜索图片',
    contexts: ['image']
  });
  
  // 为每个启用的搜索引擎创建子菜单
  searchEngines.filter(engine => engine.enabled).forEach(engine => {
    chrome.contextMenus.create({
      id: `search_${engine.id}`,
      parentId: 'imageSearch',
      title: engine.name,
      contexts: ['image']
    });
  });
  
  // 创建二维码解析菜单
  chrome.contextMenus.create({
    id: 'qrCode',
    title: '解析二维码',
    contexts: ['image']
  });
  
  // 创建分隔符
  chrome.contextMenus.create({
    id: 'separator',
    type: 'separator',
    contexts: ['image']
  });
  
  // 创建设置菜单
  chrome.contextMenus.create({
    id: 'settings',
    title: '搜索引擎设置',
    contexts: ['image']
  });
}

// 处理右键菜单点击
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'qrCode') {
    // 解析二维码
    parseQRCode(info.srcUrl, tab.id);
  } else if (info.menuItemId === 'settings') {
    // 打开设置页面
    chrome.runtime.openOptionsPage();
  } else if (info.menuItemId.startsWith('search_')) {
    // 搜索图片
    const engineId = info.menuItemId.replace('search_', '');
    searchImage(engineId, info.srcUrl);
  }
});

// 搜索图片
async function searchImage(engineId, imageUrl) {
  const result = await chrome.storage.sync.get(['searchEngines']);
  const searchEngines = result.searchEngines || [];
  const engine = searchEngines.find(e => e.id === engineId);
  
  if (engine) {
    const searchUrl = engine.url + encodeURIComponent(imageUrl);
    chrome.tabs.create({ url: searchUrl });
  }
}

// 解析二维码
async function parseQRCode(imageUrl, tabId) {
  // 向内容脚本发送消息解析二维码
  try {
    const response = await chrome.tabs.sendMessage(tabId, {
      action: 'parseQRCode',
      imageUrl: imageUrl
    });
    
    if (response && response.success) {
      // 显示解析结果
      showQRResult(response.data, tabId);
    } else {
      showQRResult('未能检测到二维码', tabId);
    }
  } catch (error) {
    console.error('QR码解析失败:', error);
    showQRResult('二维码解析失败', tabId);
  }
}

// 显示二维码解析结果
function showQRResult(data, tabId) {
  chrome.tabs.sendMessage(tabId, {
    action: 'showQRResult',
    data: data
  });
}

// 监听存储变化，更新菜单
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'sync' && changes.searchEngines) {
    createContextMenus();
  }
});