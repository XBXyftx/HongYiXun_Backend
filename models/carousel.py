# 华为轮播图数据模型
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ServiceStatus(str, Enum):
    """服务状态枚举"""
    READY = "ready"
    PREPARING = "preparing"
    ERROR = "error"


class CarouselSlide(BaseModel):
    """轮播图滑块模型"""
    slide_number: int = Field(..., description="轮播图序号", ge=1)
    image_url: Optional[str] = Field(None, description="轮播图图片URL")
    title: Optional[str] = Field(None, description="轮播图标题")
    subtitle: Optional[str] = Field(None, description="轮播图副标题")
    description: Optional[str] = Field(None, description="轮播图描述")
    all_text: List[str] = Field(default_factory=list, description="轮播图所有文本内容")
    raw_text_content: Optional[str] = Field(None, description="原始文本内容")
    crawl_timestamp: float = Field(..., description="爬取时间戳")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CarouselDataResponse(BaseModel):
    """轮播图数据响应"""
    slides: List[CarouselSlide] = Field(..., description="轮播图数据列表")
    total_count: int = Field(..., description="总数量")
    with_images: int = Field(..., description="包含图片的数量")
    with_text: int = Field(..., description="包含文本的数量")
    timestamp: datetime = Field(..., description="响应时间戳")


class CarouselCacheInfo(BaseModel):
    """轮播图缓存信息"""
    status: ServiceStatus = Field(..., description="缓存状态")
    cache_count: int = Field(..., description="缓存项目数量")
    last_updated: Optional[datetime] = Field(None, description="最后更新时间")
    created_at: datetime = Field(..., description="创建时间")
    update_count: int = Field(..., description="更新次数")
    error_message: Optional[str] = Field(None, description="错误信息")
    is_first_load: bool = Field(..., description="是否首次加载")
    uptime_seconds: float = Field(..., description="运行时间（秒）")


class CarouselDetailedInfo(BaseModel):
    """轮播图缓存详细信息"""
    basic_info: dict = Field(..., description="基本信息")
    timestamps: dict = Field(..., description="时间戳信息")
    statistics: dict = Field(..., description="统计信息")


class CarouselPageParams(BaseModel):
    """分页参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class CarouselPageResponse(BaseModel):
    """分页响应"""
    items: List[CarouselSlide] = Field(..., description="数据项")
    pagination: dict = Field(..., description="分页信息")


class CarouselStatsResponse(BaseModel):
    """轮播图统计响应"""
    total_slides: int = Field(..., description="总轮播图数量")
    slides_with_images: int = Field(..., description="包含图片的轮播图数量")
    slides_with_text: int = Field(..., description="包含文本的轮播图数量")
    slides_with_both: int = Field(..., description="同时包含图片和文本的数量")
    data_quality_score: float = Field(..., description="数据质量分数")
    cache_age_hours: Optional[float] = Field(None, description="缓存年龄（小时）")
    last_crawl_duration: Optional[float] = Field(None, description="上次爬取耗时")


class ManualCrawlResponse(BaseModel):
    """手动爬取响应"""
    message: str = Field(..., description="响应消息")
    status: str = Field(..., description="任务状态")


class SchedulerStatusResponse(BaseModel):
    """调度器状态响应"""
    state: str = Field(..., description="调度器状态")
    job_count: int = Field(..., description="任务数量")
    jobs: List[dict] = Field(default_factory=list, description="任务列表")


class JobStatusResponse(BaseModel):
    """任务状态响应"""
    job_id: str = Field(..., description="任务ID")
    job_name: str = Field(..., description="任务名称")
    status: str = Field(..., description="任务状态")
    next_run: Optional[str] = Field(None, description="下次运行时间")
    trigger: str = Field(..., description="触发器类型")


class JobActionResponse(BaseModel):
    """任务操作响应"""
    message: str = Field(..., description="操作消息")
    job_id: str = Field(..., description="任务ID")
    action: str = Field(..., description="操作类型")


class CarouselExportResponse(BaseModel):
    """轮播图导出响应"""
    message: str = Field(..., description="导出消息")
    file_path: str = Field(..., description="导出文件路径")
    export_time: datetime = Field(..., description="导出时间")
    data_count: int = Field(..., description="导出数据数量")


class CarouselImportResponse(BaseModel):
    """轮播图导入响应"""
    message: str = Field(..., description="导入消息")
    imported_count: int = Field(..., description="导入数据数量")
    skipped_count: int = Field(..., description="跳过数据数量")
    import_time: datetime = Field(..., description="导入时间")


class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str = Field(..., description="错误详情")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: Optional[datetime] = Field(None, description="错误时间戳")