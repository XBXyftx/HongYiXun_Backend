#!/bin/bash

# Copyright (c) 2025 XBXyftx
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# 华为轮播图后端部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="nowinopenharmony_carousel"
COMPOSE_FILE="docker-compose.carousel.yml"
APP_CONTAINER_NAME="nowinopenharmony_carousel"

# 函数定义
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker 服务未运行，请启动 Docker 服务"
        exit 1
    fi

    log_success "Docker 环境检查通过"
}

create_directories() {
    log_info "创建必要的目录..."

    # 创建数据目录
    mkdir -p data logs temp
    mkdir -p nginx/conf.d ssl
    mkdir -p monitoring/{grafana/{dashboards,datasources},prometheus}

    # 设置权限
    chmod -R 755 data logs temp
    chmod -R 755 nginx monitoring

    log_success "目录创建完成"
}

setup_config() {
    log_info "设置配置文件..."

    # 创建环境配置文件
    if [ ! -f .env ]; then
        cat > .env << EOF
# 华为轮播图后端环境配置
HOST=0.0.0.0
PORT=8001
DEBUG=false
LOG_LEVEL=INFO

# 数据库配置
DATABASE_URL=sqlite:///./data/openharmony_news.db

# 调度器配置
ENABLE_SCHEDULER=true
CACHE_UPDATE_INTERVAL=360  # 6小时
FULL_CRAWL_HOUR=2

# 华为轮播图配置
HUAWEI_TARGET_URL=https://developer.huawei.com
HUAWEI_BASE_DOMAIN=https://developer.huawei.com
MOBILE_USER_AGENT=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15
MOBILE_VIEWPORT_WIDTH=375
MOBILE_VIEWPORT_HEIGHT=667
MOBILE_DEVICE_SCALE_FACTOR=2
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30
CRAWLER_RETRY_COUNT=3
CRAWLER_DELAY=5

# CORS配置
CORS_ORIGINS=*

# 缓存配置
ENABLE_CACHE=true
CACHE_INITIAL_LOAD=true
EOF
        log_success "环境配置文件 .env 已创建"
    else
        log_warning "环境配置文件 .env 已存在，跳过创建"
    fi

    # 创建Nginx配置
    if [ ! -f nginx/conf.d/openharmony.conf ]; then
        cat > nginx/conf.d/openharmony.conf << EOF
upstream openharmony_app {
    server app:8001;
}

server {
    listen 80;
    server_name localhost;

    # 安全头部
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API路由
    location / {
        proxy_pass http://openharmony_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # 缓存设置
        proxy_cache_bypass \$http_pragma;
        proxy_cache_revalidate on;
        proxy_cache_min_uses 1;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
    }

    # 健康检查
    location /health {
        proxy_pass http://openharmony_app/health;
        access_log off;
    }

    # 静态文件
    location /static/ {
        alias /app/static/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
EOF
        log_success "Nginx 配置已创建"
    fi

    # 创建Prometheus配置
    if [ ! -f monitoring/prometheus.yml ]; then
        cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'openharmony-carousel'
    static_configs:
      - targets: ['app:8001']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF
        log_success "Prometheus 配置已创建"
    fi
}

build_images() {
    log_info "构建 Docker 镜像..."

    # 构建主应用镜像
    docker build -f Dockerfile.carousel -t ${PROJECT_NAME}_app:latest .

    log_success "Docker 镜像构建完成"
}

install() {
    log_info "安装部署环境..."

    check_docker
    create_directories
    setup_config
    build_images

    log_success "安装完成！"
}

start() {
    log_info "启动服务..."

    # 检查配置文件
    if [ ! -f $COMPOSE_FILE ]; then
        log_error "Docker Compose 文件 $COMPOSE_FILE 不存在"
        exit 1
    fi

    # 启动服务
    docker-compose -f $COMPOSE_FILE up -d

    log_success "服务启动完成！"

    # 显示服务状态
    sleep 5
    status
}

stop() {
    log_info "停止服务..."

    docker-compose -f $COMPOSE_FILE down

    log_success "服务已停止"
}

restart() {
    log_info "重启服务..."

    stop
    sleep 2
    start
}

status() {
    log_info "服务状态："
    echo

    # Docker 容器状态
    docker-compose -f $COMPOSE_FILE ps

    echo
    log_info "服务访问地址："
    echo "  - 主应用: http://localhost:8001"
    echo "  - API文档: http://localhost:8001/docs"
    echo "  - 健康检查: http://localhost:8001/health"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3000 (admin/admin)"

    echo
    log_info "华为轮播图API端点："
    echo "  - 轮播图数据: http://localhost:8001/api/carousel/slides"
    echo "  - 轮播图统计: http://localhost:8001/api/carousel/stats"
    echo "  - 轮播图状态: http://localhost:8001/api/carousel/cache/status"
}

logs() {
    local service=${1:-app}

    log_info "查看 $service 服务日志..."
    docker-compose -f $COMPOSE_FILE logs -f $service
}

health() {
    log_info "检查服务健康状态..."
    echo

    # 检查主应用
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        log_success "✅ 主应用健康"
    else
        log_error "❌ 主应用异常"
    fi

    # 检查华为轮播图API
    if curl -f http://localhost:8001/api/carousel/cache/status > /dev/null 2>&1; then
        log_success "✅ 华为轮播图API正常"
    else
        log_warning "⚠️ 华为轮播图API可能需要初始化"
    fi

    # 检查数据库连接
    if docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready -U openharmony > /dev/null 2>&1; then
        log_success "✅ 数据库连接正常"
    else
        log_error "❌ 数据库连接异常"
    fi

    # 检查Redis连接
    if docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "✅ Redis连接正常"
    else
        log_error "❌ Redis连接异常"
    fi
}

update() {
    log_info "更新服务..."

    # 停止服务
    stop

    # 重新构建镜像
    build_images

    # 启动服务
    start

    log_success "服务更新完成！"
}

cleanup() {
    log_warning "这将删除所有相关的容器、镜像和数据卷，确定要继续吗？(y/N)"
    read -r response

    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "清理部署环境..."

        docker-compose -f $COMPOSE_FILE down -v --rmi all

        # 删除相关镜像
        docker rmi ${PROJECT_NAME}_app:latest 2>/dev/null || true

        log_success "清理完成！"
    else
        log_info "清理操作已取消"
    fi
}

# 主逻辑
case "$1" in
    install)
        install
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    health)
        health
        ;;
    update)
        update
        ;;
    cleanup)
        cleanup
        ;;
    *)
        echo "华为轮播图后端部署脚本"
        echo
        echo "用法: $0 {install|start|stop|restart|status|logs|health|update|cleanup}"
        echo
        echo "命令说明："
        echo "  install   - 初始化安装部署环境"
        echo "  start     - 启动服务"
        echo "  stop      - 停止服务"
        echo "  restart   - 重启服务"
        echo "  status    - 查看服务状态"
        echo "  logs      - 查看服务日志 (logs [service])"
        echo "  health    - 检查服务健康状态"
        echo "  update    - 更新服务"
        echo "  cleanup   - 清理部署环境"
        echo
        echo "示例："
        echo "  $0 install      # 初始化安装"
        echo "  $0 start        # 启动服务"
        echo "  $0 logs app     # 查看应用日志"
        echo "  $0 health       # 健康检查"
        exit 1
        ;;
esac

exit 0