# NowInOpenHarmony 后端服务

## 📋 项目简介

NowInOpenHarmony 是一个聚合 OpenHarmony 相关资讯的应用后端服务。该系统从 OpenHarmony 官方网站、技术博客等多源采集新闻数据，进行结构化处理，并对外提供 RESTful 风格的数据接口。

### 核心特性

- 🚀 **多源数据采集**：支持 OpenHarmony 官网新闻、技术博客、Banner 轮播图等多源数据
- 💾 **智能缓存机制**：启动预热 + 定时更新 + 线程安全的缓存管理
- 🔄 **非阻塞爬虫**：后台线程执行爬虫任务，不影响 API 响应
- 🎯 **RESTful API**：完善的 API 接口，支持分页、搜索、分类等功能
- 🐳 **Docker 部署**：完整的 Docker 和 Docker Compose 支持
- 📊 **定时任务**：自动更新数据，支持定时全量爬取

## 🛠️ 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.9+ | 编程语言 |
| FastAPI | 0.104.1 | Web 框架 |
| Uvicorn | 0.24.0 | ASGI 服务器 |
| SQLite | - | 数据库（开发环境） |
| Requests | 2.31.0 | HTTP 客户端 |
| BeautifulSoup | 4.12.2 | HTML 解析 |
| Selenium | 4.15.0 | 浏览器自动化 |
| APScheduler | 3.10.4 | 任务调度 |
| Docker | - | 容器化部署 |

## 🚀 快速开始

### 本地开发环境

#### 1. 环境要求

- Python 3.9+
- pip

#### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 启动服务

```bash
# 方式1: 使用启动脚本（推荐）
python run.py

# 方式2: 使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

#### 4. 访问服务

- 服务地址: http://localhost:8001
- API 文档: http://localhost:8001/docs
- 健康检查: http://localhost:8001/health

---

## 🐳 服务器部署（重点）

### 部署架构

本项目采用 Docker 容器化部署，包含两个主要容器：

1. **Selenium 容器**：提供 Chromium 浏览器环境，用于动态网页爬取
2. **NIOHServer 容器**：后端 API 服务容器

两个容器通过 Docker 网络 `ohnet` 进行通信。

### 部署前准备

#### 1. 服务器要求

- **操作系统**: Linux (Ubuntu 20.04+, CentOS 7+, Debian 10+)
- **Docker**: 20.10+
- **内存**: 最低 2GB，推荐 4GB+
- **CPU**: 最低 2 核，推荐 4 核+
- **磁盘**: 至少 10GB 可用空间

#### 2. 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker ps
```

#### 3. 构建镜像

在项目根目录执行：

```bash
# 构建后端服务镜像
docker build -t openharmony-server:latest .

# 查看镜像
docker images | grep openharmony-server
```

### 一键部署命令

部署脚本提供了两种等价写法，任选其一执行。

#### 方式一：单行命令（推荐）

```bash
# 1. 清理旧容器
docker rm -f NIOHServer selenium 2>/dev/null || true

# 2. 创建 Docker 网络
docker network create ohnet || true

# 3. 启动 Selenium 容器
docker run -d --name selenium --network ohnet --shm-size=2g --restart unless-stopped -e SE_NODE_MAX_SESSIONS=1 -e SE_NODE_OVERRIDE_MAX_SESSIONS=true -e SE_SESSION_REQUEST_TIMEOUT=20 -e SE_NODE_SESSION_TIMEOUT=60 --cpus=0.6 selenium/standalone-chromium:latest

# 4. 启动后端服务容器
docker run -d --name NIOHServer --network ohnet -p 32776:8001 --shm-size=1g -e TZ=Asia/Shanghai -e ENABLE_SCHEDULER=true -e BANNER_USE_ENHANCED=true -e SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub -e SELENIUM_USE_USER_DATA_DIR=false openharmony-server:latest

# 5. 检查 Selenium 服务状态
docker exec -it NIOHServer sh -lc "curl -s http://selenium:4444/status | grep -E '\"ready\"[[:space:]]*:[[:space:]]*true' || true"

# 6. 查看容器资源使用情况
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' | egrep 'NIOHServer|selenium'
```

#### 方式二：多行命令（带续行符）

