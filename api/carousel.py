from fastapi import APIRouter, HTTPException, Query, Path, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
import logging
import os
import asyncio
from datetime import datetime

from core.cache import get_cache_manager
from core.scheduler import get_scheduler
from core.config import settings
from services.carousel_service import get_carousel_service
from models.carousel import (
    CarouselDataResponse,
    CarouselSlide,
    CarouselCacheInfo,
    CarouselDetailedInfo,
    CarouselStatsResponse,
    ManualCrawlResponse,
    SchedulerStatusResponse,
    JobStatusResponse,
    JobActionResponse,
    CarouselExportResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/api/carousel",
    tags=["华为轮播图API"],
    responses={
        404: {"model": ErrorResponse, "description": "资源未找到"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"}
    }
)


@router.get(
    "/slides",
    response_model=CarouselDataResponse,
    summary="获取华为轮播图数据",
    description="获取当前缓存的华为轮播图数据，支持分页和过滤"
)
async def get_carousel_slides(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    with_images_only: bool = Query(False, description="仅显示包含图片的轮播图"),
    with_text_only: bool = Query(False, description="仅显示包含文本的轮播图")
):
    """
    获取华为轮播图数据

    - **page**: 页码，从1开始
    - **page_size**: 每页显示数量，最大100
    - **with_images_only**: 是否仅返回包含图片的轮播图
    - **with_text_only**: 是否仅返回包含文本的轮播图
    """
    try:
        cache_manager = get_cache_manager()
        carousel_cache = cache_manager.get_cache("carousel")

        if not carousel_cache:
            raise HTTPException(
                status_code=503,
                detail="轮播图缓存服务不可用"
            )

        cache_status = carousel_cache.get_status()

        # 检查缓存状态
        if cache_status["status"] == "error":
            raise HTTPException(
                status_code=503,
                detail=f"缓存服务异常: {cache_status.get('error_message', '未知错误')}"
            )

        # 获取缓存数据
        all_slides = carousel_cache.get_data()

        # 应用过滤条件
        filtered_slides = []
        for slide_data in all_slides:
            # 检查图片条件
            has_image = bool(slide_data.get("image_url"))
            if with_images_only and not has_image:
                continue

            # 检查文本条件
            has_text = bool(
                slide_data.get("title") or
                slide_data.get("subtitle") or
                slide_data.get("description") or
                slide_data.get("all_text")
            )
            if with_text_only and not has_text:
                continue

            # 转换为响应模型
            slide = CarouselSlide(**slide_data)
            filtered_slides.append(slide)

        # 统计信息
        total_count = len(filtered_slides)
        with_images = sum(1 for slide in filtered_slides if slide.image_url)
        with_text = sum(1 for slide in filtered_slides if slide.title or slide.subtitle or slide.description)

        # 分页处理
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_slides = filtered_slides[start_index:end_index]

        return CarouselDataResponse(
            slides=paginated_slides,
            total_count=total_count,
            with_images=with_images,
            with_text=with_text,
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取轮播图数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="获取轮播图数据失败"
        )


@router.get(
    "/slides/{slide_id}",
    response_model=CarouselSlide,
    summary="获取单个轮播图",
    description="根据滑块ID获取单个轮播图详细信息"
)
async def get_carousel_slide(
    slide_id: int = Path(..., ge=1, description="轮播图滑块ID")
):
    """
    获取单个轮播图详细信息

    - **slide_id**: 轮播图滑块ID，从1开始
    """
    try:
        cache_manager = get_cache_manager()
        carousel_cache = cache_manager.get_cache("carousel")

        if not carousel_cache:
            raise HTTPException(
                status_code=503,
                detail="轮播图缓存服务不可用"
            )

        cache_status = carousel_cache.get_status()

        # 检查缓存状态
        if cache_status["status"] == "error":
            raise HTTPException(
                status_code=503,
                detail=f"缓存服务异常: {cache_status.get('error_message', '未知错误')}"
            )

        # 获取缓存数据
        all_slides = carousel_cache.get_data()

        # 查找指定ID的滑块
        target_slide = None
        for slide_data in all_slides:
            if slide_data.get("slide_number") == slide_id:
                target_slide = CarouselSlide(**slide_data)
                break

        if not target_slide:
            raise HTTPException(
                status_code=404,
                detail=f"轮播图滑块 {slide_id} 不存在"
            )

        return target_slide

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取轮播图滑块 {slide_id} 失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="获取轮播图滑块失败"
        )


