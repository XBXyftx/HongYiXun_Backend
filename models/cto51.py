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
51CTO开源社区数据模型
与前端 51cto/NewsListModules.ets 格式完全一致
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    """内容类型枚举，对应前端 CONTENT_TYPE_ENUM"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CODE = "code"


class Cto51ContentBlock(BaseModel):
    """
    新闻内容块
    对应前端 NewsContentBlock 接口
    """
    type: ContentType = Field(..., description="内容类型")
    value: str = Field(..., description="内容值")


class Cto51Article(BaseModel):
    """
    51CTO文章模型
    对应前端 NewsArticle 类
    """
    id: Optional[str] = Field(None, description="文章唯一标识符")
    title: str = Field(..., description="文章标题")
    date: str = Field(..., description="发布日期")
    url: str = Field(..., description="文章原链接")
    content: List[Cto51ContentBlock] = Field(..., description="文章内容块数组")
    category: Optional[str] = Field(None, description="文章分类")
    summary: Optional[str] = Field(None, description="文章摘要")
    source: Optional[str] = Field(None, description="新闻来源")
    created_at: Optional[datetime] = Field(None, description="创建时间（ISO 8601格式）")
    updated_at: Optional[datetime] = Field(None, description="更新时间（ISO 8601格式）")


class Cto51Response(BaseModel):
    """
    51CTO文章响应模型
    对应前端 NewsResponse 接口
    """
    articles: List[Cto51Article] = Field(..., description="文章数组")
    total: int = Field(..., description="总文章数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页文章数量")
    has_next: bool = Field(False, description="是否有下一页")
    has_prev: bool = Field(False, description="是否有上一页")
