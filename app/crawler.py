from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import random
import logging
import os
import openpyxl
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CNKICrawler:
    def __init__(self, username=None, password=None):
        self.setup_driver()
        self.base_url = 'https://kns.cnki.net/kns8/defaultresult/index'
        self.pdf_base_url = 'https://kns.cnki.net/KCMS/detail/detail.aspx'
        self.login_url = 'https://login.cnki.net/login/'
        self.username = username
        self.password = password
        self.screenshot_files = []  # 用于存储截图文件路径

    def setup_driver(self):
        """设置Chrome浏览器"""
        chrome_options = Options()
        # 添加一些配置来模拟真实浏览器
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')

        # 添加以下选项来禁用WebGL警告
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-webgl')
        chrome_options.add_argument('--disable-gpu-sandbox')
        chrome_options.add_argument('--disable-accelerated-2d-canvas')
        chrome_options.add_argument('--disable-accelerated-jpeg-decoding')
        chrome_options.add_argument('--disable-accelerated-mjpeg-decode')
        chrome_options.add_argument('--disable-accelerated-video-decode')

        # 添加以下选项来抑制USB相关警告
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--disable-site-isolation-trials')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=NetworkService')
        chrome_options.add_argument('--disable-features=NetworkServiceInProcess')
        chrome_options.add_argument('--disable-features=NetworkServiceInProcess2')
        chrome_options.add_argument('--disable-features=NetworkServiceInProcess3')

        # 添加以下选项来抑制视频捕获相关警告
        chrome_options.add_argument('--disable-features=WebRTC')
        chrome_options.add_argument('--disable-features=WebRTCPipeWireCapturer')
        chrome_options.add_argument('--disable-features=WebRTC-HWDecoding')
        chrome_options.add_argument('--disable-features=WebRTC-HWEncoding')
        chrome_options.add_argument('--disable-features=WebRTC-HWDecoding-H264')
        chrome_options.add_argument('--disable-features=WebRTC-HWEncoding-H264')
        chrome_options.add_argument('--disable-features=WebRTC-HWDecoding-VP8')
        chrome_options.add_argument('--disable-features=WebRTC-HWEncoding-VP8')
        chrome_options.add_argument('--disable-features=WebRTC-HWDecoding-VP9')
        chrome_options.add_argument('--disable-features=WebRTC-HWEncoding-VP9')
        # 设置用户代理
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # 初始化WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)

        # 设置页面加载超时
        self.driver.set_page_load_timeout(30)
        self.wait = WebDriverWait(self.driver, 10)

    def save_screenshot(self, filename):
        """保存截图并记录文件路径"""
        try:
            self.driver.save_screenshot(filename)
            self.screenshot_files.append(filename)
            logger.info(f"已保存截图: {filename}")
        except Exception as e:
            logger.error(f"保存截图失败: {str(e)}")

    def cleanup_screenshots(self):
        """清理所有截图文件"""
        for file in self.screenshot_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    logger.info(f"已删除截图: {file}")
            except Exception as e:
                logger.error(f"删除截图失败 {file}: {str(e)}")
        self.screenshot_files = []

    def login(self):
        """人工登录CNKI"""
        try:
            logger.info("开始人工登录流程...")
            self.driver.get(self.login_url)
            self.random_sleep(2, 3)

            # 保存当前页面截图以便调试
            self.save_screenshot("before_login.png")
            logger.info("已保存登录前页面截图")
            logger.info(f"当前页面标题: {self.driver.title}")
            logger.info(f"当前页面URL: {self.driver.current_url}")

            # 等待用户手动登录
            logger.info("请在浏览器中手动完成登录...")
            logger.info("登录成功后，程序将自动继续...")

            # 等待登录成功
            try:
                # 增加等待时间，因为用户需要时间手动登录
                self.wait = WebDriverWait(self.driver, 300)  # 设置5分钟超时

                # 定期检查页面状态
                start_time = time.time()
                while time.time() - start_time < 300:  # 5分钟超时
                    try:
                        # 检查当前URL
                        current_url = self.driver.current_url
                        logger.info(f"当前URL: {current_url}")

                        # 检查页面标题
                        current_title = self.driver.title
                        logger.info(f"当前标题: {current_title}")

                        # 如果URL不包含login，可能已经登录成功
                        if "login" not in current_url.lower():
                            logger.info("检测到URL变化，可能已登录成功")
                            break

                        # 尝试查找登录成功后的元素
                        login_success_selectors = [
                            "span.user-name",
                            "div.user-info",
                            "a.user-avatar",
                            "div.user-center",
                            "a.logout",
                            "span.username",
                            "div.user-menu",
                            "a[href*='user']",
                            "div[class*='user']",
                            "span[class*='user']"
                        ]

                        for selector in login_success_selectors:
                            try:
                                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if element.is_displayed():
                                    logger.info(f"检测到登录成功！找到元素: {selector}")
                                    break
                            except:
                                continue

                        # 保存当前页面截图
                        self.save_screenshot(f"check_status_{int(time.time())}.png")

                        # 等待一段时间后再次检查
                        time.sleep(5)

                    except Exception as e:
                        logger.error(f"检查状态时出错: {str(e)}")
                        time.sleep(5)
                        continue

                # 跳转到搜索页面
                logger.info("正在跳转到搜索页面...")
                self.driver.get(self.base_url)
                self.random_sleep(2, 3)

                # 等待搜索页面加载完成
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input#txt_search, div.search-box"))
                    )
                    logger.info("搜索页面加载成功")
                except TimeoutException:
                    logger.error("搜索页面加载失败")
                    self.save_screenshot("search_page_error.png")
                    return False

                # 恢复默认等待时间
                self.wait = WebDriverWait(self.driver, 10)
                return True

            except TimeoutException:
                logger.error("登录超时，请检查是否已成功登录")
                self.save_screenshot("login_timeout_error.png")
                return False

        except Exception as e:
            logger.error(f"登录过程中出错: {str(e)}")
            # 保存当前页面截图以便调试
            try:
                screenshot_path = "login_error.png"
                self.save_screenshot(screenshot_path)
                logger.info(f"已保存错误截图到: {screenshot_path}")
            except:
                logger.error("无法保存错误截图")
            return False

    def random_sleep(self, min_seconds=2, max_seconds=5):
        """随机等待一段时间"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def search_papers(self, keyword, page=1):
        """搜索论文"""
        try:
            # 访问搜索页面
            self.driver.get(self.base_url)
            self.random_sleep(3, 5)  # 增加等待时间

            # 输入搜索关键词
            search_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "txt_search"))
            )
            search_input.clear()
            search_input.send_keys(keyword)
            self.random_sleep(1, 2)

            # 点击搜索按钮
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "search-btn"))
            )
            search_button.click()
            self.random_sleep(3, 5)  # 增加等待时间

            # 等待搜索结果加载
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "result-table-list"))
            )

            # 保存当前页面截图
            self.save_screenshot("before_degree_thesis.png")

            # 点击"学位论文"分类
            try:
                logger.info("正在点击学位论文分类...")

                # 使用精确的XPath定位
                try:
                    # 找到带有haschild cur类的li元素
                    degree_thesis_li = self.wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//li[contains(@class, 'haschild') and contains(@class, 'cur')]"))
                    )

                    # 找到其中的a标签
                    degree_thesis_link = degree_thesis_li.find_element(By.XPATH, ".//a[.//span[text()='学位论文']]")

                    # 使用JavaScript点击，避免元素被遮挡
                    self.driver.execute_script("arguments[0].click();", degree_thesis_link)
                    logger.info("成功点击学位论文分类")
                    self.random_sleep(2, 3)

                except Exception as e:
                    logger.warning(f"精确XPath方法失败: {str(e)}")

                    # 使用JavaScript直接查找并点击
                    try:
                        self.driver.execute_script("""
                            var elements = document.getElementsByTagName('li');
                            for(var i = 0; i < elements.length; i++) {
                                if(elements[i].className.includes('haschild') && elements[i].className.includes('cur')) {
                                    var links = elements[i].getElementsByTagName('a');
                                    for(var j = 0; j < links.length; j++) {
                                        var spans = links[j].getElementsByTagName('span');
                                        for(var k = 0; k < spans.length; k++) {
                                            if(spans[k].textContent === '学位论文') {
                                                links[j].click();
                                                break;
                                            }
                                        }
                                    }
                                    break;
                                }
                            }
                        """)
                        logger.info("使用JavaScript方法点击学位论文分类")
                        self.random_sleep(2, 3)
                    except Exception as e:
                        logger.error(f"JavaScript方法也失败: {str(e)}")
                        return False

                # 等待学位论文列表加载
                self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "result-table-list"))
                )
                logger.info("已切换到学位论文分类")

                # 保存当前页面截图
                self.save_screenshot("degree_thesis_list.png")

                # 点击硕士论文选项
                try:
                    logger.info("正在查找硕士论文选项...")

                    # 使用classid定位
                    try:
                        master_option = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//a[contains(@classid, 'RMJLXHZ4')]"))
                        )
                        logger.info("找到硕士论文选项（通过classid）")
                    except:
                        # 使用文本内容定位
                        try:
                            master_option = self.wait.until(
                                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '硕士')]"))
                            )
                            logger.info("找到硕士论文选项（通过文本）")
                        except:
                            # 使用JavaScript查找并点击
                            try:
                                logger.info("尝试使用JavaScript方法点击硕士论文选项...")
                                self.driver.execute_script("""
                                    var elements = document.getElementsByTagName('a');
                                    for(var i = 0; i < elements.length; i++) {
                                        if(elements[i].textContent.includes('硕士') || 
                                           (elements[i].getAttribute('classid') && elements[i].getAttribute('classid').includes('RMJLXHZ4'))) {
                                            elements[i].click();
                                            break;
                                        }
                                    }
                                """)
                                logger.info("使用JavaScript方法点击硕士论文选项")
                                self.random_sleep(3, 5)

                                # 验证是否成功点击
                                try:
                                    self.wait.until(
                                        EC.presence_of_element_located((By.CLASS_NAME, "result-table-list"))
                                    )
                                    logger.info("硕士论文列表加载成功")
                                except:
                                    logger.warning("硕士论文列表未加载，尝试刷新页面...")
                                    self.driver.refresh()
                                    self.random_sleep(3, 5)

                                    # 重新等待列表加载
                                    self.wait.until(
                                        EC.presence_of_element_located((By.CLASS_NAME, "result-table-list"))
                                    )
                            except Exception as e:
                                logger.error(f"JavaScript方法也失败: {str(e)}")
                                return False
                            return True

                    # 如果找到了元素，使用常规点击方法
                    if master_option:
                        # 先尝试常规点击
                        try:
                            master_option.click()
                            logger.info("成功点击硕士论文选项")
                        except:
                            # 如果常规点击失败，使用JavaScript点击
                            self.driver.execute_script("arguments[0].click();", master_option)
                            logger.info("使用JavaScript点击硕士论文选项")

                        self.random_sleep(3, 5)

                        # 等待硕士论文列表加载完成
                        try:
                            # 等待结果列表加载
                            self.wait.until(
                                EC.presence_of_element_located((By.CLASS_NAME, "result-table-list"))
                            )

                            # 等待至少一篇论文加载
                            self.wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".result-table-list tbody tr"))
                            )

                            # 检查论文数量
                            paper_rows = self.driver.find_elements(By.CSS_SELECTOR, ".result-table-list tbody tr")
                            if not paper_rows:
                                logger.warning("硕士论文列表为空，尝试刷新页面...")
                                self.driver.refresh()
                                self.random_sleep(3, 5)

                                # 重新等待论文列表加载
                                self.wait.until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "result-table-list"))
                                )
                                self.wait.until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, ".result-table-list tbody tr"))
                                )

                                paper_rows = self.driver.find_elements(By.CSS_SELECTOR, ".result-table-list tbody tr")
                                if not paper_rows:
                                    logger.error("刷新后仍然没有找到论文")
                                    return False

                            logger.info(f"成功加载硕士论文列表，找到 {len(paper_rows)} 篇论文")

                        except TimeoutException:
                            logger.error("等待硕士论文列表加载超时")
                            return False
                        except Exception as e:
                            logger.error(f"等待硕士论文列表加载时出错: {str(e)}")
                            return False

                except Exception as e:
                    logger.error(f"点击硕士论文选项失败: {str(e)}")
                    self.save_screenshot("degree_thesis_error.png")
                    return False

            except Exception as e:
                logger.error(f"点击学位论文分类失败: {str(e)}")
                self.save_screenshot("degree_thesis_error.png")
                return False

            # 翻页到指定页码
            if page > 1:
                try:
                    logger.info(f"正在翻页到第 {page} 页...")

                    # 使用多种方法定位页码链接
                    page_link = None
                    try:
                        # 方法1：使用data-curpage属性
                        page_link = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, f"//a[@data-curpage='{page}']"))
                        )
                        logger.info(f"通过data-curpage找到第 {page} 页链接")
                    except:
                        try:
                            # 方法2：使用JavaScript查找并点击
                            self.driver.execute_script(f"""
                                var links = document.getElementsByTagName('a');
                                for(var i = 0; i < links.length; i++) {{
                                    if(links[i].getAttribute('data-curpage') === '{page}') {{
                                        links[i].click();
                                        return true;
                                    }}
                                }}
                                return false;
                            """)
                            logger.info(f"使用JavaScript方法点击第 {page} 页链接")
                            page_link = True  # 标记已经点击
                        except:
                            try:
                                # 方法3：使用下一页按钮
                                if page > 1:
                                    next_button = self.wait.until(
                                        EC.element_to_be_clickable((By.ID, "PageNext"))
                                    )
                                    for _ in range(page - 1):
                                        next_button.click()
                                        self.random_sleep(1, 2)
                                    logger.info(f"通过下一页按钮到达第 {page} 页")
                                    page_link = True  # 标记已经点击
                            except:
                                logger.error("所有方法都无法找到页码链接")
                                raise Exception("无法找到页码链接")

                    # 如果找到了页码链接（不是通过JavaScript或下一页按钮点击的），则点击
                    if page_link and page_link is not True:
                        try:
                            page_link.click()
                            logger.info(f"成功点击第 {page} 页链接")
                        except:
                            # 如果常规点击失败，使用JavaScript点击
                            self.driver.execute_script("arguments[0].click();", page_link)
                            logger.info(f"使用JavaScript点击第 {page} 页链接")

                    # 等待页面加载完成
                    self.random_sleep(3, 5)

                    # 等待结果列表重新加载
                    self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "result-table-list"))
                    )

                    # 等待至少一篇论文加载
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".result-table-list tbody tr"))
                    )

                    logger.info(f"成功加载第 {page} 页")

                except Exception as e:
                    logger.error(f"翻页失败: {str(e)}")
                    return False

            return True

        except TimeoutException:
            logger.error("页面加载超时")
            return False
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return False

    def parse_paper_info(self):
        """解析论文信息"""
        papers = []
        try:
            # 等待论文列表加载
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "result-table-list"))
            )

            # 获取所有论文行，从第二列开始
            paper_rows = self.driver.find_elements(By.CSS_SELECTOR, ".result-table-list tbody tr:nth-child(n+2)")

            if not paper_rows:
                logger.warning("本页未找到论文")
                return papers

            logger.info(f"本页找到 {len(paper_rows)} 篇论文")

            for row in paper_rows:
                try:
                    # 获取论文标题
                    try:
                        title_element = row.find_element(By.CSS_SELECTOR, "td.name a.fz14")
                        title = title_element.text.strip()
                        detail_url = title_element.get_attribute('href')
                    except:
                        # 尝试其他可能的选择器
                        try:
                            title_element = row.find_element(By.CSS_SELECTOR, "td.name a")
                            title = title_element.text.strip()
                            detail_url = title_element.get_attribute('href')
                        except:
                            logger.warning("无法获取论文标题，跳过此论文")
                            continue

                    # 获取作者信息
                    try:
                        author = row.find_element(By.CSS_SELECTOR, "td.author").text.strip()
                    except:
                        try:
                            author = row.find_element(By.CSS_SELECTOR, "td.author a").text.strip()
                        except:
                            author = "未知作者"
                            logger.warning(f"无法获取作者信息: {title}")

                    # 获取来源信息
                    try:
                        source = row.find_element(By.CSS_SELECTOR, "td.source").text.strip()
                    except:
                        try:
                            source = row.find_element(By.CSS_SELECTOR, "td.source a").text.strip()
                        except:
                            source = "未知来源"
                            logger.warning(f"无法获取来源信息: {title}")

                    logger.info(f"正在处理论文: {title}")

                    # 获取中英文摘要和所有提取的文字
                    try:
                        chinese_abstract, english_abstract, all_extracted_text = self.get_paper_abstracts(detail_url)
                    except Exception as e:
                        logger.error(f"获取摘要时出错: {str(e)}")
                        chinese_abstract = ""
                        english_abstract = ""
                        all_extracted_text = ""

                    # 将提取的文本保存到临时文件
                    paper_data = {
                        '标题': title,
                        '作者': author,
                        '来源': source,
                        '中文摘要': chinese_abstract,
                        '英文摘要': english_abstract,
                        '完整文本': all_extracted_text
                    }

                    # 立即保存到Excel
                    self.save_to_excel([paper_data])

                    papers.append(paper_data)

                except NoSuchElementException as e:
                    logger.warning(f"解析论文信息时出错: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"处理论文时出错: {str(e)}")
                    continue

        except TimeoutException:
            logger.error("等待论文列表超时")
        except Exception as e:
            logger.error(f"解析论文列表时出错: {str(e)}")

        return papers

    def handle_slider_verification(self):
        """处理滑块验证"""
        try:
            # 等待滑块出现，使用多个可能的选择器
            slider_selectors = [
                "//div[contains(@class, 'slider')]",
                "//div[contains(@class, 'verify')]",
                "//div[contains(@class, 'nc_iconfont')]",
                "//div[contains(@class, 'nc-container')]",
                "//div[contains(@class, 'nc_scale')]",
                "//div[contains(@class, 'nc_bg')]",
                "//div[contains(@class, 'nc_iconfont')]",
                "//div[contains(@class, 'nc_iconfont')]//div[contains(@class, 'button')]",
                "//div[contains(@class, 'nc_iconfont')]//div[contains(@class, 'slider')]",
                "//div[contains(@class, 'nc_iconfont')]//div[contains(@class, 'btn')]"
            ]

            slider = None
            for selector in slider_selectors:
                try:
                    slider = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    logger.info(f"找到滑块元素，使用选择器: {selector}")
                    break
                except:
                    continue

            if not slider:
                logger.error("未找到滑块元素，尝试获取页面源码...")
                logger.info(f"当前页面标题: {self.driver.title}")
                logger.info(f"当前页面URL: {self.driver.current_url}")
                logger.info(f"页面源码: {self.driver.page_source[:1000]}")  # 只打印前1000个字符
                return False

            # 获取滑块和轨道元素，使用多个可能的选择器
            button_selectors = [
                "//div[contains(@class, 'button')]",
                "//div[contains(@class, 'btn')]",
                "//div[contains(@class, 'slider')]//div",
                "//div[contains(@class, 'nc_iconfont')]//div"
            ]

            slider_button = None
            slider_track = None

            for selector in button_selectors:
                try:
                    slider_button = slider.find_element(By.XPATH, selector)
                    logger.info(f"找到滑块按钮，使用选择器: {selector}")
                    break
                except:
                    continue

            if not slider_button:
                logger.error("未找到滑块按钮")
                return False

            # 获取轨道元素
            track_selectors = [
                "//div[contains(@class, 'track')]",
                "//div[contains(@class, 'nc_bg')]",
                "//div[contains(@class, 'nc_scale')]",
                "//div[contains(@class, 'slider')]//div[contains(@class, 'bg')]"
            ]

            for selector in track_selectors:
                try:
                    slider_track = slider.find_element(By.XPATH, selector)
                    logger.info(f"找到滑块轨道，使用选择器: {selector}")
                    break
                except:
                    continue

            if not slider_track:
                logger.error("未找到滑块轨道")
                return False

            # 获取轨道宽度和滑块位置
            track_width = slider_track.size['width']
            button_location = slider_button.location
            track_location = slider_track.location

            logger.info(f"轨道宽度: {track_width}")
            logger.info(f"按钮位置: {button_location}")
            logger.info(f"轨道位置: {track_location}")

            # 计算需要滑动的距离（轨道宽度的80%）
            target_distance = track_width * 0.8
            logger.info(f"目标滑动距离: {target_distance}")

            # 方法1：使用JavaScript直接设置滑块位置
            try:
                self.driver.execute_script("""
                    var slider = arguments[0];
                    var track = arguments[1];
                    var distance = arguments[2];
                    slider.style.transform = 'translateX(' + distance + 'px)';
                    track.style.transition = 'all 0.3s ease 0s';
                """, slider_button, slider_track, target_distance)
                self.random_sleep(1, 2)
                logger.info("使用JavaScript方法完成验证")
                return True
            except Exception as e:
                logger.warning(f"JavaScript方法失败: {str(e)}")

            # 方法2：模拟人类滑动行为
            try:
                # 点击并按住滑块
                actions = webdriver.ActionChains(self.driver)
                actions.click_and_hold(slider_button).perform()
                self.random_sleep(0.5, 1)

                # 分多步滑动，模拟人类行为
                steps = 10
                for i in range(steps):
                    # 计算当前步的移动距离
                    current_distance = target_distance * (i + 1) / steps
                    # 添加随机偏移
                    random_offset = random.randint(-5, 5)
                    # 计算移动时间（逐渐加快）
                    move_time = 0.1 + (0.2 * (1 - i / steps))

                    # 移动到目标位置
                    actions.move_by_offset(current_distance + random_offset, 0).pause(move_time).perform()

                # 释放滑块
                actions.release().perform()
                logger.info("使用模拟滑动方法完成验证")

                # 等待验证结果
                self.random_sleep(2, 3)

                # 检查验证是否成功
                try:
                    self.wait.until_not(
                        EC.presence_of_element_located(
                            (By.XPATH, "//div[contains(@class, 'slider') or contains(@class, 'verify')]"))
                    )
                    logger.info("验证成功")
                    return True
                except TimeoutException:
                    logger.warning("验证可能失败，尝试最后一种方法...")
            except Exception as e:
                logger.warning(f"模拟滑动方法失败: {str(e)}")

            # 方法3：使用JavaScript触发事件
            try:
                self.driver.execute_script("""
                    var slider = arguments[0];
                    var event = new MouseEvent('mousedown', {
                        'view': window,
                        'bubbles': true,
                        'cancelable': true
                    });
                    slider.dispatchEvent(event);

                    setTimeout(function() {
                        var moveEvent = new MouseEvent('mousemove', {
                            'view': window,
                            'bubbles': true,
                            'cancelable': true,
                            'clientX': arguments[1]
                        });
                        slider.dispatchEvent(moveEvent);

                        setTimeout(function() {
                            var upEvent = new MouseEvent('mouseup', {
                                'view': window,
                                'bubbles': true,
                                'cancelable': true
                            });
                            slider.dispatchEvent(upEvent);
                        }, 500);
                    }, 100);
                """, slider_button, track_location['x'] + target_distance)
                logger.info("使用JavaScript事件方法完成验证")
                return True
            except Exception as e:
                logger.error(f"所有验证方法都失败: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"滑块验证失败: {str(e)}")
            # 保存错误时的页面截图
            self.save_screenshot("slider_error.png")
            return False

    def get_paper_abstracts(self, detail_url):
        """获取论文摘要"""
        chinese_abstract = ""
        english_abstract = ""
        all_extracted_text = ""  # 存储所有提取的文字

        # 保存当前标签页
        main_window = self.driver.current_window_handle

        try:
            # 打开新标签页
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])

            # 访问详情页，设置超时
            self.driver.set_page_load_timeout(10)  # 设置10秒超时
            try:
                self.driver.get(detail_url)
            except TimeoutException:
                logger.warning("页面加载超时，跳过...")
                return "", "", ""
            self.random_sleep(3, 5)  # 增加等待时间

            # 检查是否是付费文章
            try:
                pay_warning = self.driver.find_elements(By.XPATH,
                                                        "//div[contains(text(), '付费') or contains(text(), '购买') or contains(text(), 'VIP')]")
                if pay_warning:
                    logger.warning("发现付费文章，跳过...")
                    return "", "", ""
            except:
                pass

            # 检查是否存在原版阅读按钮
            try:
                # 等待页面加载完成
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '原版阅读')]"))
                )
            except TimeoutException:
                logger.warning("未找到原版阅读按钮，跳过该论文...")
                # 确保关闭当前标签页
                self.driver.close()
                self.driver.switch_to.window(main_window)
                return "", "", ""

            # 点击"原版阅读"按钮
            try:
                # 点击原版阅读按钮
                original_button = self.driver.find_element(By.XPATH, "//a[contains(text(), '原版阅读')]")
                original_button.click()
                self.random_sleep(3, 5)  # 增加等待时间

                # 切换到新打开的标签页
                if len(self.driver.window_handles) > 2:
                    self.driver.switch_to.window(self.driver.window_handles[-1])

                # 检查是否有滑块验证码
                try:
                    slider = self.driver.find_elements(By.XPATH,
                                                       "//div[contains(@class, 'slider') or contains(@class, 'verify')]")
                    if slider:
                        logger.info("检测到滑块验证码，跳过当前论文...")
                        return "", "", ""
                except Exception as e:
                    logger.warning(f"滑块验证检查失败: {str(e)}")

                # 等待页面加载完成
                try:
                    # 等待页面加载完成
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//span[@role='presentation']"))
                    )
                    logger.info("原版阅读页面加载完成")

                    # 额外等待确保内容完全加载
                    self.random_sleep(5, 8)

                    # 获取所有span标签
                    try:
                        # 初始化变量用于跟踪滚动
                        all_spans = set()  # 使用集合来存储唯一的span元素

                        # 加载多页内容
                        for i in range(10):
                            # 跳过第一页（封面）
                            if i == 0:
                                continue

                            # 获取当前页面的内容
                            try:
                                # 等待当前页面的内容加载
                                page_content = self.wait.until(
                                    EC.presence_of_element_located((By.ID, f"load-box{i + 1}"))
                                )

                                # 确保页面完全加载
                                self.driver.execute_script("""
                                    var element = arguments[0];
                                    var observer = new MutationObserver(function(mutations) {
                                        mutations.forEach(function(mutation) {
                                            if (mutation.type === 'childList' || mutation.type === 'characterData') {
                                                observer.disconnect();
                                            }
                                        });
                                    });
                                    observer.observe(element, {
                                        childList: true,
                                        characterData: true,
                                        subtree: true
                                    });
                                """, page_content)

                                # 等待一段时间确保内容完全加载
                                self.random_sleep(3, 5)

                                # 获取当前页面的span元素
                                current_spans = page_content.find_elements(By.XPATH, ".//span[@role='presentation']")

                                # 如果是第二页且没有找到span元素，跳过该论文
                                if i == 1 and len(current_spans) == 0:
                                    logger.warning("第二页没有找到span元素，跳过该论文")
                                    return "", "", ""

                                # 确保所有span元素都完全加载
                                for span in current_spans:
                                    try:
                                        # 等待元素可见
                                        self.wait.until(EC.visibility_of(span))
                                        # 获取完整的文本内容
                                        text = span.text
                                        if text.strip():
                                            # 检查文本是否完整
                                            if len(text) > 0 and not text.endswith('...'):
                                                all_spans.add(span)
                                            else:
                                                # 如果文本不完整，尝试获取完整内容
                                                full_text = self.driver.execute_script(
                                                    "return arguments[0].textContent;", span)
                                                if full_text.strip():
                                                    all_spans.add(span)
                                    except:
                                        continue

                                logger.info(f"第{i + 1}页找到 {len(current_spans)} 个span元素")

                                # 如果不是最后一页，滚动到下一页
                                if i < 9:
                                    self.driver.execute_script(
                                        f"document.getElementById('load-box{i + 1}').scrollIntoView();")
                                    self.random_sleep(8, 15)  # 增加等待时间，确保内容完全加载
                            except Exception as e:
                                logger.warning(f"加载第{i + 1}页时出错: {str(e)}")
                                break

                        if all_spans:
                            # 等待所有span加载完成并确保内容可见
                            self.wait.until(lambda driver: all(
                                span.is_displayed() and span.is_enabled()
                                for span in all_spans
                            ))

                            # 额外等待确保内容完全加载
                            self.random_sleep(2, 3)

                            # 按位置排序所有span
                            sorted_spans = sorted(all_spans, key=lambda x: (x.location['y'], x.location['x']))

                            # 提取所有span的文本内容
                            all_text = []
                            current_line = []
                            last_y = None

                            # 按顺序处理span元素
                            empty_span_count = 0  # 记录连续空span的数量
                            for span in sorted_spans:
                                try:
                                    # 获取span的位置
                                    rect = span.rect
                                    current_y = rect['y']

                                    # 如果是新的一行（y坐标变化超过阈值）
                                    if last_y is not None and abs(current_y - last_y) > 5:
                                        # 将当前行的文本合并并添加到结果中
                                        if current_line:
                                            line_text = ''.join(current_line)
                                            all_text.append(line_text)
                                            current_line = []
                                        empty_span_count = 0  # 新行重置计数

                                    # 检查是否是br标签
                                    if span.tag_name == 'br':
                                        # 将当前行的文本合并并添加到结果中
                                        if current_line:
                                            line_text = ''.join(current_line)
                                            all_text.append(line_text)
                                            current_line = []
                                        all_text.append('')  # 添加空行
                                        empty_span_count = 0  # 换行重置计数
                                        continue

                                    # 获取完整的文本内容，保留原始格式
                                    text = ""
                                    try:
                                        # 使用JavaScript获取原始内容
                                        text = self.driver.execute_script("return arguments[0].textContent;", span)
                                    except:
                                        # 即使获取失败也添加空值
                                        pass

                                    # 检查是否为空span
                                    if not text.strip():
                                        empty_span_count += 1
                                        if empty_span_count >= 2:
                                            logger.info("连续遇到两个空span，跳过当前页面")
                                            break
                                    else:
                                        empty_span_count = 0  # 非空span重置计数

                                    # 直接添加到当前行，不做任何处理
                                    current_line.append(text)

                                    # 记录日志以便调试
                                    logger.debug(f"提取到span内容: {text}")

                                    last_y = current_y
                                except Exception as e:
                                    logger.warning(f"处理span时出错: {str(e)}")
                                    # 出错时也添加空值
                                    current_line.append("")
                                    empty_span_count += 1
                                    if empty_span_count >= 2:
                                        logger.info("连续遇到两个空span，跳过当前页面")
                                        break
                                    continue

                            # 处理最后一行
                            if current_line:
                                line_text = ''.join(current_line)
                                all_text.append(line_text)

                            # 将文本按行组合，保留原始格式
                            combined_text = '\n'.join(all_text)

                            # 记录提取的span数量
                            logger.info(f"共处理了 {len(sorted_spans)} 个span元素")
                            logger.info(f"提取到 {len(all_text)} 行文本")

                            all_extracted_text = combined_text  # 保存所有提取的文字

                            # 保存文本内容用于调试
                            logger.info(f"提取的文本内容: {combined_text[:500]}...")  # 只打印前500个字符

                            # 提取中文摘要（从"摘要"开始到"关键词"结束）
                            try:
                                # 查找"摘要"的位置
                                abstract_start = combined_text.find("摘要")
                                if abstract_start != -1:
                                    logger.info("找到'摘要'标记")
                                    # 查找"关键词"的位置
                                    keywords_start = combined_text.find("关键词", abstract_start)
                                    if keywords_start != -1:
                                        logger.info("找到'关键词'标记")
                                        chinese_abstract = combined_text[abstract_start:keywords_start].strip()
                                        # 清理中文摘要
                                        chinese_abstract = self.clean_abstract(chinese_abstract, is_chinese=True)
                                        logger.info("成功提取并清理中文摘要")
                                    else:
                                        # 如果找不到"关键词"，尝试其他可能的结束标记
                                        end_markers = ["关键词", "关键字", "Key Words", "key words", "KEY WORDS"]
                                        for marker in end_markers:
                                            keywords_start = combined_text.find(marker, abstract_start)
                                            if keywords_start != -1:
                                                logger.info(f"找到备用结束标记 '{marker}'")
                                                chinese_abstract = combined_text[abstract_start:keywords_start].strip()
                                                # 清理中文摘要
                                                chinese_abstract = self.clean_abstract(chinese_abstract,
                                                                                       is_chinese=True)
                                                logger.info("成功提取并清理中文摘要")
                                                break
                                        else:
                                            # 如果找不到任何结束标记，尝试提取到下一个标题
                                            next_title = combined_text.find("Abstract", abstract_start)
                                            if next_title != -1:
                                                chinese_abstract = combined_text[abstract_start:next_title].strip()
                                                # 清理中文摘要
                                                chinese_abstract = self.clean_abstract(chinese_abstract,
                                                                                       is_chinese=True)
                                                logger.info("使用'Abstract'作为结束标记提取中文摘要")
                                            else:
                                                # 如果还是找不到，就提取到文本末尾
                                                chinese_abstract = combined_text[abstract_start:].strip()
                                                # 清理中文摘要
                                                chinese_abstract = self.clean_abstract(chinese_abstract,
                                                                                       is_chinese=True)
                                                logger.info("提取到文本末尾作为中文摘要")
                            except Exception as e:
                                logger.error(f"提取中文摘要时出错: {str(e)}")

                            # 提取英文摘要
                            try:
                                abstract_start = combined_text.lower().find("abstract")
                                if abstract_start != -1:
                                    logger.info("找到'Abstract'标记")
                                    # 查找"Key Words"的位置（不区分大小写）
                                    keywords_start = combined_text.lower().find("key words", abstract_start)
                                    if keywords_start != -1:
                                        logger.info("找到'Key Words'标记")
                                        english_abstract = combined_text[abstract_start:keywords_start].strip()
                                        # 清理英文摘要
                                        english_abstract = self.clean_abstract(english_abstract, is_chinese=False)
                                        logger.info("成功提取并清理英文摘要")
                                    else:
                                        # 如果找不到"Key Words"，尝试其他可能的结束标记
                                        end_markers = ["key words", "keywords", "KEY WORDS", "KEYWORDS"]
                                        for marker in end_markers:
                                            keywords_start = combined_text.lower().find(marker, abstract_start)
                                            if keywords_start != -1:
                                                logger.info(f"找到备用结束标记 '{marker}'")
                                                english_abstract = combined_text[abstract_start:keywords_start].strip()
                                                # 清理英文摘要
                                                english_abstract = self.clean_abstract(english_abstract,
                                                                                       is_chinese=False)
                                                logger.info("成功提取并清理英文摘要")
                                                break
                            except Exception as e:
                                logger.error(f"提取英文摘要时出错: {str(e)}")

                            logger.info(f"中文摘要长度: {len(chinese_abstract)}")
                            logger.info(f"英文摘要长度: {len(english_abstract)}")
                            logger.info(f"找到的span元素数量: {len(all_spans)}")
                        else:
                            logger.warning("未找到摘要内容")
                    except Exception as e:
                        logger.error(f"获取摘要内容时出错: {str(e)}")
                except Exception as e:
                    logger.error(f"等待页面加载失败: {str(e)}")
                    return "", "", ""
            except Exception as e:
                logger.warning(f"点击原版阅读按钮失败: {str(e)}")
                return "", "", ""

        except Exception as e:
            logger.error(f"获取摘要失败: {str(e)}")

        finally:
            # 关闭所有打开的标签页，除了主标签页
            try:
                while len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()
                # 切换回主标签页
                self.driver.switch_to.window(main_window)
                self.random_sleep(2, 3)  # 切换标签页后等待
            except Exception as e:
                logger.error(f"关闭标签页时出错: {str(e)}")
                # 如果出错，尝试刷新主页面
                self.driver.refresh()
                self.random_sleep(3, 5)  # 刷新后等待

        return chinese_abstract, english_abstract, all_extracted_text

    def clean_abstract(self, text, is_chinese=True):
        """清理摘要文本"""
        if not text:
            return text

        # 移除罗马数字（Ⅰ、Ⅱ等）及其后的内容
        roman_patterns = [
            r'[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ][、.．]',  # 罗马数字后跟顿号或点
            r'[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]\s',  # 罗马数字后跟空格
            r'[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]$',  # 行尾的罗马数字
            r'[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]'  # 单独的罗马数字
        ]

        for pattern in roman_patterns:
            text = re.sub(pattern, '', text)

        # 移除所有包含摘要的行
        if is_chinese:
            # 移除所有包含"摘要"的行（包括"摘要："和"摘要"）
            text = re.sub(r'^.*摘要[：:].*$', '', text, flags=re.MULTILINE)
            text = re.sub(r'^.*摘要.*$', '', text, flags=re.MULTILINE)
        else:
            # 移除所有包含"Abstract"的行（不区分大小写）
            text = re.sub(r'^.*abstract[：:].*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
            text = re.sub(r'^.*abstract.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)

        # 移除多余的空行
        text = re.sub(r'\n\s*\n', '\n', text)

        # 移除首尾空白
        text = text.strip()

        return text

    def save_to_excel(self, papers, filename='水利论文_完整内容.xlsx'):
        """保存到Excel文件"""
        try:
            # 获取当前工作目录
            current_dir = os.getcwd()
            # 构建完整的文件路径
            full_path = os.path.join(current_dir, filename)

            # 检查文件是否已存在
            if os.path.exists(full_path):
                # 读取现有数据
                try:
                    existing_df = pd.read_excel(full_path)
                    # 将新数据追加到现有数据
                    df = pd.concat([existing_df, pd.DataFrame(papers)], ignore_index=True)
                except Exception as e:
                    logger.warning(f"读取现有Excel文件失败，创建新文件: {str(e)}")
                    df = pd.DataFrame(papers)
            else:
                # 创建新的DataFrame
                df = pd.DataFrame(papers)

            # 使用ExcelWriter来设置列宽和格式
            with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
                # 保存数据
                df.to_excel(writer, index=False)

                # 获取工作表
                worksheet = writer.sheets['Sheet1']

                # 设置列宽
                for idx, col in enumerate(df.columns):
                    # 获取最大内容长度
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    # 设置列宽，不限制最大宽度
                    worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2

                # 设置单元格格式为文本，防止内容被截断
                for row in worksheet.iter_rows():
                    for cell in row:
                        cell.number_format = '@'  # 设置为文本格式
                        # 设置自动换行
                        cell.alignment = openpyxl.styles.Alignment(
                            wrap_text=True,
                            vertical='top',
                            horizontal='left'
                        )

            logger.info(f"数据已保存到 {full_path}")
        except Exception as e:
            logger.error(f"保存Excel文件时出错: {str(e)}")
            # 尝试使用简单路径保存
            try:
                simple_path = filename
                if os.path.exists(simple_path):
                    existing_df = pd.read_excel(simple_path)
                    df = pd.concat([existing_df, pd.DataFrame(papers)], ignore_index=True)
                else:
                    df = pd.DataFrame(papers)

                with pd.ExcelWriter(simple_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                    worksheet = writer.sheets['Sheet1']
                    for row in worksheet.iter_rows():
                        for cell in row:
                            cell.number_format = '@'
                            cell.alignment = openpyxl.styles.Alignment(
                                wrap_text=True,
                                vertical='top',
                                horizontal='left'
                            )
                logger.info(f"数据已保存到 {simple_path}")
            except Exception as e2:
                logger.error(f"使用简单路径保存也失败: {str(e2)}")

    def crawl(self, keyword='水利', max_pages=100):
        """主爬取函数"""
        all_papers = []
        current_page = 50  # 从第二页开始
        retry_count = 0
        max_retries = 3
        output_file = '水利论文_完整内容.xlsx'  # 统一的输出文件名

        logger.info("开始爬取任务...")

        try:
            # 先进行登录
            if not self.login():
                logger.error("登录失败，无法继续爬取")
                return

            # 先搜索并设置好筛选条件（只需要做一次）
            if not self.search_papers(keyword, page=1):
                logger.error("初始搜索失败，无法继续爬取")
                return

            # 从第二页开始爬取
            while current_page <= max_pages:
                logger.info(f"\n开始爬取第 {current_page} 页...")

                try:
                    # 直接跳转到指定页码
                    logger.info(f"正在跳转到第 {current_page} 页...")

                    # 使用多种方法定位页码链接
                    page_link = None
                    try:
                        # 使用data-curpage属性
                        page_link = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, f"//a[@data-curpage='{current_page}']"))
                        )
                        logger.info(f"通过data-curpage找到第 {current_page} 页链接")
                    except:
                        try:
                            #使用JavaScript查找并点击
                            self.driver.execute_script(f"""
                                var links = document.getElementsByTagName('a');
                                for(var i = 0; i < links.length; i++) {{
                                    if(links[i].getAttribute('data-curpage') === '{current_page}') {{
                                        links[i].click();
                                        return true;
                                    }}
                                }}
                                return false;
                            """)
                            logger.info(f"使用JavaScript方法点击第 {current_page} 页链接")
                            page_link = True  # 标记已经点击
                        except:
                            try:
                                # 使用下一页按钮
                                if current_page > 1:
                                    next_button = self.wait.until(
                                        EC.element_to_be_clickable((By.ID, "PageNext"))
                                    )
                                    for _ in range(current_page - 1):
                                        next_button.click()
                                        self.random_sleep(1, 2)
                                    logger.info(f"通过下一页按钮到达第 {current_page} 页")
                                    page_link = True  # 标记已经点击
                            except:
                                logger.error("所有方法都无法找到页码链接")
                                raise Exception("无法找到页码链接")

                    # 如果找到了页码链接，则点击
                    if page_link and page_link is not True:
                        try:
                            page_link.click()
                            logger.info(f"成功点击第 {current_page} 页链接")
                        except:
                            # 如果常规点击失败，使用JavaScript点击
                            self.driver.execute_script("arguments[0].click();", page_link)
                            logger.info(f"使用JavaScript点击第 {current_page} 页链接")

                    # 等待页面加载完成
                    self.random_sleep(3, 5)

                    # 等待结果列表重新加载
                    self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "result-table-list"))
                    )

                    # 等待至少一篇论文加载
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".result-table-list tbody tr"))
                    )

                    logger.info(f"成功加载第 {current_page} 页")

                    # 解析论文信息
                    papers = self.parse_paper_info()
                    if not papers:
                        retry_count += 1
                        if retry_count >= max_retries:
                            logger.error(f"连续 {max_retries} 次解析失败，跳过第 {current_page} 页")
                            current_page += 1
                            retry_count = 0
                            continue

                        logger.warning(f"第 {current_page} 页未找到论文，等待后重试... (第 {retry_count} 次)")
                        self.random_sleep(5, 10)
                        continue

                    all_papers.extend(papers)
                    logger.info(f"第 {current_page} 页爬取完成，找到 {len(papers)} 篇论文")

                    # 每爬取一页就保存一次，但都保存到同一个文件
                    if papers:
                        self.save_to_excel(papers, output_file)
                        logger.info(f"已保存当前进度到 {output_file}")

                    current_page += 1
                    retry_count = 0
                    self.random_sleep(3, 5)

                except Exception as e:
                    logger.error(f"处理第 {current_page} 页时出错: {str(e)}")
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"连续 {max_retries} 次失败，跳过第 {current_page} 页")
                        current_page += 1
                        retry_count = 0
                    self.random_sleep(5, 10)

        except Exception as e:
            logger.error(f"爬取过程中出错: {str(e)}")

        finally:
            if all_papers:
                # 保存最终结果到同一个文件
                self.save_to_excel(all_papers, output_file)
                logger.info(f"爬取完成，共找到 {len(all_papers)} 篇论文，所有内容已保存到 {output_file}")
            else:
                logger.warning("没有找到相关论文")

            # 清理截图文件
            self.cleanup_screenshots()

            # 关闭浏览器
            self.driver.quit()


if __name__ == '__main__':
    try:
        logger.info("启动爬虫程序...")
        # 设置CNKI账号和密码
        username = "17816515259"
        password = "Yxy20021023qaz@"
        crawler = CNKICrawler(username=username, password=password)
        crawler.crawl(keyword='水利', max_pages=50)
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
    finally:
        logger.info("程序结束")
