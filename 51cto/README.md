# 51CTO开源社区爬虫模块

## 📋 概述

本模块为NowInOpenHarmony项目提供51CTO开源技术社区的文章爬取功能。

**数据源**: https://ost.51cto.com/postlist

## 🏗️ 架构设计

### 文件结构

```
51cto/
├── NewsListModules.ets      # 前端数据模型（TypeScript）
├── NewsSwiperModules.ets    # 前端轮播图模型（TypeScript）
└── README.md                # 本文档

services/
└── cto51_crawler.py         # 51CTO爬虫服务

models/
└── cto51.py                 # 51CTO数据模型（Python）

api/
└── cto51.py                 # 51CTO API路由
```

### 数据格式

后端数据模型完全遵循前端TypeScript接口定义：

**文章数据结构** (`NewsArticle`):
```python
{
    "id": "唯一标识符",
    "title": "文章标题",
    "date": "发布日期",
    "url": "原文链接",
    "content": [
        {"type": "text", "value": "文本内容"},
        {"type": "image", "value": "图片URL"},
        {"type": "code", "value": "代码内容"},
        {"type": "video", "value": "视频URL"}
    ],
    "category": "开源技术",
    "summary": "文章摘要",
    "source": "51CTO开源社区",
    "created_at": "2025-11-16T12:00:00",
    "updated_at": "2025-11-16T12:00:00"
}
```

**响应格式** (`NewsResponse`):
```python
{
    "articles": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "has_next": true,
    "has_prev": false
}
```

## 🚀 API接口

### 1. 获取文章列表

```http
GET /api/cto51/
```

**查询参数**:
- `page` (int): 页码，默认1
- `page_size` (int): 每页数量，默认20，最大100
- `search` (string): 搜索关键词（可选）
- `all` (boolean): 是否返回全部文章不分页，默认false

**示例**:
```bash
# 获取第1页，每页20条
curl http://localhost:8001/api/cto51/?page=1&page_size=20

# 搜索包含"OpenHarmony"的文章
curl http://localhost:8001/api/cto51/?search=OpenHarmony

# 获取全部文章不分页
curl http://localhost:8001/api/cto51/?all=true
```

### 2. 获取文章详情

```http
GET /api/cto51/{article_id}
```

**示例**:
```bash
curl http://localhost:8001/api/cto51/abc123def456
```

### 3. 手动触发爬取

```http
POST /api/cto51/crawl
```

**查询参数**:
- `max_pages` (int): 最大爬取页数，默认3，范围1-10

**示例**:
```bash
# 爬取3页
curl -X POST http://localhost:8001/api/cto51/crawl?max_pages=3
```

### 4. 获取服务状态

```http
GET /api/cto51/status/info
```

**示例**:
```bash
curl http://localhost:8001/api/cto51/status/info
```

### 5. 清空缓存

```http
POST /api/cto51/cache/clear
```

**示例**:
```bash
curl -X POST http://localhost:8001/api/cto51/cache/clear
```

## 🛠️ 技术实现

### 爬虫特性

1. **Selenium WebDriver**
   - 处理动态加载的JavaScript内容
   - 支持自动翻页功能
   - 无头浏览器模式

2. **反爬虫策略**
   - 随机User-Agent池
   - 模拟人类浏览行为（随机滚动、延迟）
   - 隐藏WebDriver特征
   - 随机访问间隔（1-3秒）

3. **内容解析**
   - BeautifulSoup HTML解析
   - 支持多种内容类型（文本、图片、视频、代码）
   - 智能日期提取
   - 自动生成摘要

4. **并发与缓存**
   - 线程锁保护（RLock）
   - 批量回调机制
   - 内存缓存
   - 去重处理

### 爬取流程

```
1. 初始化Selenium WebDriver
   ↓
2. 访问列表页 (https://ost.51cto.com/postlist)
   ↓
3. 解析 <ul class="infinite-list"> 下的所有 <li class="infinite-list-item">
   ↓
4. 遍历每个文章链接
   ↓
5. 访问文章详情页，提取内容
   ↓
6. 返回列表页，继续下一篇
   ↓
7. 点击"下一页"按钮
   ↓
8. 重复步骤3-7，直到达到最大页数
```

