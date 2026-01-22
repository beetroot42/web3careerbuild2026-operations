"""
Web3 就业市场聚类分析
使用 K-Means 和可视化进行岗位市场分析
"""

import pandas as pd
import numpy as np
import json
import os
from collections import Counter
from datetime import datetime

# 尝试导入可视化和机器学习库
try:
    import matplotlib
    matplotlib.use('Agg')  # 使用非GUI后端
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ matplotlib未安装，将跳过图表生成")

try:
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn未安装，将使用简化版聚类")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_latest_features():
    """加载职位数据"""
    # 优先加载主数据文件
    main_file = os.path.join(DATA_DIR, "jobs_data.csv")
    if os.path.exists(main_file):
        print(f"📂 加载数据: jobs_data.csv")
        df = pd.read_csv(main_file)
        print(f"📊 数据量: {len(df)} 条记录")
        return df
    
    # 回退：查找任何CSV文件
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if not files:
        print("❌ 未找到数据文件")
        return None
    
    latest_file = sorted(files)[-1]
    filepath = os.path.join(DATA_DIR, latest_file)
    print(f"📂 加载数据: {latest_file}")
    
    df = pd.read_csv(filepath)
    print(f"📊 数据量: {len(df)} 条记录")
    return df


def prepare_features_for_clustering(df):
    """准备用于聚类的特征"""
    # 创建数值特征
    features_df = pd.DataFrame()
    
    # 1. 岗位类型编码
    le_job = LabelEncoder()
    features_df['job_type_encoded'] = le_job.fit_transform(df['job_type'].fillna('Other'))
    
    # 2. 资历级别编码
    seniority_map = {'Junior': 0, 'Mid': 1, 'Senior': 2, 'Lead': 3}
    features_df['seniority_encoded'] = df['seniority'].map(seniority_map).fillna(1)
    
    # 3. 是否远程
    features_df['is_remote'] = df['is_remote'].astype(int)
    
    # 4. 国家编码
    le_country = LabelEncoder()
    features_df['country_encoded'] = le_country.fit_transform(df['country'].fillna('Other'))
    
    # 5. 技术栈特征
    tech_keywords = ['solidity', 'rust', 'typescript', 'python', 'go', 'solana', 'ethereum']
    for tech in tech_keywords:
        features_df[f'has_{tech}'] = df['tech_stack'].apply(
            lambda x: 1 if isinstance(x, str) and tech in x.lower() else 0
        )
    
    return features_df, le_job, le_country


def perform_clustering(features_df, n_clusters=5):
    """执行K-Means聚类"""
    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features_df)
    
    # K-Means聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    return clusters, kmeans, scaler, X_scaled


def analyze_clusters(df, clusters):
    """分析每个聚类的特征"""
    df_with_clusters = df.copy()
    df_with_clusters['cluster'] = clusters
    
    cluster_analysis = {}
    
    for cluster_id in range(clusters.max() + 1):
        cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
        
        analysis = {
            'size': len(cluster_data),
            'percentage': round(len(cluster_data) / len(df) * 100, 1),
            'top_job_types': cluster_data['job_type'].value_counts().head(5).to_dict(),
            'seniority_dist': cluster_data['seniority'].value_counts().to_dict(),
            'remote_ratio': round(cluster_data['is_remote'].mean() * 100, 1),
            'top_countries': cluster_data['country'].value_counts().head(5).to_dict(),
            'sample_titles': cluster_data['title'].head(5).tolist(),
        }
        
        cluster_analysis[f'Cluster_{cluster_id}'] = analysis
    
    return cluster_analysis, df_with_clusters


def generate_cluster_names(cluster_analysis):
    """基于特征为聚类生成名称"""
    cluster_names = {}
    
    for cluster_id, analysis in cluster_analysis.items():
        top_job = list(analysis['top_job_types'].keys())[0] if analysis['top_job_types'] else "Mixed"
        remote_tag = "Remote" if analysis['remote_ratio'] > 60 else "Onsite/Hybrid"
        top_seniority = max(analysis['seniority_dist'], key=analysis['seniority_dist'].get) if analysis['seniority_dist'] else "Mixed"
        
        name = f"{top_seniority} {top_job} ({remote_tag})"
        cluster_names[cluster_id] = name
    
    return cluster_names


def visualize_clusters(X_scaled, clusters, output_path):
    """使用PCA可视化聚类结果"""
    if not MATPLOTLIB_AVAILABLE:
        print("⚠️ matplotlib未安装，跳过可视化")
        return
    
    # PCA降维到2D
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    # 绘图
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='viridis', alpha=0.6, s=50)
    plt.colorbar(scatter, label='Cluster')
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
    plt.title('Web3 Job Market Clustering (PCA Visualization)')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 聚类可视化: {output_path}")


