# 华为轮播图API文档

## 概述

华为轮播图API是NowInOpenHarmony项目的一个重要组件，专门用于爬取和管理华为开发者网站的轮播图数据。该API提供了完整的轮播图数据获取、管理、统计和监控功能。

### 特性

- 🚀 **高效爬取**: 自动爬取华为开发者网站轮播图数据
- 📊 **智能缓存**: 内存缓存系统，支持实时数据更新
- ⏰ **定时调度**: 自动定时更新轮播图数据
- 📈 **数据统计**: 详细的数据质量分析和统计信息
- 🔧 **易于集成**: RESTful API设计，易于客户端集成
- 🐳 **容器化**: 支持Docker部署，可扩展性强

## 基础信息

- **API基础路径**: `http://localhost:8001/api/carousel`
- **API版本**: v1.0.0
- **认证方式**: 当前无需认证
- **数据格式**: JSON
- **字符编码**: UTF-8

## API端点

### 1. 获取轮播图数据

**端点**: `GET /api/carousel/slides`

**描���**: 获取当前缓存的华为轮播图数据，支持分页和过滤

**参数**:
- `page` (int, optional): 页码，从1开始，默认为1
- `page_size` (int, optional): 每页数量，范围1-100，默认为20
- `with_images_only` (bool, optional): 是否仅返回包含图片的轮播图，默认为false
- `with_text_only` (bool, optional): 是否仅返回包含文本的轮播图，默认为false

**响应示例**:
```json
{
  "slides": [
    {
      "slide_number": 1,
      "image_url": "https://developer.huawei.com/images/carousel/slide1.jpg",
      "title": "HarmonyOS 4.0 发布",
      "subtitle": "全场景智能体验",
      "description": "全新一代操作系统，带来更智能的全场景体验",
      "all_text": ["HarmonyOS", "4.0", "全场景", "智能体验"],
      "raw_text_content": "HarmonyOS 4.0 - 全场景智能体验",
      "crawl_timestamp": 1701234567.89
    }
  ],
  "total_count": 5,
  "with_images": 5,
  "with_text": 4,
  "timestamp": "2024-11-28T12:34:56.789"
}
```

### 2. 获取单个轮播图

**端点**: `GET /api/carousel/slides/{slide_id}`

**描述**: 根据轮播图ID获取单个轮播图的详细信息

**路径参数**:
- `slide_id` (int, required): 轮播图ID，从1开始

**响应**: 返回单个轮播图对象的详细信息

### 3. 获取缓存状态

**端点**: `GET /api/carousel/cache/status`

**描述**: 获取轮播图缓存的当前状态信息

**响应示例**:
```json
{
  "status": "ready",
  "cache_count": 5,
  "last_updated": "2024-11-28T12:30:00.000",
  "created_at": "2024-11-28T10:00:00.000",
  "update_count": 3,
  "error_message": null,
  "is_first_load": false,
  "uptime_seconds": 9000.0
}
```

### 4. 获取统计信息

**端点**: `GET /api/carousel/stats`

**描述**: 获取轮播图数据的详细统计信息

**响应示例**:
```json
{
  "total_slides": 5,
  "slides_with_images": 5,
  "slides_with_text": 4,
  "slides_with_both": 4,
  "data_quality_score": 90.0,
  "cache_age_hours": 2.5,
  "last_crawl_duration": null
}
```

### 5. 手动触发爬取

**端点**: `POST /api/carousel/crawl/manual`

**描述**: 手动触发华为轮播图数据爬取任务

**响应示例**:
```json
{
  "message": "手动华为轮播图爬取任务已提交",
  "status": "submitted"
}
```

### 6. 获取爬虫信息

**端点**: `GET /api/carousel/crawler/info`

**描述**: 获取轮播图爬虫的配置和状态信息

**响���示例**:
```json
{
  "config": {
    "target_url": "https://developer.huawei.com",
    "base_domain": "https://developer.huawei.com",
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
    "viewport": {
      "width": 375,
      "height": 667,
      "device_scale_factor": 2
    },
    "headless": true,
    "timeout": 30
  },
  "thread_pool_workers": 2,
  "crawler_version": "1.0.0"
}
```

### 7. 测试爬虫连接

**端点**: `GET /api/carousel/crawler/test`

**描述**: 测试轮播图爬虫的连接性和可用性

**响应示例**:
```json
{
  "target_url": "https://developer.huawei.com",
  "base_domain": "https://developer.huawei.com",
  "timestamp": 1701234567.89,
  "status": "success",
  "http_status": 200,
  "response_time": 1.23
}
```

### 8. 导出缓存数据

**端点**: `POST /api/carousel/cache/export`

**描述**: 将当前轮播图缓存数据导出到文件

**响应示例**:
```json
{
  "message": "轮播图缓存数据已成功导出到 carousel_export_20241128_123456.json",
  "file_path": "/app/data/carousel_export_20241128_123456.json",
  "export_time": "2024-11-28T12:34:56.789",
  "data_count": 5
}
```

## 数据模型

### CarouselSlide (轮播图滑块)

```json
{
  "slide_number": "int",           // 轮播图序号 (>=1)
  "image_url": "string|null",      // 轮播图图片URL
  "title": "string|null",          // 轮播图标题
  "subtitle": "string|null",       // 轮播图副标题
  "description": "string|null",    // 轮播图描述
  "all_text": "string[]",          // 轮播图所有文本内容
  "raw_text_content": "string|null", // 原始文本内容
  "crawl_timestamp": "float"       // 爬取时间戳
}
```

