// Options页面脚本 - 管理搜索引擎设置

document.addEventListener('DOMContentLoaded', function() {
    loadSearchEngines();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    document.getElementById('add-engine-form').addEventListener('submit', handleAddEngine);
}

// 加载搜索引擎列表
async function loadSearchEngines() {
    try {
        const result = await chrome.storage.sync.get(['searchEngines']);
        const searchEngines = result.searchEngines || [];
        
        const engineList = document.getElementById('engine-list');
        engineList.innerHTML = '';
        
        if (searchEngines.length === 0) {
            engineList.innerHTML = `
                <div class="engine-item">
                    <div class="engine-info">
                        <div class="engine-name">暂无搜索引擎</div>
                        <div class="engine-url">点击下方模板按钮快速添加</div>
                    </div>
                </div>
            `;
            return;
        }
        
        searchEngines.forEach((engine, index) => {
            const engineItem = createEngineItem(engine, index);
            engineList.appendChild(engineItem);
        });
        
    } catch (error) {
        console.error('加载搜索引擎失败:', error);
        showMessage('加载搜索引擎失败', 'error');
    }
}

// 创建搜索引擎项
function createEngineItem(engine, index) {
    const engineItem = document.createElement('div');
    engineItem.className = 'engine-item';
    
    engineItem.innerHTML = `
        <label class="toggle-switch">
            <input type="checkbox" ${engine.enabled ? 'checked' : ''} 
                   onchange="toggleEngine(${index})">
            <span class="slider"></span>
        </label>
        <div class="engine-info">
            <div class="engine-name">${escapeHtml(engine.name)}</div>
            <div class="engine-url">${escapeHtml(engine.url)}</div>
        </div>
        <div class="engine-actions">
            <button class="btn btn-primary btn-small" onclick="editEngine(${index})">编辑</button>
            <button class="btn btn-danger btn-small" onclick="deleteEngine(${index})">删除</button>
        </div>
    `;
    
    return engineItem;
}

// HTML转义
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// 处理添加搜索引擎表单
async function handleAddEngine(event) {
    event.preventDefault();
    
    const name = document.getElementById('engine-name').value.trim();
    const url = document.getElementById('engine-url').value.trim();
    
    if (!name || !url) {
        showMessage('请填写完整的搜索引擎信息', 'error');
        return;
    }
    
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        showMessage('搜索URL必须以http://或https://开头', 'error');
        return;
    }
    
    try {
        const result = await chrome.storage.sync.get(['searchEngines']);
        const searchEngines = result.searchEngines || [];
        
        // 检查是否已存在相同名称或URL
        const existingName = searchEngines.find(engine => engine.name === name);
        const existingUrl = searchEngines.find(engine => engine.url === url);
        
        if (existingName) {
            showMessage('已存在相同名称的搜索引擎', 'error');
            return;
        }
        
        if (existingUrl) {
            showMessage('已存在相同URL的搜索引擎', 'error');
            return;
        }
        
        // 添加新搜索引擎
        const newEngine = {
            id: Date.now().toString(),
            name: name,
            url: url,
            enabled: true
        };
        
        searchEngines.push(newEngine);
        await chrome.storage.sync.set({ searchEngines: searchEngines });
        
        // 清空表单
        document.getElementById('engine-name').value = '';
        document.getElementById('engine-url').value = '';
        
        // 重新加载列表
        loadSearchEngines();
        showMessage('搜索引擎添加成功', 'success');
        
    } catch (error) {
        console.error('添加搜索引擎失败:', error);
        showMessage('添加搜索引擎失败', 'error');
    }
}

// 切换搜索引擎启用状态
async function toggleEngine(index) {
    try {
        const result = await chrome.storage.sync.get(['searchEngines']);
        const searchEngines = result.searchEngines || [];
        
        if (searchEngines[index]) {
            searchEngines[index].enabled = !searchEngines[index].enabled;
            await chrome.storage.sync.set({ searchEngines: searchEngines });
            showMessage(`${searchEngines[index].name} ${searchEngines[index].enabled ? '已启用' : '已禁用'}`, 'success');
        }
        
    } catch (error) {
        console.error('切换搜索引擎状态失败:', error);
        showMessage('操作失败', 'error');
    }
}