@router.get(
    "/cache/status",
    response_model=CarouselCacheInfo,
    summary="获取轮播图缓存状态",
    description="获取轮播图缓存的当前状态信息"
)
async def get_cache_status():
    """
    获取轮播图缓存状态信息
    """
    try:
        cache_manager = get_cache_manager()
        carousel_cache = cache_manager.get_cache("carousel")

        if not carousel_cache:
            raise HTTPException(
                status_code=503,
                detail="轮播图缓存服务不可用"
            )

        cache_status = carousel_cache.get_status()
        from models.carousel import ServiceStatus

        return CarouselCacheInfo(
            status=ServiceStatus(cache_status["status"]),
            cache_count=cache_status["cache_count"],
            last_updated=datetime.fromisoformat(cache_status["last_updated"]) if cache_status.get("last_updated") else None,
            created_at=datetime.fromisoformat(cache_status["created_at"]),
            update_count=cache_status.get("update_count", 0),
            error_message=cache_status.get("error_message"),
            is_first_load=cache_status.get("is_first_load", True),
            uptime_seconds=cache_status.get("uptime_seconds", 0.0)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取缓存状态失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="获取缓存状态失败"
        )


@router.get(
    "/stats",
    response_model=CarouselStatsResponse,
    summary="获取轮播图统计信息",
    description="获取轮播图数据的统计信息"
)
async def get_carousel_stats():
    """
    获取轮播图数据统计信息
    """
    try:
        cache_manager = get_cache_manager()
        carousel_cache = cache_manager.get_cache("carousel")

        if not carousel_cache:
            raise HTTPException(
                status_code=503,
                detail="轮播图缓存服务不可用"
            )

        cache_info = carousel_cache.get_cache_info()

        basic_info = cache_info["basic_info"]
        timestamps = cache_info["timestamps"]

        # 计算缓存年龄
        cache_age_hours = None
        if timestamps.get("age_seconds"):
            cache_age_hours = timestamps["age_seconds"] / 3600

        # 计算同时包含图片和文本的数量
        slides_with_both = basic_info["valid_items"] - (
            (basic_info["total_items"] - basic_info["items_with_images"]) +
            (basic_info["total_items"] - basic_info["items_with_text"])
        )
        slides_with_both = max(0, slides_with_both)  # 确保非负

        return CarouselStatsResponse(
            total_slides=basic_info["total_items"],
            slides_with_images=basic_info["items_with_images"],
            slides_with_text=basic_info["items_with_text"],
            slides_with_both=slides_with_both,
            data_quality_score=basic_info["data_quality_score"],
            cache_age_hours=cache_age_hours,
            last_crawl_duration=None  # 这里可以添加爬取耗时统计
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="获取统计信息失败"
        )


@router.post(
    "/crawl/manual",
    response_model=ManualCrawlResponse,
    summary="手动触发轮播图爬取",
    description="手动触发华为轮播图数据爬取任务"
)
async def manual_crawl(background_tasks: BackgroundTasks):
    """
    手动触发华为轮播图数据爬取

    这个端点会启动一个后台任务来爬取最新的轮播图数据
    """
    try:
        scheduler = get_scheduler()
        result = await scheduler.manual_crawl("carousel")

        return ManualCrawlResponse(
            message=result.get("message", "手动爬取任务已提交"),
            status=result.get("status", "unknown")
        )

    except Exception as e:
        logger.error(f"手动触发爬取失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="手动触发爬取失败"
        )


@router.get(
    "/crawler/info",
    summary="获取轮播图爬虫信息",
    description="获取轮播图爬虫配置和信息"
)
async def get_crawler_info():
    """
    获取轮播图爬虫配置和信息
    """
    try:
        carousel_service = get_carousel_service()
        crawler_info = carousel_service.get_crawler_info()

        return crawler_info

    except Exception as e:
        logger.error(f"获取爬虫信息失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="获取爬虫信息失败"
        )


@router.get(
    "/crawler/test",
    summary="测试轮播图爬虫连接",
    description="测试轮播图爬虫的连接性和可用性"
)
async def test_crawler_connectivity():
    """
    测试轮播图爬虫连接性
    """
    try:
        carousel_service = get_carousel_service()
        test_result = await carousel_service.test_crawler_connectivity()

        return test_result

    except Exception as e:
        logger.error(f"测试爬虫连接失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="测试爬虫连接失败"
        )


@router.post(
    "/cache/export",
    response_model=CarouselExportResponse,
    summary="导出轮播图缓存数据",
    description="将当前轮播图缓存数据导出到文件"
)
async def export_cache_data():
    """
    导出轮播图缓存数据到文件
    """
    try:
        cache_manager = get_cache_manager()
        carousel_cache = cache_manager.get_cache("carousel")

        if not carousel_cache:
            raise HTTPException(
                status_code=503,
                detail="轮播图缓存服务不可用"
            )

        cache_info = carousel_cache.get_status()

        # 生成导出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = f"carousel_export_{timestamp}.json"
        export_path = os.path.join(os.getcwd(), "data", export_file)

        # 确保数据目录存在
        os.makedirs(os.path.dirname(export_path), exist_ok=True)

        # 导出数据
        success = carousel_cache.export_data(export_path)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="导出缓存数据失败"
            )

        return CarouselExportResponse(
            message=f"轮播图缓存数据已成功导出到 {export_file}",
            file_path=export_path,
            export_time=datetime.now(),
            data_count=cache_info["cache_count"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出缓存数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="导出缓存数据失败"
        )