```bash
# 1. 清理旧容器
docker rm -f NIOHServer selenium 2>/dev/null || true

# 2. 创建 Docker 网络
docker network create ohnet || true

# 3. 启动 Selenium 容器
docker run -d --name selenium --network ohnet \
  --shm-size=2g --restart unless-stopped \
  -e SE_NODE_MAX_SESSIONS=1 \
  -e SE_NODE_OVERRIDE_MAX_SESSIONS=true \
  -e SE_SESSION_REQUEST_TIMEOUT=20 \
  -e SE_NODE_SESSION_TIMEOUT=60 \
  --cpus=0.6 \
  selenium/standalone-chromium:latest

# 4. 启动后端服务容器
docker run -d --name NIOHServer --network ohnet \
  -p 32776:8001 --shm-size=1g \
  -e TZ=Asia/Shanghai \
  -e ENABLE_SCHEDULER=true \
  -e BANNER_USE_ENHANCED=true \
  -e SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub \
  -e SELENIUM_USE_USER_DATA_DIR=false \
  openharmony-server:latest

# 5. 检查 Selenium 服务状态
docker exec -it NIOHServer sh -lc "curl -s http://selenium:4444/status | grep -E '\"ready\"[[:space:]]*:[[:space:]]*true' || true"

# 6. 查看容器资源使用情况
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' | egrep 'NIOHServer|selenium'
```

### 部署命令详解

#### 1. 清理旧容器

```bash
docker rm -f NIOHServer selenium 2>/dev/null || true
```

- `docker rm -f`: 强制删除容器
- `2>/dev/null`: 忽略错误输出（容器不存在时）
- `|| true`: 确保命令总是返回成功，即使容器不存在

#### 2. 创建 Docker 网络

```bash
docker network create ohnet || true
```

- 创建名为 `ohnet` 的自定义网络
- 允许容器间通过容器名互相通信
- `|| true`: 网络已存在时不报错

#### 3. 启动 Selenium 容器

```bash
docker run -d --name selenium --network ohnet \
  --shm-size=2g \              # 共享内存 2GB（Chromium 需要）
  --restart unless-stopped \    # 自动重启策略
  -e SE_NODE_MAX_SESSIONS=1 \   # 最大会话数
  -e SE_NODE_OVERRIDE_MAX_SESSIONS=true \
  -e SE_SESSION_REQUEST_TIMEOUT=20 \  # 会话请求超时
  -e SE_NODE_SESSION_TIMEOUT=60 \     # 会话超时
  --cpus=0.6 \                 # CPU 限制 60%
  selenium/standalone-chromium:latest
```

**关键参数说明**：

- `--shm-size=2g`: Chromium 需要较大的共享内存，避免崩溃
- `--cpus=0.6`: 限制 CPU 使用率，防止资源占用过高
- `SE_NODE_MAX_SESSIONS=1`: 单个会话，避免并发问题
- `--restart unless-stopped`: 容器异常退出自动重启

**镜像信息**：
- **镜像名称**: selenium/standalone-chromium:latest
- **镜像大小**: ~2.1 GB
- **基础系统**: Ubuntu 24.04
- **架构**: amd64 (x86_64)
- **暴露端口**: 4444 (WebDriver), 5900 (VNC), 7900 (noVNC)

#### 4. 启动后端服务容器

```bash
docker run -d --name NIOHServer --network ohnet \
  -p 32776:8001 \              # 端口映射
  --shm-size=1g \              # 共享内存 1GB
  -e TZ=Asia/Shanghai \        # 时区设置
  -e ENABLE_SCHEDULER=true \   # 启用定时任务
  -e BANNER_USE_ENHANCED=true \  # 启用增强版 Banner 爬虫
  -e SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub \  # Selenium 服务地址
  -e SELENIUM_USE_USER_DATA_DIR=false \  # 不使用用户数据目录
  openharmony-server:latest
```

**关键参数说明**：

- `-p 32776:8001`: 将容器的 8001 端口映射到主机的 32776 端口
- `SELENIUM_REMOTE_URL`: 指向 Selenium 容器的 WebDriver 地址
- `ENABLE_SCHEDULER=true`: 启用定时任务（每 30 分钟更新数据）
- `BANNER_USE_ENHANCED=true`: 使用 Selenium 爬取动态 Banner 图片

### 环境变量配置