## 🔧 配置说明

### 环境依赖

```bash
# Python依赖（已包含在 requirements.txt）
selenium>=4.15.0
beautifulsoup4>=4.12.0
webdriver-manager>=4.0.0  # 自动管理ChromeDriver

# 系统依赖
chromium        # Docker镜像已包含
chromium-driver # Docker镜像已包含
```

### 调优参数

编辑 `services/cto51_crawler.py`:

```python
# 爬取延迟（秒）
self._random_delay(min_seconds=1.0, max_seconds=3.0)

# 页面加载超时（秒）
WebDriverWait(self.driver, 15)

# 隐式等待（秒）
driver.implicitly_wait(10)
```

## 📊 使用示例

### Python代码调用

```python
from services.cto51_crawler import Cto51Crawler

# 创建爬虫实例
crawler = Cto51Crawler(headless=True)

# 定义批量回调
def batch_callback(articles_batch):
    print(f"收到 {len(articles_batch)} 篇文章")
    for article in articles_batch:
        print(f"- {article['title']}")

# 开始爬取
articles = crawler.crawl_articles(
    max_pages=3,
    batch_callback=batch_callback
)

print(f"总共爬取 {len(articles)} 篇文章")
```

### API调用流程

```bash
# 1. 检查服务状态
curl http://localhost:8001/api/cto51/status/info

# 2. 触发爬取（后台执行）
curl -X POST http://localhost:8001/api/cto51/crawl?max_pages=5

# 3. 等待几分钟后查看结果
curl http://localhost:8001/api/cto51/?page=1&page_size=10

# 4. 查看文章详情
curl http://localhost:8001/api/cto51/{article_id}
```

## ⚠️ 注意事项

### 使用限制

1. **爬取频率**: 建议设置合理的爬取间隔，避免对目标网站造成压力
2. **IP限制**: 如果被封IP，请调整爬取策略或更换代理
3. **资源占用**: Selenium会消耗较多内存，建议在资源充足的环境运行
4. **法律合规**: 仅用于个人学习和研究，请遵守网站robots.txt和服务条款

### 常见问题

**Q: ChromeDriver找不到？**
A: Docker镜像已包含Chromium和ChromeDriver。本地开发需要安装：
```bash
# Ubuntu/Debian
sudo apt-get install chromium chromium-driver

# macOS
brew install chromium chromedriver

# Windows
下载ChromeDriver并添加到PATH
```

**Q: 爬取速度慢？**
A: 可以调整以下参数：
- 减少延迟时间（但可能增加被封风险）
- 增加max_pages限制
- 使用多线程/多进程（需要修改代码）

**Q: 内容解析不准确？**
A: 51CTO网站结构可能变化，需要更新CSS选择器：
- 编辑 `services/cto51_crawler.py` 中的 `_parse_article_detail` 方法
- 根据实际HTML结构调整选择器

## 📝 开发规范

本模块严格遵循项目的多人协作开发规范：

1. **文件命名**: 使用 `cto51_` 前缀
2. **数据模型**: 继承自统一的基础模型
3. **API路由**: 使用 `/api/cto51/` 前缀
4. **日志记录**: 使用标准logging模块
5. **错误处理**: 统一HTTPException格式

详见项目根目录的 `COLLABORATION_GUIDE.md`

## 🔄 更新日志

### v1.0.0 (2025-11-16)
- ✅ 初始版本发布
- ✅ 实现基础爬虫功能
- ✅ 完整的API接口
- ✅ 反爬虫策略
- ✅ 内存缓存系统
- ✅ 与前端数据格式完全兼容

## 📚 相关文档

- [DEPLOYMENT.md](../DEPLOYMENT.md) - 部署指南
- [COLLABORATION_GUIDE.md](../COLLABORATION_GUIDE.md) - 协作开发规范
- [README.md](../README.md) - 项目总览

## 👥 贡献者

按照项目协作规范开发，欢迎提交PR！