// 编辑搜索引擎
async function editEngine(index) {
    try {
        const result = await chrome.storage.sync.get(['searchEngines']);
        const searchEngines = result.searchEngines || [];
        const engine = searchEngines[index];
        
        if (!engine) return;
        
        const newName = prompt('请输入新的搜索引擎名称:', engine.name);
        if (newName === null) return; // 用户取消
        
        const newUrl = prompt('请输入新的搜索URL:', engine.url);
        if (newUrl === null) return; // 用户取消
        
        if (!newName.trim() || !newUrl.trim()) {
            showMessage('搜索引擎名称和URL不能为空', 'error');
            return;
        }
        
        if (!newUrl.startsWith('http://') && !newUrl.startsWith('https://')) {
            showMessage('搜索URL必须以http://或https://开头', 'error');
            return;
        }
        
        // 检查是否与其他引擎重复（排除自己）
        const duplicateName = searchEngines.find((e, i) => i !== index && e.name === newName.trim());
        const duplicateUrl = searchEngines.find((e, i) => i !== index && e.url === newUrl.trim());
        
        if (duplicateName) {
            showMessage('已存在相同名称的搜索引擎', 'error');
            return;
        }
        
        if (duplicateUrl) {
            showMessage('已存在相同URL的搜索引擎', 'error');
            return;
        }
        
        // 更新搜索引擎
        searchEngines[index].name = newName.trim();
        searchEngines[index].url = newUrl.trim();
        
        await chrome.storage.sync.set({ searchEngines: searchEngines });
        loadSearchEngines();
        showMessage('搜索引擎更新成功', 'success');
        
    } catch (error) {
        console.error('编辑搜索引擎失败:', error);
        showMessage('编辑失败', 'error');
    }
}

// 删除搜索引擎
async function deleteEngine(index) {
    try {
        const result = await chrome.storage.sync.get(['searchEngines']);
        const searchEngines = result.searchEngines || [];
        const engine = searchEngines[index];
        
        if (!engine) return;
        
        if (!confirm(`确定要删除搜索引擎"${engine.name}"吗？`)) {
            return;
        }
        
        searchEngines.splice(index, 1);
        await chrome.storage.sync.set({ searchEngines: searchEngines });
        
        loadSearchEngines();
        showMessage('搜索引擎删除成功', 'success');
        
    } catch (error) {
        console.error('删除搜索引擎失败:', error);
        showMessage('删除失败', 'error');
    }
}

// 添加模板搜索引擎
async function addTemplate(type) {
    const templates = {
        google: {
            name: 'Google 图片搜索',
            url: 'https://www.google.com/searchbyimage?image_url='
        },
        baidu: {
            name: '百度识图',
            url: 'https://graph.baidu.com/s?sign=&rt=upload&rn=10&ct=1&tn=baiduimage&objurl='
        },
        yandex: {
            name: 'Yandex 图片搜索',
            url: 'https://yandex.com/images/search?rpt=imageview&url='
        },
        tineye: {
            name: 'TinEye 反向搜索',
            url: 'https://www.tineye.com/search?url='
        },
        bing: {
            name: 'Bing 图片搜索',
            url: 'https://www.bing.com/images/searchbyimage?FORM=IRSBIQ&cbir=sbi&imgUrl='
        }
    };
    
    const template = templates[type];
    if (!template) return;
    
    try {
        const result = await chrome.storage.sync.get(['searchEngines']);
        const searchEngines = result.searchEngines || [];
        
        // 检查是否已存在
        const existing = searchEngines.find(engine => 
            engine.name === template.name || engine.url === template.url
        );
        
        if (existing) {
            showMessage(`${template.name} 已存在`, 'error');
            return;
        }
        
        // 添加模板
        const newEngine = {
            id: Date.now().toString(),
            name: template.name,
            url: template.url,
            enabled: true
        };
        
        searchEngines.push(newEngine);
        await chrome.storage.sync.set({ searchEngines: searchEngines });
        
        loadSearchEngines();
        showMessage(`${template.name} 添加成功`, 'success');
        
    } catch (error) {
        console.error('添加模板失败:', error);
        showMessage('添加模板失败', 'error');
    }
}

// 显示消息
function showMessage(message, type = 'success') {
    const messageArea = document.getElementById('message-area');
    const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
    
    messageArea.innerHTML = `
        <div class="alert ${alertClass}">
            ${escapeHtml(message)}
        </div>
    `;
    
    // 3秒后自动清除消息
    setTimeout(() => {
        messageArea.innerHTML = '';
    }, 3000);
}