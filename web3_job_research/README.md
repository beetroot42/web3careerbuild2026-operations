# 📊 Web3 新人入行指南：2026年岗位市场分析

> 基于 **426条真实岗位数据** 的 Web3 就业市场深度调研

[![DashBoard](https://img.shields.io/badge/Interactive-Dashboard-blue)](https://your-username.github.io/repo-name)
[![Data](https://img.shields.io/badge/Data-426_Jobs-green)](./data)
[![Report](https://img.shields.io/badge/Report-Available-orange)](./report_template.md)

---

## 🎯 项目亮点

### 数据规模
- **426** 个 Web3 岗位的完整数据集
- **200+** 家公司覆盖
- **2026年1月** 最新采集

### 核心发现
- 💼 **47.7%** 岗位支持远程工作
- � **仅 3.8%** 岗位面向新人（Junior/Intern）
- 💰 技术岗薪资是非技术岗的 **2-3倍**
- 📈 **Marketing/Growth** 是新人最大入口（13.1%）

### 技术实现
- 🕷️ **Web 爬虫**：自动化数据采集（Web3.career）
- 📊 **数据分析**：聚类分析、薪资建模
- � **交互式仪表盘**：React + Recharts 可视化
- 📝 **完整报告**：一体化数据报告

---

## 📁 项目结构

```
web3_job_research/
├── � DashBoard.html           # 交互式仪表盘（主要成果）
├── 📄 report_template.md       # 完整调研报告
├── 📄 SOURCES.md               # 数据来源文档
│
├── 🐍 scraper.py               # 数据爬虫
├── 🐍 clustering_analysis.py   # 聚类分析
├── 🐍 salary_visualization.py  # 薪资可视化
│
├── 📂 data/                     # 原始数据
│   ├── jobs_data.csv            # 426条岗位数据
│   ├── jobs_raw.json            # JSON格式原始数据
│   └── statistics.json          # 统计摘要
│
└── 📂 analysis_output/          # 分析结果
    ├── clustering_report.txt    # 聚类分析报告
    ├── clustered_jobs.csv       # 带聚类标签的数据
    └── cluster_analysis.json    # 聚类统计
```

---

##  核心数据洞察

### 岗位类型分布 Top 5

| 岗位类型 | 数量 | 占比 | 薪资范围 (Mid级) |
|---------|------|------|------------------|
| Product Manager | 63 | 14.8% | $100k-$150k |
| Marketing/Growth | 53 | 12.4% | $70k-$110k |
| Designer | 34 | 8.0% | $80k-$120k |
| Blockchain Developer | 30 | 7.0% | $110k-$160k |
| Rust/Solana Developer | 16 | 3.8% | $130k-$200k |

### 资历级别分布

| 级别 | 数量 | 占比 | 竞争程度 |
|------|------|------|----------|
| **Mid** (1-3年) | 249 | 58.5% | ⭐⭐⭐ 中等 |
| **Senior** (3-5年) | 104 | 24.4% | ⭐⭐ 较低 |
| **Lead** (管理层) | 57 | 13.4% | ⭐⭐ 较低 |
| **Junior** (新人) | 16 | **3.8%** | ⭐⭐⭐⭐⭐ 极高 |

### 薪资水平

| 岗位 | Junior | Mid | Senior |
|------|--------|-----|--------|
| Smart Contract Dev | $80k-$120k | $120k-$180k | $180k-$300k+ |
| Rust/Solana Dev | $90k-$130k | $130k-$200k | $200k-$350k |
| Product Manager | $70k-$100k | $100k-$150k | $150k-$220k |
| Marketing/Growth | $40k-$70k | $70k-$110k | $110k-$160k |

---

## 🎨 可视化成果

本项目包含完整的**交互式数据仪表盘**，支持：

- 📊 动态图表切换（概览 / 薪资分析 / 完整报告）
- 🔄 实时数据可视化（饼图、柱状图、条形图）
- 📱 响应式设计（支持移动端）
- 🎯 一键查看完整分析报告

**在线预览**：[点击访问仪表盘](https://your-username.github.io/repo-name)

---

## 📚 数据来源

- **岗位数据**：Web3.career (2026年1月采集)
- **行业报告**：
  - a16z State of Crypto 2025
  - Electric Capital Developer Report
  - Messari Crypto Theses 2026
- **薪资参考**：Glassdoor, Web3.career, 行业综合数据

详细来源见 [`SOURCES.md`](./SOURCES.md)

---

##  关键结论

1. **新人入行难度高**：Junior 岗位仅占 3.8%，竞争激烈
2. **Marketing 是最大入口**：非技术岗位占低门槛岗位的 95%
3. **技术岗高薪优势明显**：核心开发岗薪资是运营岗的 2-3 倍
4. **远程工作成主流**：近半数岗位支持全球远程
5. **技能迁移可行**：PM/Designer 可从传统行业转型

---

## 🛠️ 技术栈

- **数据采集**：Python (requests, BeautifulSoup)
- **数据分析**：pandas, numpy, scikit-learn
- **可视化**：matplotlib, Recharts
- **前端**：React, Tailwind CSS
- **工具**：Jupyter Notebook (分析过程)
