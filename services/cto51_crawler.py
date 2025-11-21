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
51CTO开源技术社区爬虫
爬取地址: https://ost.51cto.com/postlist
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import logging
import time
import random
from typing import List, Dict, Optional, Callable
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class Cto51Crawler:
    """51CTO开源技术社区爬虫"""

    def __init__(self, headless: bool = True):
        """
        初始化爬虫

        Args:
            headless: 是否使用无头模式
        """
        self.base_url = "https://ost.51cto.com/postlist"
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None

        # 用户代理池，模拟真实浏览器
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

    def _init_driver(self) -> webdriver.Chrome:
        """初始化Selenium WebDriver"""
        try:
            chrome_options = Options()

            # 使用无头模式
            if self.headless:
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')

            # 反爬虫策略
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # 随机User-Agent
            user_agent = random.choice(self.user_agents)
            chrome_options.add_argument(f'user-agent={user_agent}')

            # 窗口大小
            chrome_options.add_argument('--window-size=1920,1080')

            # 其他优化选项
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-popup-blocking')

            # 创建driver
            driver = webdriver.Chrome(options=chrome_options)

            # 设置隐式等待
            driver.implicitly_wait(10)

            # 执行CDP命令隐藏webdriver特征
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['zh-CN', 'zh', 'en']
                    });
                '''
            })

            logger.info("✅ Selenium WebDriver初始化成功")
            return driver

        except Exception as e:
            logger.error(f"❌ 初始化WebDriver失败: {e}")
            raise

    def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """随机延迟，模拟人类行为"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def _human_like_scroll(self, driver: webdriver.Chrome):
        """模拟人类滚动行为"""
        try:
            # 随机滚动距离
            scroll_distance = random.randint(300, 800)
            driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
            self._random_delay(0.5, 1.5)

            # 有时候向上滚一点
            if random.random() > 0.7:
                driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)});")
                self._random_delay(0.3, 0.8)
        except Exception as e:
            logger.warning(f"⚠️ 模拟滚动失败: {e}")

    def _generate_article_id(self, url: str) -> str:
        """根据URL生成唯一ID"""
        return hashlib.md5(url.encode()).hexdigest()[:16]

    def _parse_article_detail(self, driver: webdriver.Chrome, article_url: str) -> Optional[Dict]:
        """
        解析文章详情页

        Args:
            driver: WebDriver实例
            article_url: 文章URL

        Returns:
            文章详情字典
        """
        try:
            # 访问文章页面
            driver.get(article_url)
            self._random_delay(2, 4)

            # 等待页面加载
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # 模拟人类浏览行为
            self._human_like_scroll(driver)

            # 获取页面HTML
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # 提取标题
            title = ""
            title_selectors = [
                'h1.article-title',
                'h1.post-title',
                '.article-header h1',
                'h1'
            ]
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break

            if not title:
                logger.warning(f"⚠️ 未找到标题: {article_url}")
                return None

            # 提取日期
            date = ""
            date_selectors = [
                '.post-meta time',
                '.article-meta time',
                'time',
                '.publish-time',
                '.date'
            ]
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date = date_elem.get_text(strip=True)
                    # 尝试从datetime属性获取
                    if not date and date_elem.get('datetime'):
                        date = date_elem['datetime']
                    break

            # 如果没有日期，使用当前时间
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")

            # 提取文章内容
            content_blocks = []
            content_selectors = [
                '.article-content',
                '.post-content',
                '.content',
                'article'
            ]

            content_container = None
            for selector in content_selectors:
                content_container = soup.select_one(selector)
                if content_container:
                    break

            if content_container:
                # 遍历内容元素
                for element in content_container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'pre', 'code', 'video']):
                    if element.name == 'img':
                        # 图片元素
                        img_src = element.get('src') or element.get('data-src')
                        if img_src:
                            # 补全相对URL
                            if img_src.startswith('//'):
                                img_src = 'https:' + img_src
                            elif img_src.startswith('/'):
                                img_src = 'https://ost.51cto.com' + img_src
                            content_blocks.append({
                                "type": "image",
                                "value": img_src
                            })
                    elif element.name == 'video':
                        # 视频元素
                        video_src = element.get('src')
                        if video_src:
                            if video_src.startswith('//'):
                                video_src = 'https:' + video_src
                            elif video_src.startswith('/'):
                                video_src = 'https://ost.51cto.com' + video_src
                            content_blocks.append({
                                "type": "video",
                                "value": video_src
                            })
                    elif element.name in ['pre', 'code']:
                        # 代码块
                        code_text = element.get_text(strip=True)
                        if code_text:
                            content_blocks.append({
                                "type": "code",
                                "value": code_text
                            })
                    else:
                        # 文本元素
                        text = element.get_text(strip=True)
                        if text:
                            content_blocks.append({
                                "type": "text",
                                "value": text
                            })

            # 如果没有解析到内容块，尝试获取整体文本
            if not content_blocks and content_container:
                full_text = content_container.get_text(strip=True)
                if full_text:
                    # 按段落分割
                    paragraphs = [p.strip() for p in full_text.split('\n') if p.strip()]
                    for para in paragraphs[:10]:  # 最多取前10段
                        content_blocks.append({
                            "type": "text",
                            "value": para
                        })

            # 提取摘要（取前3个文本块）
            summary = ""
            text_blocks = [block['value'] for block in content_blocks if block['type'] == 'text']
            if text_blocks:
                summary = ' '.join(text_blocks[:3])[:200] + '...'

            # 构建文章数据
            article_data = {
                "id": self._generate_article_id(article_url),
                "title": title,
                "date": date,
                "url": article_url,
                "content": content_blocks if content_blocks else [{"type": "text", "value": "暂无内容"}],
                "category": "开源技术",
                "summary": summary or title[:100],
                "source": "51CTO开源社区",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            logger.info(f"✅ 成功解析文章: {title}")
            return article_data

        except TimeoutException:
            logger.error(f"❌ 页面加载超时: {article_url}")
            return None
        except Exception as e:
            logger.error(f"❌ 解析文章详情失败: {e}", exc_info=True)
            return None

    def crawl_articles(
        self,
        max_pages: int = 3,
        batch_callback: Optional[Callable[[List[Dict]], None]] = None
    ) -> List[Dict]:
        """
        爬取51CTO开源社区文章

        Args:
            max_pages: 最大爬取页数
            batch_callback: 批量回调函数，用于分批处理数据

        Returns:
            文章列表
        """
        all_articles = []

        try:
            # 初始化driver
            self.driver = self._init_driver()

            logger.info(f"🚀 开始爬取51CTO开源社区，目标页数: {max_pages}")

            # 访问首页
            self.driver.get(self.base_url)
            self._random_delay(3, 5)

            current_page = 1

            while current_page <= max_pages:
                try:
                    logger.info(f"📄 正在爬取第 {current_page} 页")

                    # 等待文章列表加载
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.infinite-list"))
                    )

                    # 模拟人类浏览
                    self._human_like_scroll(self.driver)
                    self._random_delay(2, 4)

                    # 获取当前页面的文章列表
                    try:
                        article_elements = self.driver.find_elements(
                            By.CSS_SELECTOR,
                            "ul.infinite-list li.infinite-list-item"
                        )

                        logger.info(f"📋 找到 {len(article_elements)} 篇文章")

                        page_articles = []

                        for idx, article_elem in enumerate(article_elements, 1):
                            try:
                                # 查找文章链接
                                link_elem = article_elem.find_element(By.CSS_SELECTOR, "a")
                                article_url = link_elem.get_attribute('href')

                                if not article_url:
                                    continue

                                # 补全URL
                                if article_url.startswith('/'):
                                    article_url = 'https://ost.51cto.com' + article_url

                                logger.info(f"  📖 [{idx}/{len(article_elements)}] 正在解析: {article_url}")

                                # 解析文章详情
                                article_data = self._parse_article_detail(self.driver, article_url)

                                if article_data:
                                    page_articles.append(article_data)
                                    all_articles.append(article_data)

                                # 返回列表页
                                self.driver.back()
                                self._random_delay(2, 4)

                                # 重新等待列表加载
                                WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.infinite-list"))
                                )

                            except (NoSuchElementException, StaleElementReferenceException) as e:
                                logger.warning(f"⚠️ 跳过无效文章元素: {e}")
                                continue
                            except Exception as e:
                                logger.error(f"❌ 处理文章时出错: {e}")
                                continue

                        # 批量回调
                        if batch_callback and page_articles:
                            try:
                                batch_callback(page_articles)
                                logger.info(f"✅ 第{current_page}页数据已通过回调处理")
                            except Exception as e:
                                logger.error(f"❌ 批量回调失败: {e}")

                        # 查找并点击下一页按钮
                        if current_page < max_pages:
                            try:
                                # 滚动到页面底部
                                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                self._random_delay(1, 2)

                                # 查找下一页按钮
                                next_button_selectors = [
                                    "button.btn-next",
                                    ".pagination .next",
                                    "a.next",
                                    "button:contains('下一页')",
                                    ".el-pagination button.btn-next"
                                ]

                                next_button = None
                                for selector in next_button_selectors:
                                    try:
                                        next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                                        if next_button and next_button.is_enabled():
                                            break
                                    except NoSuchElementException:
                                        continue

                                if next_button and next_button.is_enabled():
                                    logger.info("🔄 点击下一页按钮")

                                    # 滚动到按钮位置
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                                    self._random_delay(0.5, 1)

                                    # 点击
                                    next_button.click()
                                    self._random_delay(3, 5)

                                    current_page += 1
                                else:
                                    logger.info("ℹ️ 没有更多页面了")
                                    break

                            except Exception as e:
                                logger.warning(f"⚠️ 翻页失败: {e}")
                                break
                        else:
                            break

                    except TimeoutException:
                        logger.error("❌ 等待文章列表超时")
                        break

                except Exception as e:
                    logger.error(f"❌ 处理第{current_page}页时出错: {e}")
                    break

            logger.info(f"✅ 爬取完成，共获取 {len(all_articles)} 篇文章")
            return all_articles

        except Exception as e:
            logger.error(f"❌ 爬虫执行失败: {e}", exc_info=True)
            return all_articles

        finally:
            # 关闭浏览器
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("🔒 浏览器已关闭")
                except Exception as e:
                    logger.error(f"❌ 关闭浏览器失败: {e}")


def main():
    """测试函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    crawler = Cto51Crawler(headless=True)
    articles = crawler.crawl_articles(max_pages=2)

    print(f"\n总共爬取 {len(articles)} 篇文章")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']} - {article['url']}")


if __name__ == "__main__":
    main()
