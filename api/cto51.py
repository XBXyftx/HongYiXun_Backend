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

"""
51CTO开源社区API路由
提供文章获取、搜索、分页等功能
"""

from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import Optional, List
import logging
from datetime import datetime
import threading

from services.cto51_crawler import Cto51Crawler
from models.cto51 import Cto51Article, Cto51Response, Cto51ContentBlock

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cto51", tags=["51cto"])

# 内存缓存
_cache_lock = threading.RLock()
_article_cache: List[Cto51Article] = []
_cache_status = {
    "last_update": None,
    "is_updating": False,
    "total_articles": 0,
    "error": None
}


def _update_cache_from_dict_list(articles_dict_list: List[dict]):
    """从字典列表更新缓存"""
    global _article_cache, _cache_status

    with _cache_lock:
        try:
            # 转换为Pydantic模型
            new_articles = []
            for article_dict in articles_dict_list:
                try:
                    # 转换content blocks
                    content_blocks = [
                        Cto51ContentBlock(**block) for block in article_dict.get('content', [])
                    ]
                    article_dict['content'] = content_blocks

                    # 创建Article对象
                    article = Cto51Article(**article_dict)
                    new_articles.append(article)
                except Exception as e:
                    logger.error(f"❌ 转换文章失败: {e}")
                    continue

            # 更新缓存（去重）
            existing_ids = {article.id for article in _article_cache}
            for article in new_articles:
                if article.id not in existing_ids:
                    _article_cache.append(article)
                    existing_ids.add(article.id)

            # 按日期排序（最新的在前）
            _article_cache.sort(key=lambda x: x.created_at or datetime.now(), reverse=True)

            # 更新状态
            _cache_status["total_articles"] = len(_article_cache)
            _cache_status["last_update"] = datetime.now().isoformat()
            _cache_status["error"] = None

            logger.info(f"✅ 缓存已更新，当前共有 {len(_article_cache)} 篇文章")

        except Exception as e:
            logger.error(f"❌ 更新缓存失败: {e}")
            _cache_status["error"] = str(e)


def _crawl_and_update_cache(max_pages: int = 3):
    """后台爬取并更新缓存"""
    global _cache_status

    try:
        _cache_status["is_updating"] = True
        logger.info(f"🚀 开始后台爬取51CTO文章，最大页数: {max_pages}")

        # 创建爬虫
        crawler = Cto51Crawler(headless=True)

        # 定义批量回调
        def batch_callback(articles_batch: List[dict]):
            _update_cache_from_dict_list(articles_batch)

        # 执行爬取
        articles = crawler.crawl_articles(max_pages=max_pages, batch_callback=batch_callback)

        logger.info(f"✅ 后台爬取完成，共获取 {len(articles)} 篇文章")

    except Exception as e:
        logger.error(f"❌ 后台爬取失败: {e}")
        _cache_status["error"] = str(e)

    finally:
        _cache_status["is_updating"] = False


@router.get("/", response_model=Cto51Response)
async def get_cto51_articles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    all: bool = Query(False, description="是否返回全部文章不分页")
):
    """
    获取51CTO文章列表

    参数说明：
    - page: 页码（当all=True时忽略）
    - page_size: 每页数量（当all=True时忽略）
    - search: 搜索关键词（在标题和摘要中搜索）
    - all: 是否返回全部文章不分页
    """
    try:
        with _cache_lock:
            articles = _article_cache.copy()

        # 搜索过滤
        if search:
            search_lower = search.lower()
            articles = [
                article for article in articles
                if (search_lower in article.title.lower()) or
                   (article.summary and search_lower in article.summary.lower())
            ]

        total = len(articles)

        # 分页处理
        if all:
            # 返回所有数据
            return Cto51Response(
                articles=articles,
                total=total,
                page=1,
                page_size=total,
                has_next=False,
                has_prev=False
            )
        else:
            # 正常分页
            start = (page - 1) * page_size
            end = start + page_size
            paginated_articles = articles[start:end]

            return Cto51Response(
                articles=paginated_articles,
                total=total,
                page=page,
                page_size=page_size,
                has_next=end < total,
                has_prev=page > 1
            )

    except Exception as e:
        logger.error(f"❌ 获取文章列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取文章列表失败")


@router.get("/{article_id}", response_model=Cto51Article)
async def get_cto51_article_detail(article_id: str):
    """
    获取单篇文章详情

    参数：
    - article_id: 文章唯一标识符
    """
    try:
        with _cache_lock:
            for article in _article_cache:
                if article.id == article_id:
                    return article

        # 未找到文章
        raise HTTPException(status_code=404, detail="文章不存在")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取文章详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取文章详情失败")


@router.post("/crawl")
async def crawl_cto51_articles(
    background_tasks: BackgroundTasks,
    max_pages: int = Query(3, ge=1, le=10, description="最大爬取页数")
):
    """
    手动触发爬取51CTO文章

    参数：
    - max_pages: 最大爬取页数（1-10）
    """
    try:
        if _cache_status["is_updating"]:
            raise HTTPException(status_code=409, detail="爬取任务正在进行中，请稍后再试")

        # 添加后台任务
        background_tasks.add_task(_crawl_and_update_cache, max_pages)

        return {
            "message": f"爬取任务已启动，将爬取最多 {max_pages} 页",
            "max_pages": max_pages,
            "timestamp": datetime.now().isoformat(),
            "note": "爬取任务在后台执行，请稍后查看缓存状态"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 启动爬取任务失败: {e}")
        raise HTTPException(status_code=500, detail="启动爬取任务失败")


@router.get("/status/info")
async def get_cto51_status():
    """
    获取51CTO服务状态信息
    """
    try:
        with _cache_lock:
            status = _cache_status.copy()

        return {
            "service": "51CTO开源社区",
            "cache_status": status,
            "endpoints": {
                "list": "/api/cto51/",
                "detail": "/api/cto51/{article_id}",
                "crawl": "/api/cto51/crawl",
                "status": "/api/cto51/status/info"
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 获取服务状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取服务状态失败")


@router.post("/cache/clear")
async def clear_cto51_cache():
    """
    清空缓存（谨慎使用）
    """
    try:
        global _article_cache, _cache_status

        with _cache_lock:
            _article_cache.clear()
            _cache_status["total_articles"] = 0
            _cache_status["last_update"] = None

        return {
            "message": "缓存已清空",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail="清空缓存失败")
