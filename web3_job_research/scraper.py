"""
Web3 就业市场增强版爬虫 V2
支持多个平台：Web3.career, Remote OK, WellFound, 电鸭社区
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
from collections import Counter
import os
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(OUTPUT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


class Web3CareerScraper:
    """爬取 web3.career"""
    
    BASE_URL = "https://web3.career"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def fetch_page(self, category="", page=1):
        url = f"{self.BASE_URL}/{category}" if category else f"{self.BASE_URL}/web3-jobs"
        if page > 1:
            url = f"{url}?page={page}"
        
        try:
            print(f"  [Web3.career] 爬取: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  [Web3.career] 请求失败: {e}")
            return None
    
    def parse_jobs(self, html):
        if not html:
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        jobs = []
        job_rows = soup.select("tr.table_row")
        
        for row in job_rows:
            try:
                cells = row.find_all("td")
                if len(cells) < 3:
                    continue
                
                title_elem = cells[0].find("a") or cells[0]
                company_elem = cells[1] if len(cells) > 1 else None
                
                job = {
                    "title": title_elem.get_text(strip=True) if title_elem else "Unknown",
                    "company": company_elem.get_text(strip=True) if company_elem else "Unknown",
                    "location": cells[3].get_text(strip=True) if len(cells) > 3 else "Remote",
                    "posted": cells[2].get_text(strip=True) if len(cells) > 2 else "Unknown",
                    "source": "web3.career",
                }
                
                if len(job["company"]) > 80:
                    continue
                
                jobs.append(job)
                
            except Exception as e:
                continue
        
        return jobs
    
    def scrape(self, pages=50):
        all_jobs = []
        # 扩展分类列表以获取更多数据
        categories = [
            "",           # 全部
            "remote-jobs",
            "developer-jobs", 
            "solidity-jobs",
            "rust-jobs",
            "marketing-jobs",
            "community-jobs",
            "product-jobs",
            "design-jobs",
            "defi-jobs",
            "nft-jobs",
            "internship-jobs",
        ]
        
        for category in categories:
            cat_name = category if category else "all"
            print(f"\n📂 [Web3.career] 分类: {cat_name}")
            
            # 每个分类爬取更多页
            max_pages_per_cat = max(pages // len(categories), 5)
            for page in range(1, max_pages_per_cat + 1):
                html = self.fetch_page(category, page)
                if html:
                    jobs = self.parse_jobs(html)
                    for job in jobs:
                        job["category"] = cat_name
                    all_jobs.extend(jobs)
                    print(f"    第 {page} 页: {len(jobs)} 个职位")
                    if len(jobs) == 0:
                        break
                time.sleep(1)  # 稍微加快速度
        
        return all_jobs


class RemoteOKScraper:
    """爬取 remoteok.com - 远程工作聚合站"""
    
    BASE_URL = "https://remoteok.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        # Remote OK 需要特殊的 User-Agent
        self.session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    
    def fetch_jobs(self, tag="blockchain"):
        """获取指定标签的职位"""
        url = f"{self.BASE_URL}/remote-{tag}-jobs"
        
        try:
            print(f"  [RemoteOK] 爬取: {url}")
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  [RemoteOK] 请求失败: {e}")
            return None
    
    def parse_jobs(self, html):
        if not html:
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        jobs = []
        
        # Remote OK 使用表格行展示职位
        job_rows = soup.select("tr.job")
        
        for row in job_rows:
            try:
                # 职位标题
                title_elem = row.select_one("h2, .company_and_position h2")
                title = title_elem.get_text(strip=True) if title_elem else None
                
                # 公司名
                company_elem = row.select_one("h3, .company_and_position h3")
                company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                
                # 标签
                tags = [tag.get_text(strip=True) for tag in row.select(".tag")]
                
                # 位置
                location_elem = row.select_one(".location")
                location = location_elem.get_text(strip=True) if location_elem else "Remote"
                
                if title:
                    job = {
                        "title": title,
                        "company": company,
                        "location": location if location else "Remote",
                        "posted": "Recent",
                        "source": "remoteok.com",
                        "tags": tags,
                    }
                    jobs.append(job)
                    
            except Exception as e:
                continue
        
        return jobs
    
    def scrape(self):
        all_jobs = []
        
        # 扩展标签列表
        tags = [
            "blockchain", "crypto", "web3", "defi", "solidity", "ethereum",
            "nft", "dao", "smart-contract", "rust", "bitcoin", "polygon",
            "token", "dapp", "metaverse", "gamefi"
        ]
        
        for tag in tags:
            print(f"\n📂 [RemoteOK] 标签: {tag}")
            html = self.fetch_jobs(tag)
            if html:
                jobs = self.parse_jobs(html)
                for job in jobs:
                    job["category"] = tag
                all_jobs.extend(jobs)
                print(f"    获取: {len(jobs)} 个职位")
            time.sleep(1.5)
        
        return all_jobs


class WellFoundScraper:
    """爬取 wellfound.com (原 AngelList) - 创业公司招聘"""
    
    BASE_URL = "https://wellfound.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def fetch_jobs(self, keyword="web3"):
        """搜索职位"""
        url = f"{self.BASE_URL}/jobs"
        params = {"q": keyword}
        
        try:
            print(f"  [WellFound] 搜索: {keyword}")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  [WellFound] 请求失败: {e}")
            return None
    
    def parse_jobs(self, html):
        if not html:
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        jobs = []
        
        # WellFound 职位卡片
        job_cards = soup.select("[data-test='JobListing'], .job-listing, article")
        
        for card in job_cards:
            try:
                title_elem = card.select_one("a[class*='JobTitle'], h2, .title")
                company_elem = card.select_one("[class*='company'], .company-name, h3")
                location_elem = card.select_one("[class*='location'], .location")
                
                title = title_elem.get_text(strip=True) if title_elem else None
                
                if title:
                    job = {
                        "title": title,
                        "company": company_elem.get_text(strip=True) if company_elem else "Unknown",
                        "location": location_elem.get_text(strip=True) if location_elem else "Remote",
                        "posted": "Recent",
                        "source": "wellfound.com",
                    }
                    jobs.append(job)
                    
            except Exception as e:
                continue
        
        return jobs
    
    def scrape(self):
        all_jobs = []
        # 扩展关键词列表
        keywords = [
            "web3", "blockchain", "crypto", "defi", "smart contract",
            "solidity", "ethereum", "nft", "dao", "tokenomics",
            "decentralized", "dapp"
        ]
        
        for keyword in keywords:
            print(f"\n📂 [WellFound] 关键词: {keyword}")
            html = self.fetch_jobs(keyword)
            if html:
                jobs = self.parse_jobs(html)
                for job in jobs:
                    job["category"] = keyword
                all_jobs.extend(jobs)
                print(f"    获取: {len(jobs)} 个职位")
            time.sleep(1.5)
        
        return all_jobs


class DeJobAIScraper:
    """爬取 dejob.ai - Web3远程招聘平台"""
    
    BASE_URL = "https://dejob.ai"
    API_URL = "https://dejob.ai/api"  # 尝试API端点
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.headers["Accept"] = "application/json, text/plain, */*"
        self.session.headers["Referer"] = "https://dejob.ai/job"
    
    def fetch_jobs_api(self, page=1, page_size=50):
        """尝试通过API获取职位"""
        # 常见的API端点格式
        possible_urls = [
            f"{self.API_URL}/job/list?page={page}&pageSize={page_size}",
            f"{self.API_URL}/jobs?page={page}&limit={page_size}",
            f"{self.BASE_URL}/api/job?page={page}",
            f"{self.BASE_URL}/job/list?page={page}",
        ]
        
        for url in possible_urls:
            try:
                print(f"  [DeJob.ai] 尝试: {url}")
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        return data
            except:
                continue
        
        return None
    
    def fetch_page(self):
        """获取页面HTML"""
        url = f"{self.BASE_URL}/job"
        
        try:
            print(f"  [DeJob.ai] 爬取: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  [DeJob.ai] 请求失败: {e}")
            return None
    
    def parse_jobs_from_html(self, html):
        """从HTML解析职位"""
        if not html:
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        jobs = []
        
        # 尝试多种选择器
        selectors = [
            ".job-item", ".job-card", ".job-list-item",
            "[class*='job']", "article", ".card",
            "div[class*='Job']", "li[class*='job']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if len(items) > 3:  # 找到有效的选择器
                for item in items:
                    try:
                        # 尝试获取标题
                        title_elem = item.select_one("h2, h3, .title, [class*='title'], a")
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        if len(title) < 3:
                            continue
                        
                        # 尝试获取公司
                        company_elem = item.select_one(".company, [class*='company'], span")
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        
                        # 尝试获取地点
                        location_elem = item.select_one(".location, [class*='location']")
                        location = location_elem.get_text(strip=True) if location_elem else "Remote"
                        
                        job = {
                            "title": title,
                            "company": company if len(company) < 50 else "Unknown",
                            "location": location,
                            "posted": "Recent",
                            "source": "dejob.ai",
                        }
                        jobs.append(job)
                        
                    except Exception as e:
                        continue
                
                if jobs:
                    break  # 成功找到职位，退出
        
        return jobs
    
    def parse_jobs_from_api(self, data):
        """从API响应解析职位"""
        jobs = []
        
        # 处理不同的API响应格式
        job_list = []
        if isinstance(data, list):
            job_list = data
        elif isinstance(data, dict):
            job_list = data.get("data", data.get("jobs", data.get("list", data.get("items", []))))
            if isinstance(job_list, dict):
                job_list = job_list.get("list", job_list.get("items", []))
        
        for item in job_list:
            try:
                job = {
                    "title": item.get("title", item.get("name", item.get("jobTitle", "Unknown"))),
                    "company": item.get("company", item.get("companyName", item.get("employer", "Unknown"))),
                    "location": item.get("location", item.get("city", item.get("area", "Remote"))),
                    "posted": item.get("createTime", item.get("postedAt", item.get("date", "Recent"))),
                    "source": "dejob.ai",
                    "salary": item.get("salary", item.get("salaryRange", "")),
                }
                
                if job["title"] and job["title"] != "Unknown":
                    jobs.append(job)
                    
            except Exception as e:
                continue
        
        return jobs
    
    def scrape(self):
        all_jobs = []
        
        print(f"\n📂 [DeJob.ai] 爬取Web3远程职位")
        
        # 方法1: 尝试API
        api_data = self.fetch_jobs_api()
        if api_data:
            jobs = self.parse_jobs_from_api(api_data)
            if jobs:
                all_jobs.extend(jobs)
                print(f"    通过API获取: {len(jobs)} 个职位")
                return all_jobs
        
        # 方法2: 解析HTML
        html = self.fetch_page()
        if html:
            jobs = self.parse_jobs_from_html(html)
            all_jobs.extend(jobs)
            print(f"    通过HTML获取: {len(jobs)} 个职位")
        
        return all_jobs


class EleDuckScraper:
    """爬取电鸭社区 (eleduck.com) - 国内远程工作社区"""
    
    BASE_URL = "https://eleduck.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def fetch_jobs(self, page=1):
        """获取职位列表"""
        url = f"{self.BASE_URL}/categories/5"  # 工作机会分类
        if page > 1:
            url = f"{url}?page={page}"
        
        try:
            print(f"  [电鸭社区] 爬取第 {page} 页")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  [电鸭社区] 请求失败: {e}")
            return None
    
    def parse_jobs(self, html):
        if not html:
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        jobs = []
        
        # 电鸭帖子列表
        posts = soup.select(".topic-list-item, .post-item, article.topic")
        
        for post in posts:
            try:
                title_elem = post.select_one(".title a, h2 a, .topic-title")
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    # 过滤非招聘帖子
                    if any(kw in title for kw in ["招", "聘", "求", "remote", "远程", "开发", "工程师"]):
                        job = {
                            "title": title,
                            "company": "电鸭社区发布",
                            "location": "Remote (China)",
                            "posted": "Recent",
                            "source": "eleduck.com",
                        }
                        jobs.append(job)
                    
            except Exception as e:
                continue
        
        return jobs
    
    def scrape(self, pages=5):
        all_jobs = []
        
        print(f"\n📂 [电鸭社区] 爬取远程工作")
        for page in range(1, pages + 1):
            html = self.fetch_jobs(page)
            if html:
                jobs = self.parse_jobs(html)
                all_jobs.extend(jobs)
                print(f"    第 {page} 页: {len(jobs)} 个职位")
                if len(jobs) == 0:
                    break
            time.sleep(1.5)
        
        return all_jobs


def extract_job_features(job):
    """提取职位特征用于分析"""
    title = job.get("title", "").lower()
    
    features = {
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "location": job.get("location", ""),
        "source": job.get("source", ""),
    }
    
    # 岗位类型分类
    if any(kw in title for kw in ["solidity", "smart contract", "智能合约"]):
        features["job_type"] = "Smart Contract Developer"
    elif any(kw in title for kw in ["rust", "solana"]) and any(kw in title for kw in ["engineer", "developer", "工程师"]):
        features["job_type"] = "Rust/Solana Developer"
    elif any(kw in title for kw in ["defi"]):
        features["job_type"] = "DeFi Engineer"
    elif any(kw in title for kw in ["blockchain", "protocol", "web3", "区块链"]) and any(kw in title for kw in ["engineer", "developer", "工程师", "开发"]):
        features["job_type"] = "Blockchain Developer"
    elif any(kw in title for kw in ["front", "react", "vue", "前端"]):
        features["job_type"] = "Frontend Developer"
    elif any(kw in title for kw in ["backend", "后端", "go ", "golang", "node", "python"]):
        features["job_type"] = "Backend Developer"
    elif any(kw in title for kw in ["full stack", "fullstack", "全栈"]):
        features["job_type"] = "Full Stack Developer"
    elif any(kw in title for kw in ["security", "audit", "安全", "审计"]):
        features["job_type"] = "Security/Auditor"
    elif any(kw in title for kw in ["devops", "sre", "运维"]):
        features["job_type"] = "DevOps/Infrastructure"
    elif any(kw in title for kw in ["data", "ml", "machine learning", "ai ", "数据"]):
        features["job_type"] = "Data/AI"
    elif any(kw in title for kw in ["product", "产品"]):
        features["job_type"] = "Product Manager"
    elif any(kw in title for kw in ["design", "ux", "ui", "设计"]):
        features["job_type"] = "Designer"
    elif any(kw in title for kw in ["community", "社区", "dao"]):
        features["job_type"] = "Community"
    elif any(kw in title for kw in ["marketing", "growth", "content", "social", "运营", "市场"]):
        features["job_type"] = "Marketing/Growth"
    elif any(kw in title for kw in ["compliance", "legal", "合规", "法务"]):
        features["job_type"] = "Compliance/Legal"
    elif any(kw in title for kw in ["research", "analyst", "研究"]):
        features["job_type"] = "Research/Analyst"
    elif any(kw in title for kw in ["qa", "test", "测试"]):
        features["job_type"] = "QA/Testing"
    elif any(kw in title for kw in ["ceo", "cto", "cfo", "head of", "director", "chief", "lead", "总监", "负责人"]):
        features["job_type"] = "Executive/Lead"
    else:
        features["job_type"] = "Other"
    
    # 资历级别
    if any(kw in title for kw in ["senior", "sr.", "staff", "principal", "高级", "资深"]):
        features["seniority"] = "Senior"
    elif any(kw in title for kw in ["junior", "jr.", "entry", "intern", "初级", "实习"]):
        features["seniority"] = "Junior"
    elif any(kw in title for kw in ["lead", "head", "director", "chief", "vp"]):
        features["seniority"] = "Lead"
    else:
        features["seniority"] = "Mid"
    
    # 是否远程
    location = job.get("location", "").lower()
    features["is_remote"] = any(kw in location for kw in ["remote", "远程", "worldwide", "global"])
    
    # 提取国家
    features["country"] = extract_country_from_location(location)
    
    return features


def extract_country_from_location(location):
    """从地点提取国家"""
    country_map = {
        "united states": "USA", "usa": "USA", "new york": "USA", "san francisco": "USA",
        "united kingdom": "UK", "london": "UK", "uk": "UK",
        "germany": "Germany", "berlin": "Germany",
        "singapore": "Singapore",
        "hong kong": "Hong Kong",
        "japan": "Japan", "tokyo": "Japan",
        "china": "China", "中国": "China", "北京": "China", "上海": "China", "深圳": "China",
        "india": "India",
        "brazil": "Brazil",
        "canada": "Canada",
        "remote": "Remote", "远程": "Remote", "worldwide": "Remote",
    }
    
    location = location.lower()
    for keyword, country in country_map.items():
        if keyword in location:
            return country
    return "Other"


def deduplicate_jobs(jobs):
    """去重"""
    seen = set()
    unique_jobs = []
    
    for job in jobs:
        key = f"{job.get('title', '').lower().strip()}_{job.get('company', '').lower().strip()}"
        if key not in seen and len(job.get("title", "")) > 3:
            seen.add(key)
            unique_jobs.append(job)
    
    return unique_jobs


def save_results(jobs, features_df):
    """保存结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    json_file = os.path.join(DATA_DIR, f"jobs_multi_source_{timestamp}.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON数据: {json_file}")
    
    csv_file = os.path.join(DATA_DIR, f"jobs_multi_features_{timestamp}.csv")
    features_df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    print(f"✅ CSV特征数据: {csv_file}")
    
    return json_file, csv_file