#### 后端服务环境变量

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `HOST` | 0.0.0.0 | 服务监听地址 |
| `PORT` | 8001 | 服务端口 |
| `TZ` | UTC | 时区设置 |
| `ENABLE_SCHEDULER` | false | 是否启用定时任务 |
| `BANNER_USE_ENHANCED` | true | 是否使用 Selenium 爬虫 |
| `SELENIUM_REMOTE_URL` | - | Selenium 服务地址 |
| `SELENIUM_USE_USER_DATA_DIR` | false | 是否使用用户数据目录 |
| `LOG_LEVEL` | INFO | 日志级别 |
| `CORS_ORIGINS` | * | CORS 允许的源 |

#### Selenium 容器环境变量（高级配置）

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `SE_NODE_MAX_SESSIONS` | 1 | 最大并发会话数 |
| `SE_NODE_SESSION_TIMEOUT` | 300 | 会话超时时间（秒） |
| `SE_SESSION_REQUEST_TIMEOUT` | 300 | 会话请求超时（秒） |
| `SE_SCREEN_WIDTH` | 1920 | 浏览器窗口宽度 |
| `SE_SCREEN_HEIGHT` | 1080 | 浏览器窗口高度 |
| `SE_START_VNC` | true | 是否启用 VNC 服务 |
| `SE_VNC_PORT` | 5900 | VNC 端口 |
| `SE_NO_VNC_PORT` | 7900 | noVNC 端口（浏览器访问） |
| `TZ` | UTC | 时区设置 |
| `SE_LOG_LEVEL` | INFO | 日志级别 |
| `SE_ENABLE_TRACING` | true | 是否启用追踪 |

### Selenium 容器详细配置

#### 端口说明

- **4444**: WebDriver 协议端口（主要通信端口）
- **5900**: VNC 端口（用于远程查看浏览器界面）
- **7900**: noVNC 端口（通过浏览器访问 VNC）
- **9000**: 内部服务端口

#### 启用 VNC 调试（可选）

如果需要通过 VNC 查看 Selenium 浏览器的实时画面，可以映射 VNC 端口：

```bash
# 启动 Selenium 容器并暴露 VNC 端口
docker run -d --name selenium --network ohnet \
  --shm-size=2g --restart unless-stopped \
  -p 4444:4444 \
  -p 5900:5900 \
  -p 7900:7900 \
  -e SE_NODE_MAX_SESSIONS=1 \
  -e SE_NODE_OVERRIDE_MAX_SESSIONS=true \
  -e SE_SESSION_REQUEST_TIMEOUT=20 \
  -e SE_NODE_SESSION_TIMEOUT=60 \
  -e SE_START_VNC=true \
  -e SE_VNC_NO_PASSWORD=1 \
  --cpus=0.6 \
  selenium/standalone-chromium:latest
```

访问方式：
- **VNC 客户端**: `vnc://your-server-ip:5900`（需要 VNC Viewer）
- **noVNC 浏览器**: `http://your-server-ip:7900`（直接在浏览器中查看）

#### 性能调优参数

根据服务器性能调整以下参数：

```bash
# 高性能配置（4核8G以上）
docker run -d --name selenium --network ohnet \
  --shm-size=4g \
  --memory=4g \
  --cpus=2.0 \
  -e SE_NODE_MAX_SESSIONS=2 \
  -e SE_NODE_SESSION_TIMEOUT=120 \
  selenium/standalone-chromium:latest

# 低性能配置（2核2G）
docker run -d --name selenium --network ohnet \
  --shm-size=1g \
  --memory=1.5g \
  --cpus=0.5 \
  -e SE_NODE_MAX_SESSIONS=1 \
  -e SE_NODE_SESSION_TIMEOUT=60 \
  selenium/standalone-chromium:latest

# 最小化配置（仅用于测试）
docker run -d --name selenium --network ohnet \
  --shm-size=512m \
  --memory=1g \
  --cpus=0.3 \
  -e SE_NODE_MAX_SESSIONS=1 \
  -e SE_SCREEN_WIDTH=1280 \
  -e SE_SCREEN_HEIGHT=720 \
  selenium/standalone-chromium:latest
```

#### 浏览器配置

Selenium 容器内置配置：
- **浏览器**: Chromium (稳定版)
- **分辨率**: 1920x1080 (可通过环境变量调整)
- **显示服务**: Xvfb (虚拟显示)
- **VNC 服务**: TigerVNC
- **平台**: Linux

#### 常用环境变量组合

