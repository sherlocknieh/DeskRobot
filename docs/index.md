# Chrome 浏览器扩展架构说明

## 概述

Chrome 扩展程序主要由三个核心组件构成：
- **Background Script（后台脚本）**：运行在扩展的后台
- **Content Script（内容脚本）**：注入到网页中运行
- **Popup（弹出页面）**：用户点击扩展图标时显示的界面

## Background Script 不能做的事（需要 Content Script 或 Popup 完成）

### 1. 直接访问和操作网页 DOM

**原因**：Background Script 运行在独立的上下文中，无法直接访问网页的 DOM 结构。

**解决方案**：需要使用 Content Script

**示例场景**：
- 读取或修改网页内容
- 获取网页表单数据
- 修改网页样式
- 监听网页事件（如点击、滚动等）

```javascript
// ❌ Background Script 中无效
document.getElementById('someElement'); // undefined

// ✅ 需要在 Content Script 中执行
chrome.runtime.sendMessage({action: "getElement"}, (response) => {
  // 处理从 content script 返回的数据
});
```

### 2. 使用网页的 window 对象

**原因**：Background Script 有自己独立的 window 对象，无法访问网页的 window。

**解决方案**：通过 Content Script 访问

**示例场景**：
- 访问网页的全局变量
- 调用网页定义的函数
- 访问网页的 localStorage（注意：content script 可以访问网页的 DOM，但不能直接访问网页的 JS 变量，需要通过注入脚本）

### 3. 直接展示用户界面（非持久化）

**原因**：Background Script 没有 UI 界面。

**解决方案**：使用 Popup 页面或创建新的窗口/标签页

**示例场景**：
- 显示设置界面
- 展示扩展功能菜单
- 用户交互表单

## 只有 Background Script 能做的事

### 1. 持久化事件监听（Manifest V2）

**说明**：Background Script 可以持续运行（persistent background），始终监听事件。

**特性**：
- 监听浏览器级别的事件
- 处理长期运行的任务
- 保持扩展状态

**示例场景**：
```javascript
// 监听扩展安装事件
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === "install") {
    console.log("扩展首次安装");
  }
});

// 监听来自其他组件的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // 处理消息
});
```

### 2. 管理扩展全局状态

**说明**：Background Script 是扩展的中枢，负责协调各个组件。

**功能**：
- 维护全局变量和状态
- 作为消息中转站
- 管理数据同步

**示例**：
```javascript
// 全局状态管理
let extensionState = {
  isEnabled: true,
  userPreferences: {},
  cache: {}
};

// 供其他组件访问
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getState") {
    sendResponse(extensionState);
  }
});
```

### 3. 跨域请求（在 Manifest V2 中）

**说明**：Background Script 可以不受同源策略限制发起跨域请求（需要在 manifest.json 中声明权限）。

**示例**：
```javascript
// Background Script 中
fetch('https://api.example.com/data', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

**注意**：在 Manifest V3 中，推荐使用 Service Worker 和声明式网络请求。

### 4. 管理 Chrome API 的高级功能

**说明**：某些 Chrome API 只能在 Background Script 中调用。

**包括**：
- `chrome.webRequest`（网络请求拦截和修改）
- `chrome.declarativeNetRequest`（声明式网络请求，V3）
- `chrome.alarms`（定时器，比 setTimeout 更可靠）
- `chrome.browsingData`（清除浏览数据）
- `chrome.downloads`（下载管理）
- `chrome.history`（历史记录）
- `chrome.management`（扩展管理）

**示例**：
```javascript
// 设置定时任务
chrome.alarms.create('refreshData', {
  periodInMinutes: 30
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'refreshData') {
    // 执行定时任务
  }
});
```

### 5. 后台数据同步

**说明**：Background Script 可以在用户不使用扩展时继续工作。

**场景**：
- 定期同步数据
- 轮询服务器更新
- 后台数据处理

## 两者都能做的事

### 1. 使用 chrome.storage API

**说明**：Background Script、Content Script 和 Popup 都可以读写 chrome.storage。

**示例**：
```javascript
// 保存数据
chrome.storage.local.set({key: 'value'}, () => {
  console.log('数据已保存');
});