def generate_statistics(features_df):
    """生成统计摘要"""
    total = len(features_df)
    
    stats = {
        "total_jobs": total,
        "scraped_at": datetime.now().isoformat(),
        "by_source": features_df["source"].value_counts().to_dict(),
        "by_job_type": features_df["job_type"].value_counts().to_dict(),
        "by_seniority": features_df["seniority"].value_counts().to_dict(),
        "by_country": features_df["country"].value_counts().to_dict(),
        "remote_ratio": round(features_df["is_remote"].mean() * 100, 1),
    }
    
    print("\n" + "=" * 60)
    print("📊 多源数据采集统计")
    print("=" * 60)
    print(f"📋 总职位数: {total}")
    print(f"🏠 远程岗位比例: {stats['remote_ratio']}%")
    
    print("\n📡 数据来源分布:")
    for source, count in stats["by_source"].items():
        pct = count / total * 100
        print(f"  • {source}: {count} ({pct:.1f}%)")
    
    print("\n📈 岗位类型分布 (Top 10):")
    for job_type, count in list(stats["by_job_type"].items())[:10]:
        pct = count / total * 100
        print(f"  • {job_type}: {count} ({pct:.1f}%)")
    
    print("=" * 60)
    
    stats_file = os.path.join(DATA_DIR, f"multi_source_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"\n💾 统计数据: {stats_file}")
    
    return stats


def main():
    print("🚀 启动多源 Web3 就业数据爬虫 V2")
    print("=" * 60)
    print("数据源: Web3.career, RemoteOK, WellFound, DeJob.ai, 电鸭社区")
    print("=" * 60)
    
    all_jobs = []
    
    # 1. Web3.career
    print("\n" + "=" * 40)
    print("📡 数据源 1: Web3.career")
    print("=" * 40)
    try:
        scraper1 = Web3CareerScraper()
        jobs1 = scraper1.scrape(pages=20)
        all_jobs.extend(jobs1)
        print(f"✅ Web3.career: {len(jobs1)} 条")
    except Exception as e:
        print(f"❌ Web3.career 爬取失败: {e}")
    
    # 2. Remote OK
    print("\n" + "=" * 40)
    print("📡 数据源 2: RemoteOK")
    print("=" * 40)
    try:
        scraper2 = RemoteOKScraper()
        jobs2 = scraper2.scrape()
        all_jobs.extend(jobs2)
        print(f"✅ RemoteOK: {len(jobs2)} 条")
    except Exception as e:
        print(f"❌ RemoteOK 爬取失败: {e}")
    
    # 3. WellFound
    print("\n" + "=" * 40)
    print("📡 数据源 3: WellFound")
    print("=" * 40)
    try:
        scraper3 = WellFoundScraper()
        jobs3 = scraper3.scrape()
        all_jobs.extend(jobs3)
        print(f"✅ WellFound: {len(jobs3)} 条")
    except Exception as e:
        print(f"❌ WellFound 爬取失败: {e}")
    
    # 4. DeJob.ai (新增)
    print("\n" + "=" * 40)
    print("📡 数据源 4: DeJob.ai")
    print("=" * 40)
    try:
        scraper4 = DeJobAIScraper()
        jobs4 = scraper4.scrape()
        all_jobs.extend(jobs4)
        print(f"✅ DeJob.ai: {len(jobs4)} 条")
    except Exception as e:
        print(f"❌ DeJob.ai 爬取失败: {e}")
    
    # 5. 电鸭社区
    print("\n" + "=" * 40)
    print("📡 数据源 5: 电鸭社区")
    print("=" * 40)
    try:
        scraper5 = EleDuckScraper()
        jobs5 = scraper5.scrape(pages=5)
        all_jobs.extend(jobs5)
        print(f"✅ 电鸭社区: {len(jobs5)} 条")
    except Exception as e:
        print(f"❌ 电鸭社区 爬取失败: {e}")
    
    # 汇总
    print("\n" + "=" * 60)
    print(f"📊 原始总数: {len(all_jobs)}")
    unique_jobs = deduplicate_jobs(all_jobs)
    print(f"📊 去重后: {len(unique_jobs)}")
    
    if not unique_jobs:
        print("❌ 未获取到任何数据")
        return
    
    # 提取特征
    print("\n🔧 提取职位特征...")
    features = [extract_job_features(job) for job in unique_jobs]
    features_df = pd.DataFrame(features)
    
    # 保存结果
    save_results(unique_jobs, features_df)
    
    # 生成统计
    generate_statistics(features_df)
    
    print("\n🎉 多源数据采集完成！")


if __name__ == "__main__":
    main()