```bash
# 生产环境推荐配置
-e SE_NODE_MAX_SESSIONS=1 \
-e SE_NODE_SESSION_TIMEOUT=120 \
-e SE_SESSION_REQUEST_TIMEOUT=60 \
-e SE_SCREEN_WIDTH=1920 \
-e SE_SCREEN_HEIGHT=1080 \
-e SE_START_VNC=false \
-e TZ=Asia/Shanghai

# 调试环境配置（启用 VNC）
-e SE_NODE_MAX_SESSIONS=1 \
-e SE_NODE_SESSION_TIMEOUT=300 \
-e SE_START_VNC=true \
-e SE_VNC_NO_PASSWORD=1 \
-e SE_LOG_LEVEL=DEBUG

# 高并发配置（需要足够资源）
-e SE_NODE_MAX_SESSIONS=3 \
-e SE_NODE_OVERRIDE_MAX_SESSIONS=true \
-e SE_NODE_SESSION_TIMEOUT=180 \
-e SE_SCREEN_WIDTH=1280 \
-e SE_SCREEN_HEIGHT=720
```

### 部署验证

#### 1. 检查容器状态

```bash
# 查看所有容器
docker ps

# 查看特定容器日志
docker logs NIOHServer
docker logs selenium

# 实时查看日志
docker logs -f NIOHServer
```

#### 查看 Selenium 容器详细信息

```bash
# 查看容器完整配置
docker inspect selenium

# 查看镜像信息
docker inspect selenium/standalone-chromium:latest

# 查看容器环境变量
docker inspect selenium --format='{{range .Config.Env}}{{println .}}{{end}}'

# 查看容器 IP 地址
docker inspect selenium --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'

# 查看资源配置
docker inspect selenium --format='内存: {{.HostConfig.Memory}} | 共享内存: {{.HostConfig.ShmSize}} | CPU: {{.HostConfig.NanoCpus}}'

# 查看端口映射
docker port selenium

# 一键查看所有关键信息
echo "=== Selenium 容器信息 ===" && \
docker ps --filter name=selenium && \
echo -e "\n=== 资源使用 ===" && \
docker stats selenium --no-stream && \
echo -e "\n=== Selenium 服务状态 ===" && \
docker exec selenium curl -s http://localhost:4444/status 2>/dev/null | head -30
```

#### 2. 测试 API 接口

```bash
# 健康检查
curl http://localhost:32776/health

# 获取 API 文档
curl http://localhost:32776/docs

# 获取新闻列表
curl http://localhost:32776/api/news/?all=true

# 获取 Banner 图片
curl http://localhost:32776/api/banner/mobile
```

#### 3. 检查 Selenium 连接

```bash
# 从后端容器内部测试
docker exec -it NIOHServer sh -lc "curl -s http://selenium:4444/status"

# 或使用 grep 检查就绪状态
docker exec -it NIOHServer sh -lc "curl -s http://selenium:4444/status | grep -E '\"ready\"[[:space:]]*:[[:space:]]*true' || true"
```

#### 4. 查看资源使用

```bash
# 查看 CPU 和内存使用
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' | egrep 'NIOHServer|selenium'

# 持续监控
docker stats NIOHServer selenium
```

### 数据持久化（可选）

如果需要持久化数据，可以添加数据卷：

```bash
# 创建数据卷
docker volume create openharmony-data

# 启动容器时挂载数据卷
docker run -d --name NIOHServer --network ohnet \
  -p 32776:8001 \
  -v openharmony-data:/app/data \
  -v openharmony-logs:/app/logs \
  -e TZ=Asia/Shanghai \
  -e ENABLE_SCHEDULER=true \
  -e BANNER_USE_ENHANCED=true \
  -e SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub \
  -e SELENIUM_USE_USER_DATA_DIR=false \
  openharmony-server:latest
```

### 容器管理命令

```bash
# 停止容器
docker stop NIOHServer selenium

# 启动容器
docker start NIOHServer selenium

# 重启容器
docker restart NIOHServer selenium

# 删除容器
docker rm -f NIOHServer selenium

# 删除网络
docker network rm ohnet

# 删除镜像
docker rmi openharmony-server:latest

# 进入容器
docker exec -it NIOHServer sh
docker exec -it selenium sh

# 查看容器详细信息
docker inspect NIOHServer
```

### 更新部署

当代码更新后，需要重新构建镜像并部署：

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker build -t openharmony-server:latest .

# 3. 停止并删除旧容器
docker rm -f NIOHServer

