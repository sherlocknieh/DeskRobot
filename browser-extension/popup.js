// Popup脚本 - 处理弹出界面逻辑

document.addEventListener('DOMContentLoaded', function() {
    loadSearchEngines();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    document.getElementById('settings-btn').addEventListener('click', function() {
        chrome.runtime.openOptionsPage();
        window.close();
    });
    
    document.getElementById('help-btn').addEventListener('click', function() {
        showHelp();
    });
}

// 加载搜索引擎列表
async function loadSearchEngines() {
    try {
        const result = await chrome.storage.sync.get(['searchEngines']);
        const searchEngines = result.searchEngines || [];
        
        const engineList = document.getElementById('engine-list');
        engineList.innerHTML = '';
        
        if (searchEngines.length === 0) {
            engineList.innerHTML = '<div class="engine-item"><span>暂无搜索引擎</span></div>';
            return;
        }
        
        searchEngines.forEach(engine => {
            const engineItem = document.createElement('div');
            engineItem.className = 'engine-item';
            
            engineItem.innerHTML = `
                <span>${engine.name}</span>
                <span class="status ${engine.enabled ? 'enabled' : 'disabled'}">
                    ${engine.enabled ? '已启用' : '已禁用'}
                </span>
            `;
            
            engineList.appendChild(engineItem);
        });
        
    } catch (error) {
        console.error('加载搜索引擎失败:', error);
        document.getElementById('engine-list').innerHTML = 
            '<div class="engine-item"><span>加载失败</span></div>';
    }
}

// 显示帮助信息
function showHelp() {
    const helpWindow = window.open('', '_blank', 'width=500,height=600');
    helpWindow.document.write(`
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>使用帮助</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    padding: 20px; 
                    line-height: 1.6;
                    max-width: 600px;
                    margin: 0 auto;
                }
                h1, h2 { color: #333; }
                h1 { border-bottom: 2px solid #007bff; padding-bottom: 10px; }
                .feature { 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin: 15px 0; 
                }
                .step { 
                    background: #e7f3ff; 
                    padding: 10px; 
                    border-left: 4px solid #007bff; 
                    margin: 10px 0; 
                }
                code { 
                    background: #f1f1f1; 
                    padding: 2px 4px; 
                    border-radius: 3px; 
                }
            </style>
        </head>
        <body>
            <h1>图片搜索与二维码解析器 - 使用帮助</h1>
            
            <div class="feature">
                <h2>🔍 图片搜索功能</h2>
                <div class="step">
                    <strong>步骤1:</strong> 在任何网页上找到您想搜索的图片
                </div>
                <div class="step">
                    <strong>步骤2:</strong> 右键点击图片
                </div>
                <div class="step">
                    <strong>步骤3:</strong> 选择"搜索图片" → 选择搜索引擎
                </div>
                <div class="step">
                    <strong>结果:</strong> 新标签页中打开相应的搜索结果
                </div>
            </div>
            
            <div class="feature">
                <h2>📱 二维码解析功能</h2>
                <div class="step">
                    <strong>步骤1:</strong> 在网页上找到包含二维码的图片
                </div>
                <div class="step">
                    <strong>步骤2:</strong> 右键点击图片
                </div>
                <div class="step">
                    <strong>步骤3:</strong> 选择"解析二维码"
                </div>
                <div class="step">
                    <strong>结果:</strong> 页面右上角显示解析结果，支持复制和链接跳转
                </div>
            </div>
            
            <div class="feature">
                <h2>⚙️ 搜索引擎管理</h2>
                <div class="step">
                    <strong>默认引擎:</strong> Google、百度、Yandex、TinEye
                </div>
                <div class="step">
                    <strong>自定义:</strong> 点击"搜索引擎设置"可添加、编辑、删除搜索引擎
                </div>
                <div class="step">
                    <strong>URL格式:</strong> 在搜索URL末尾加上图片地址参数，如：<br>
                    <code>https://www.google.com/searchbyimage?image_url=</code>
                </div>
            </div>
            
            <div class="feature">
                <h2>🛠️ 技术说明</h2>
                <p><strong>兼容性:</strong> 支持Chrome、Edge等基于Chromium的浏览器</p>
                <p><strong>权限:</strong> 仅需要右键菜单和存储权限，不收集用户数据</p>
                <p><strong>隐私:</strong> 图片搜索通过跳转到第三方网站进行，本扩展不存储图片</p>
            </div>
        </body>
        </html>
    `);
    helpWindow.document.close();
}