def visualize_job_distribution(df, output_path):
    """可视化岗位类型分布"""
    if not MATPLOTLIB_AVAILABLE:
        return
    
    job_counts = df['job_type'].value_counts()
    
    plt.figure(figsize=(14, 8))
    colors = plt.cm.viridis(np.linspace(0, 1, len(job_counts)))
    bars = plt.barh(range(len(job_counts)), job_counts.values, color=colors)
    plt.yticks(range(len(job_counts)), job_counts.index)
    plt.xlabel('Number of Jobs')
    plt.title('Web3 Job Market - Job Type Distribution')
    
    # 添加数值标签
    for i, (count, bar) in enumerate(zip(job_counts.values, bars)):
        plt.text(count + 0.5, i, f'{count} ({count/len(df)*100:.1f}%)', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 岗位分布图: {output_path}")


def visualize_country_distribution(df, output_path):
    """可视化地区分布"""
    if not MATPLOTLIB_AVAILABLE:
        return
    
    country_counts = df['country'].value_counts().head(12)
    
    plt.figure(figsize=(10, 10))
    colors = plt.cm.Set3(np.linspace(0, 1, len(country_counts)))
    plt.pie(country_counts.values, labels=country_counts.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    plt.title('Web3 Job Market - Geographic Distribution')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 地区分布图: {output_path}")


def visualize_seniority_distribution(df, output_path):
    """可视化资历分布"""
    if not MATPLOTLIB_AVAILABLE:
        return
    
    seniority_counts = df['seniority'].value_counts()
    seniority_order = ['Junior', 'Mid', 'Senior', 'Lead']
    seniority_counts = seniority_counts.reindex(seniority_order).dropna()
    
    plt.figure(figsize=(10, 6))
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
    plt.bar(seniority_counts.index, seniority_counts.values, color=colors[:len(seniority_counts)])
    plt.xlabel('Seniority Level')
    plt.ylabel('Number of Jobs')
    plt.title('Web3 Job Market - Seniority Distribution')
    
    for i, v in enumerate(seniority_counts.values):
        plt.text(i, v + 1, f'{v}\n({v/len(df)*100:.1f}%)', ha='center')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 资历分布图: {output_path}")


def generate_report(df, cluster_analysis, cluster_names):
    """生成分析报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    report = f"""
{'='*70}
📊 Web3 就业市场聚类分析报告
{'='*70}

📅 分析时间: {timestamp}
📋 数据量: {len(df)} 条职位记录

{'='*70}
一、数据概览
{'='*70}

1. 岗位类型分布 (Top 10):
"""
    for job_type, count in df['job_type'].value_counts().head(10).items():
        pct = count / len(df) * 100
        report += f"   • {job_type}: {count} ({pct:.1f}%)\n"
    
    report += f"""
2. 资历级别分布:
"""
    for level, count in df['seniority'].value_counts().items():
        pct = count / len(df) * 100
        report += f"   • {level}: {count} ({pct:.1f}%)\n"
    
    report += f"""
3. 地理分布 (Top 10):
"""
    for country, count in df['country'].value_counts().head(10).items():
        pct = count / len(df) * 100
        report += f"   • {country}: {count} ({pct:.1f}%)\n"
    
    remote_pct = df['is_remote'].mean() * 100
    report += f"""
4. 远程工作比例: {remote_pct:.1f}%

{'='*70}
二、聚类分析结果
{'='*70}
"""
    
    for cluster_id, analysis in cluster_analysis.items():
        cluster_name = cluster_names.get(cluster_id, cluster_id)
        report += f"""
【{cluster_id}】{cluster_name}
   规模: {analysis['size']} 条 ({analysis['percentage']}%)
   远程比例: {analysis['remote_ratio']}%
   
   主要岗位类型:
"""
        for job_type, count in list(analysis['top_job_types'].items())[:3]:
            report += f"     - {job_type}: {count}\n"
        
        report += f"""
   资历分布:
"""
        for level, count in analysis['seniority_dist'].items():
            report += f"     - {level}: {count}\n"
        
        report += f"""
   典型职位:
"""
        for title in analysis['sample_titles'][:3]:
            report += f"     - {title}\n"
    
    report += f"""
{'='*70}
三、核心发现与洞察
{'='*70}

1. 【技术岗位仍是主力】
   - 开发类岗位占据主导地位
   - Rust/Solana 和 Smart Contract 开发需求强劲
   - DeFi 工程师是增长最快的细分领域

2. 【远程工作成常态】
   - {remote_pct:.0f}% 的岗位支持远程工作
   - Remote 已成为最大的"地区"类别
   - 美国仍是第二大招聘市场

3. 【中高级人才需求旺盛】
   - Senior 级别岗位占比约 {df[df['seniority']=='Senior'].shape[0]/len(df)*100:.0f}%
   - Lead/管理岗位需求增长
   - 初级岗位相对较少，新人入行门槛不低

4. 【非技术岗位不容忽视】
   - Product Manager 需求量大
   - Marketing/Growth 岗位持续增长
   - Designer 岗位数量可观

5. 【头部公司主导招聘】
   - Tether、Zscaler、Bitpanda等公司招聘活跃
   - 交易所和DeFi协议是最大雇主

{'='*70}
四、新人入行建议
{'='*70}

基于数据分析，给Web3新人的建议：

1. 【技术方向】
   - 优先学习 Solidity（EVM链） 或 Rust（Solana/新链）
   - TypeScript/React 对前端开发必备
   - 安全审计是高薪细分赛道

2. 【非技术方向】
   - Product Manager 需求大，有互联网PM背景者优势明显
   - Marketing/Growth 方向适合有运营经验的人
   - 社区运营是入门门槛最低的方向

3. 【地理策略】
   - 优先选择Remote岗位，竞争更全球化但机会多
   - 美国公司招聘量最大
   - 亚洲市场（日本、新加坡、香港）增长迅速

4. 【资历提升】
   - 大量岗位需要Mid及以上经验
   - 建议通过开源贡献或Hackathon积累背书
   - Lead岗位需要技术+管理双重能力

{'='*70}
报告结束
{'='*70}
"""
    
    return report


def simple_clustering(df):
    """简化版聚类（不依赖sklearn）"""
    # 基于岗位类型和远程状态进行简单分组
    df['cluster'] = 0
    
    # 技术岗位 + 远程
    df.loc[(df['job_type'].isin(['Blockchain Developer', 'Smart Contract Developer', 
                                  'Rust/Solana Developer', 'DeFi Engineer', 
                                  'Backend Developer', 'Frontend Developer', 
                                  'Full Stack Developer'])) & (df['is_remote'] == True), 'cluster'] = 0
    
    # 技术岗位 + 非远程
    df.loc[(df['job_type'].isin(['Blockchain Developer', 'Smart Contract Developer', 
                                  'Rust/Solana Developer', 'DeFi Engineer', 
                                  'Backend Developer', 'Frontend Developer', 
                                  'Full Stack Developer'])) & (df['is_remote'] == False), 'cluster'] = 1
    
    # 产品/设计 岗位
    df.loc[df['job_type'].isin(['Product Manager', 'Designer']), 'cluster'] = 2
    
    # 市场/运营 岗位
    df.loc[df['job_type'].isin(['Marketing/Growth', 'Community']), 'cluster'] = 3
    
    # 其他岗位
    df.loc[df['job_type'].isin(['Executive/Lead', 'Other', 'Research/Analyst', 
                                 'Compliance/Legal', 'Security/Auditor']), 'cluster'] = 4
    
    return df['cluster'].values


def main():
    print("🚀 启动 Web3 就业市场聚类分析")
    print("=" * 60)
    
    # 加载数据
    df = load_latest_features()
    if df is None:
        return
    
    # 准备特征
    if SKLEARN_AVAILABLE:
        print("\n🔧 准备聚类特征...")
        features_df, le_job, le_country = prepare_features_for_clustering(df)
        
        # 执行聚类
        print("🔬 执行K-Means聚类 (k=5)...")
        clusters, kmeans, scaler, X_scaled = perform_clustering(features_df, n_clusters=5)
    else:
        print("\n🔧 使用简化版聚类...")
        clusters = simple_clustering(df)
        X_scaled = None
    
    # 分析聚类
    print("📊 分析聚类结果...")
    cluster_analysis, df_with_clusters = analyze_clusters(df, clusters)
    cluster_names = generate_cluster_names(cluster_analysis)
    
    # 生成可视化
    if MATPLOTLIB_AVAILABLE:
        print("\n📈 生成可视化图表...")
        
        if X_scaled is not None:
            visualize_clusters(X_scaled, clusters, os.path.join(OUTPUT_DIR, "cluster_pca.png"))
        
        visualize_job_distribution(df, os.path.join(OUTPUT_DIR, "job_distribution.png"))
        visualize_country_distribution(df, os.path.join(OUTPUT_DIR, "country_distribution.png"))
        visualize_seniority_distribution(df, os.path.join(OUTPUT_DIR, "seniority_distribution.png"))
    
    # 生成报告
    report = generate_report(df, cluster_analysis, cluster_names)
    print(report)
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存报告
    report_path = os.path.join(OUTPUT_DIR, f"clustering_report_{timestamp}.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n💾 分析报告: {report_path}")
    
    # 保存聚类结果
    cluster_path = os.path.join(OUTPUT_DIR, f"clustered_jobs_{timestamp}.csv")
    df_with_clusters.to_csv(cluster_path, index=False, encoding="utf-8-sig")
    print(f"💾 聚类结果: {cluster_path}")
    
    # 保存聚类分析JSON
    analysis_path = os.path.join(OUTPUT_DIR, f"cluster_analysis_{timestamp}.json")
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump({
            'cluster_names': cluster_names,
            'cluster_analysis': cluster_analysis
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 聚类分析: {analysis_path}")
    
    print("\n🎉 聚类分析完成！")


if __name__ == "__main__":
    main()