# 4. 启动新容器
docker run -d --name NIOHServer --network ohnet \
  -p 32776:8001 --shm-size=1g \
  -e TZ=Asia/Shanghai \
  -e ENABLE_SCHEDULER=true \
  -e BANNER_USE_ENHANCED=true \
  -e SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub \
  -e SELENIUM_USE_USER_DATA_DIR=false \
  openharmony-server:latest
```

---

## 📡 API 接口说明

### 服务访问地址

部署成功后，服务将在以下地址可用：

- **API 服务**: http://your-server-ip:32776
- **API 文档**: http://your-server-ip:32776/docs
- **健康检查**: http://your-server-ip:32776/health

### 核心 API 端点

#### 基础服务

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | 服务信息 |
| GET | `/health` | 健康检查 |
| GET | `/api/health` | 详细健康检查 |
| GET | `/docs` | Swagger API 文档 |
| GET | `/redoc` | ReDoc API 文档 |

#### 新闻接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/news/` | 获取新闻列表（支持分页、搜索） |
| GET | `/api/news/openharmony` | 获取 OpenHarmony 官网新闻 |
| GET | `/api/news/blog` | 获取技术博客文章 |
| POST | `/api/news/crawl` | 手动触发新闻爬取 |
| GET | `/api/news/status/info` | 获取服务状态 |

#### Banner 轮播图接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/banner/mobile` | 获取手机版 Banner 图片 |
| GET | `/api/banner/mobile/enhanced` | 增强版 Banner 爬虫 |
| POST | `/api/banner/crawl` | 手动触发 Banner 爬取 |
| GET | `/api/banner/status` | 获取 Banner 服务状态 |
| DELETE | `/api/banner/cache/clear` | 清空 Banner 缓存 |

### API 调用示例

```bash
# 获取所有新闻
curl http://localhost:32776/api/news/?all=true

# 分页获取新闻
curl "http://localhost:32776/api/news/?page=1&page_size=20"

# 搜索新闻
curl "http://localhost:32776/api/news/?search=OpenHarmony"

# 获取 Banner 图片
curl http://localhost:32776/api/banner/mobile

# 手动触发爬取（POST 请求）
curl -X POST http://localhost:32776/api/news/crawl

# 查看服务状态
curl http://localhost:32776/api/news/status/info
```

---

## 🔧 故障排查

### 常见问题

#### 1. 容器无法启动

**问题**: 容器启动后立即退出

**排查步骤**:

```bash
# 查看容器日志
docker logs NIOHServer

# 查看容器退出状态
docker ps -a | grep NIOHServer

# 检查镜像是否存在
docker images | grep openharmony-server
```

**可能原因**:
- 镜像构建失败
- 端口被占用
- 环境变量配置错误

#### 2. Selenium 连接失败

**问题**: 后端无法连接到 Selenium 服务

**排查步骤**:

```bash
# 检查 Selenium 容器状态
docker ps | grep selenium

# 检查容器是否正在运行
docker inspect selenium --format='{{.State.Status}}'

# 测试 Selenium 服务是否就绪
docker exec selenium curl -s http://localhost:4444/status

# 从后端容器测试连接
docker exec -it NIOHServer curl http://selenium:4444/status

# 检查网络配置
docker network inspect ohnet | grep -A 10 selenium

# 检查容器 IP
docker inspect selenium --format='{{range .NetworkSettings.Networks}}IP: {{.IPAddress}}{{end}}'

# 查看 Selenium 容器日志
docker logs selenium --tail 50

# 检查防火墙规则（如果适用）
iptables -L -n | grep 4444
```

**常见错误及解决方案**:

1. **错误**: `Connection refused`
   ```bash
   # 解决: 等待 Selenium 启动完成（通常需要 10-30 秒）
   docker logs selenium -f
   # 看到 "Selenium Server is up and running" 后即可
   ```

2. **错误**: `Could not start a new session`
   ```bash
   # 解决: 检查共享内存是否足够
   docker inspect selenium --format='ShmSize: {{.HostConfig.ShmSize}}'
   # 应该至少是 2147483648 (2GB)
   ```

3. **错误**: `Container not found`
   ```bash
   # 解决: 检查容器名称和网络
   docker ps -a --filter name=selenium
   docker network ls | grep ohnet
   ```