### ServiceStatus (服务状态)

- `ready`: 服务就绪，数据可用
- `preparing`: 准备中，数据正在更新
- `error`: 错误状态，服务异常

## 错误处理

所有API端点都遵循统一的错误响应格式：

```json
{
  "detail": "错误描述信息",
  "error_code": "ERROR_CODE",  // 可选
  "timestamp": "2024-11-28T12:34:56.789"  // 可选
}
```

### 常见HTTP状态码

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误
- `503 Service Unavailable`: 服务不可用

## 限制和配额

- **分页大小**: 最大每页100条记录
- **并发限制**: 支持多客户端并发访问
- **更新频率**: 定时更新间隔为6小时，可手动触发更新
- **缓存时间**: 数据在内存中缓存，定期自动更新

## 使用示例

### JavaScript/TypeScript

```javascript
// 获取轮播图数据
async function getCarouselSlides() {
  try {
    const response = await fetch('/api/carousel/slides?page=1&page_size=10');
    const data = await response.json();
    console.log('轮播图数据:', data);
    return data;
  } catch (error) {
    console.error('获取轮播图数据失败:', error);
  }
}

// 手动触发爬取
async function triggerCrawl() {
  try {
    const response = await fetch('/api/carousel/crawl/manual', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    const result = await response.json();
    console.log('爬取结果:', result);
  } catch (error) {
    console.error('触发爬取失败:', error);
  }
}

// 获取缓存状态
async function getCacheStatus() {
  try {
    const response = await fetch('/api/carousel/cache/status');
    const status = await response.json();
    console.log('缓存状态:', status);
    return status;
  } catch (error) {
    console.error('获取缓存状态失败:', error);
  }
}
```

### Python

```python
import requests

# 获取轮播图数据
def get_carousel_slides(page=1, page_size=20):
    try:
        response = requests.get(
            '/api/carousel/slides',
            params={
                'page': page,
                'page_size': page_size,
                'with_images_only': False
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取轮播图数据失败: {e}")
        return None

# 手动触发爬取
def trigger_crawl():
    try:
        response = requests.post('/api/carousel/crawl/manual')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"触发爬取失败: {e}")
        return None

# 获取统计信息
def get_carousel_stats():
    try:
        response = requests.get('/api/carousel/stats')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取统计信息失败: {e}")
        return None
```

### cURL

```bash
# 获取轮播图数据
curl -X GET "http://localhost:8001/api/carousel/slides?page=1&page_size=10"

# 获取单个轮播图
curl -X GET "http://localhost:8001/api/carousel/slides/1"

# 获取缓存状态
curl -X GET "http://localhost:8001/api/carousel/cache/status"

# 获取统计信息
curl -X GET "http://localhost:8001/api/carousel/stats"

# 手动触发爬取
curl -X POST "http://localhost:8001/api/carousel/crawl/manual"

# 测试爬虫连接
curl -X GET "http://localhost:8001/api/carousel/crawler/test"

# 导出缓存数据
curl -X POST "http://localhost:8001/api/carousel/cache/export"
```

## 部署说明

### Docker部署

1. 使用提供的Docker Compose配置：
```bash
# 开发环境
docker-compose -f docker-compose.carousel.yml up -d

# 生产环境
docker-compose -f docker-compose.carousel.prod.yml up -d
```

2. 使用部署脚本：
```bash
# 安装和初始化
./deploy-carousel.sh install

# 启动服务
./deploy-carousel.sh start

# 检查服务状态
./deploy-carousel.sh health
```

### 环境配置

主要环境变量：

```bash
# 华为轮播图配置
HUAWEI_TARGET_URL=https://developer.huawei.com
HUAWEI_BASE_DOMAIN=https://developer.huawei.com
MOBILE_USER_AGENT=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30
CRAWLER_RETRY_COUNT=3
CRAWLER_DELAY=5

# 调度器配置
ENABLE_SCHEDULER=true
CACHE_UPDATE_INTERVAL=360  # 6小时（秒）
```

## 监控和维护

### 健康检查

- **基础健康检查**: `GET /health`
- **API健康检查**: `GET /api/health`
- **轮播图特定检查**: `GET /api/carousel/cache/status`

### 日志监控

查看应用日志：
```bash
docker-compose -f docker-compose.carousel.yml logs -f app
```

### 数据导出

定期导出轮播图数据：
```bash
curl -X POST "http://localhost:8001/api/carousel/cache/export"
```

## 常见问题

### Q: 轮播图数据多久更新一次？
A: 默认每6小时自动更新一次，也可以通过API手动触发更新。

### Q: 如何检查轮播图服务状态？
A: 访问 `/api/carousel/cache/status` 端点查看缓存状态和服务健康情况。

### Q: 爬取失败怎么办？
A: 检查网络连接和目标网站可访问性，可以通过 `/api/carousel/crawler/test` 端点测试连接。

### Q: 如何获取历史数据？
A: 使用导出功能可以将当前缓存数据导出为JSON文件保存。

### Q: 支持自定义过滤条件吗？
A: 目前支持基本的图片和文本过滤，如需更复杂的过滤条件可以在此基础上扩展。

## 更新日志

### v1.0.0 (2024-11-28)
- 🎉 初始版本发布
- ✨ 完整的轮播图数据爬取功能
- 📊 数据统计和质量分析
- 🔄 定时更新和手动触发机制
- 🐳 Docker化部署支持
- 📚 完整的API文档

---

如有问题或建议，请查看项目GitHub仓库或联系开发团队。