// 读取数据
chrome.storage.local.get(['key'], (result) => {
  console.log('获取的值：', result.key);
});
```

**应用场景**：
- 用户设置存储
- 缓存数据
- 跨组件数据共享

### 2. 消息传递

**说明**：所有组件都可以发送和接收消息。

**通信方式**：

**Content Script → Background Script：**
```javascript
// Content Script
chrome.runtime.sendMessage({
  action: "getData",
  params: {id: 123}
}, (response) => {
  console.log('收到回复：', response);
});

// Background Script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getData") {
    // 处理请求
    sendResponse({data: "some data"});
  }
  return true; // 异步响应
});
```

**Background Script → Content Script：**
```javascript
// Background Script
chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
  chrome.tabs.sendMessage(tabs[0].id, {
    action: "updateUI",
    data: "new content"
  });
});

// Content Script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "updateUI") {
    // 更新页面
  }
});
```

### 3. 使用大部分 Chrome API

**说明**：许多 Chrome API 在多个上下文中都可用。

**常用 API**：
- `chrome.runtime`（运行时通信和信息）
- `chrome.storage`（数据存储）
- `chrome.i18n`（国际化）
- `chrome.tabs`（标签页管理，部分功能）

### 4. 发起网络请求

**说明**：所有组件都可以使用 `fetch` 或 `XMLHttpRequest`。

**区别**：
- **Background Script**：可以跨域（需要权限）
- **Content Script**：受网页同源策略限制
- **Popup**：与 Background Script 类似，可以跨域

**示例**：
```javascript
// 所有组件都可以使用
fetch('https://api.example.com/data')
  .then(response => response.json())
  .then(data => console.log(data));
```

### 5. 本地数据处理

**说明**：JavaScript 计算、数据处理、算法执行等。

**场景**：
- 数据格式转换
- 文本处理
- 加密解密
- 本地计算

## 实际应用建议

### 架构设计原则

1. **Background Script 作为中枢**
   - 管理扩展的核心逻辑
   - 协调各组件通信
   - 处理需要持久化的任务

2. **Content Script 作为桥梁**
   - 连接网页和扩展
   - 操作 DOM
   - 收集网页数据

3. **Popup 作为界面**
   - 展示扩展功能
   - 用户交互入口
   - 显示状态和设置

### 通信流程示例

```
用户点击 Popup 按钮
    ↓
Popup 发送消息给 Background
    ↓
Background 处理逻辑，发送消息给 Content Script
    ↓
Content Script 操作网页 DOM
    ↓
Content Script 返回结果给 Background
    ↓
Background 更新状态并通知 Popup
    ↓
Popup 更新显示
```

## Manifest V2 vs V3 的变化

### Manifest V3 主要变化

1. **Background Script → Service Worker**
   - 不再持久运行
   - 事件驱动，空闲时自动休眠
   - 不能使用 DOM API

2. **webRequest → declarativeNetRequest**
   - 更安全的网络请求拦截
   - 声明式规则，性能更好

3. **远程代码限制**
   - 不能执行远程代码
   - 所有代码必须打包在扩展中

## 总结对比表

| 功能 | Background Script | Content Script | Popup |
|------|-------------------|----------------|-------|
| 访问网页 DOM | ❌ | ✅ | ❌ |
| 持久运行（V2）| ✅ | ❌ | ❌ |
| 跨域请求 | ✅ | ❌ | ✅ |
| 显示 UI | ❌ | ⚠️（注入） | ✅ |
| chrome.storage | ✅ | ✅ | ✅ |
| 消息通信 | ✅ | ✅ | ✅ |
| chrome.tabs | ✅（完整）| ⚠️（部分）| ✅（完整）|
| chrome.alarms | ✅ | ❌ | ❌ |
| chrome.webRequest | ✅ | ❌ | ❌ |
| 网页 window 对象 | ❌ | ⚠️（受限）| ❌ |

**图例**：
- ✅ 完全支持
- ❌ 不支持
- ⚠️ 部分支持或有限制

## 参考资源

- [Chrome Extensions 官方文档](https://developer.chrome.com/docs/extensions/)
- [Manifest V3 迁移指南](https://developer.chrome.com/docs/extensions/mv3/intro/)
- [Chrome Extension API 参考](https://developer.chrome.com/docs/extensions/reference/)