4. **错误**: `Session timeout`
   ```bash
   # 解决: 调整超时参数
   docker rm -f selenium
   docker run -d --name selenium --network ohnet \
     -e SE_NODE_SESSION_TIMEOUT=180 \
     -e SE_SESSION_REQUEST_TIMEOUT=60 \
     --shm-size=2g \
     selenium/standalone-chromium:latest
   ```

**解决方案检查清单**:
- ✅ 确保两个容器在同一网络 `ohnet`
- ✅ 检查 `SELENIUM_REMOTE_URL` 环境变量为 `http://selenium:4444/wd/hub`
- ✅ 确认 Selenium 容器的 `--shm-size` 至少为 2GB
- ✅ 等待 Selenium 完全启动（查看日志确认）
- ✅ 检查系统内存是否充足

#### 3. Banner 爬取失败

**问题**: Banner 图片爬取不成功

**解决方案**:

```bash
# 方案1: 降级到传统爬虫
docker run -d --name NIOHServer --network ohnet \
  -p 32776:8001 \
  -e BANNER_USE_ENHANCED=false \
  openharmony-server:latest

# 方案2: 增加 Selenium 资源
docker rm -f selenium
docker run -d --name selenium --network ohnet \
  --shm-size=4g \
  --cpus=1.0 \
  selenium/standalone-chromium:latest
```

#### 4. 端口占用

**问题**: 端口 32776 已被占用

**排查**:

```bash
# 查看端口占用
netstat -tuln | grep 32776
# 或
ss -tuln | grep 32776

# 查找占用进程
lsof -i :32776
```

**解决方案**:

```bash
# 方案1: 使用其他端口
docker run -d --name NIOHServer --network ohnet \
  -p 8001:8001 \
  ...

# 方案2: 停止占用端口的进程
kill -9 <PID>
```

#### 5. 内存不足

**问题**: 容器因内存不足被 OOM Killer 杀死

**排查**:

```bash
# 查看系统内存
free -h

# 查看 Docker 日志
dmesg | grep -i oom
```

**解决方案**:

```bash
# 限制容器内存使用
docker run -d --name NIOHServer --network ohnet \
  -p 32776:8001 \
  --memory=1g \
  --memory-swap=2g \
  ...
```

#### 6. 日志查看

```bash
# 查看后端日志
docker logs NIOHServer
docker logs -f NIOHServer  # 实时查看

# 查看 Selenium 日志
docker logs selenium

# 进入容器查看应用日志
docker exec -it NIOHServer sh
cd logs
tail -f openharmony_api_*.log
```

### 性能优化建议

#### 1. Selenium 容器优化

```bash
# 增加共享内存
--shm-size=4g

# 调整 CPU 限制
--cpus=1.0

# 调整会话超时
-e SE_NODE_SESSION_TIMEOUT=120
```

#### 2. 后端容器优化

```bash
# 添加资源限制
--memory=2g
--memory-swap=4g
--cpus=2.0

# 调整日志级别
-e LOG_LEVEL=WARNING
```

#### 3. 系统级优化

```bash
# 清理 Docker 系统
docker system prune -a

# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune
```

---

## 📊 监控与维护

### 日志管理

```bash
# 查看日志大小
docker exec -it NIOHServer du -sh /app/logs

# 清理旧日志（保留最近 7 天）
docker exec -it NIOHServer sh -c "find /app/logs -name '*.log' -mtime +7 -delete"
```

### 定期维护

```bash
# 每周执行一次
# 1. 清理 Docker 缓存
docker system prune -f

# 2. 重启容器
docker restart NIOHServer selenium

# 3. 检查磁盘空间
df -h

# 4. 备份数据库（如果有持久化数据）
docker exec NIOHServer sqlite3 /app/openharmony_news.db ".backup /app/data/backup.db"
```

### 监控指标

```bash
# 实时监控容器资源使用
docker stats NIOHServer selenium

# 查看容器网络统计
docker inspect NIOHServer | grep -A 10 Networks

# 查看 API 响应时间（在容器内）
docker exec -it NIOHServer curl -w "@-" -o /dev/null -s http://localhost:8001/health <<'EOF'
    time_total: %{time_total}s
EOF
```

### Selenium 容器监控与调试

#### 实时监控

```bash
# 监控 Selenium 资源使用
docker stats selenium --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}"

# 持续监控
watch -n 2 'docker stats selenium --no-stream'

# 查看 Selenium 进程
docker top selenium

# 查看容器内存详情
docker exec selenium free -h

# 查看共享内存使用情况
docker exec selenium df -h /dev/shm
```

#### Selenium 服务状态检查

```bash
# 检查 Selenium 就绪状态
docker exec selenium curl -s http://localhost:4444/status | grep -o '"ready":[^,]*'

# 查看 Selenium 版本
docker exec selenium curl -s http://localhost:4444/status | grep -o '"version":"[^"]*"'

# 查看当前会话数
docker exec selenium curl -s http://localhost:4444/status | grep -o '"sessionCount":[0-9]*'

# 完整状态信息（如果安装了 jq）
docker exec selenium curl -s http://localhost:4444/status | jq '.'

# 不使用 jq 的格式化输出
docker exec selenium curl -s http://localhost:4444/status | python3 -m json.tool
```

#### VNC 远程调试

如果启用了 VNC，可以远程查看浏览器运行情况：

```bash
# 检查 VNC 是否启用
docker exec selenium ps aux | grep vnc

# 通过 noVNC 在浏览器中访问（需要映射端口）
# 访问: http://your-server-ip:7900

# 使用 VNC 客户端连接
# 地址: vnc://your-server-ip:5900
```

#### 日志分析

```bash
# 查看 Selenium 启动日志
docker logs selenium --tail 100

# 搜索错误日志
docker logs selenium 2>&1 | grep -i error

# 搜索警告信息
docker logs selenium 2>&1 | grep -i warn

# 实时查看日志
docker logs selenium -f

# 查看特定时间段的日志
docker logs selenium --since 10m

# 导出日志到文件
docker logs selenium > selenium-logs.txt 2>&1
```

#### 性能基准测试

```bash
# 测试 WebDriver 响应时间
time docker exec selenium curl -s http://localhost:4444/status > /dev/null

# 从后端容器测试连接速度
time docker exec NIOHServer curl -s http://selenium:4444/status > /dev/null

# 批量测试（10次）
for i in {1..10}; do
  echo "Test $i:"
  time docker exec NIOHServer curl -s http://selenium:4444/status > /dev/null 2>&1
done

# 监控连接数
watch -n 1 'docker exec selenium netstat -an | grep 4444 | wc -l'
```

#### 常用调试命令

```bash
# 进入 Selenium 容器
docker exec -it selenium bash

# 在容器内查看浏览器版本
docker exec selenium chromium --version

# 查看容器环境变量
docker exec selenium env | sort

# 查看容器内存映射
docker exec selenium cat /proc/meminfo

# 查看容器限制
docker exec selenium cat /sys/fs/cgroup/memory/memory.limit_in_bytes

# 查看容器启动时间
docker inspect selenium --format='{{.State.StartedAt}}'

# 查看容器运行时长
docker inspect selenium --format='Started: {{.State.StartedAt}} | Running: {{.State.Running}}'

# 查看容器重启次数
docker inspect selenium --format='Restart Count: {{.RestartCount}}'
```

---

## 📁 项目结构

```
HongYiXun_Backend/
├── api/                        # API 接口模块
│   ├── news.py                # 新闻 API
│   └── banner.py              # Banner API
├── core/                       # 核心模块
│   ├── cache.py               # 缓存管理
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库管理
│   ├── logging_config.py      # 日志配置
│   └── scheduler.py           # 定时任务
├── models/                     # 数据模型
│   ├── news.py                # 新闻模型
│   └── banner.py              # Banner 模型
├── services/                   # 服务层（爬虫）
│   ├── news_service.py        # 新闻服务
│   ├── openharmony_news_crawler.py    # 官网新闻爬虫
│   ├── openharmony_blog_crawler.py    # 博客爬虫
│   ├── mobile_banner_crawler.py       # Banner 爬虫
│   └── enhanced_mobile_banner_crawler.py  # 增强版 Banner 爬虫
├── logs/                       # 日志目录
├── data/                       # 数据目录
├── main.py                     # FastAPI 应用入口
├── run.py                      # 启动脚本
├── requirements.txt            # Python 依赖
├── Dockerfile                  # Docker 镜像配置
└── README.md                   # 项目文档
```

---

## 📝 许可证

```
Copyright (c) 2025 XBXyftx
Licensed under the Apache License, Version 2.0
```

详见项目根目录的 LICENSE 文件。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📮 联系方式

如有问题或建议，请通过 GitHub Issues 反馈。

---

**最后更新**: 2025-12-10  
**版本**: 2.0.0  
**维护状态**: ✅ 积极维护中

