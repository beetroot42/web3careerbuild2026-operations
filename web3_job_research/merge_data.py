"""
合并多次爬取的数据，达到500+条记录
"""

import pandas as pd
import json
import os
from datetime import datetime
from collections import Counter

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def merge_all_data():
    """合并所有爬取的数据"""
    
    # 找到所有CSV特征文件
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv') and 'features' in f]
    
    print(f"📂 找到 {len(csv_files)} 个特征文件:")
    for f in csv_files:
        print(f"  - {f}")
    
    # 合并所有DataFrame
    all_dfs = []
    for csv_file in csv_files:
        filepath = os.path.join(DATA_DIR, csv_file)
        try:
            df = pd.read_csv(filepath)
            print(f"  ✅ {csv_file}: {len(df)} 条")
            all_dfs.append(df)
        except Exception as e:
            print(f"  ❌ {csv_file}: 读取失败 - {e}")
    
    if not all_dfs:
        print("❌ 没有找到有效数据")
        return None
    
    # 合并
    merged_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\n📊 合并前总数: {len(merged_df)}")
    
    # 去重 (基于 title + company)
    # 先填充空值
    merged_df['title'] = merged_df['title'].fillna('')
    merged_df['company'] = merged_df['company'].fillna('')
    
    # 创建去重键
    merged_df['_dedup_key'] = merged_df['title'].str.lower().str.strip() + '_' + merged_df['company'].str.lower().str.strip()
    
    # 去重
    merged_df = merged_df.drop_duplicates(subset=['_dedup_key'], keep='first')
    merged_df = merged_df.drop(columns=['_dedup_key'])
    
    print(f"📊 去重后总数: {len(merged_df)}")
    
    return merged_df


def generate_final_statistics(df):
    """生成最终统计"""
    total = len(df)
    
    stats = {
        "total_jobs": total,
        "merged_at": datetime.now().isoformat(),
    }
    
    # 各维度统计
    if 'source' in df.columns:
        stats["by_source"] = df["source"].value_counts().to_dict()
    
    if 'job_type' in df.columns:
        stats["by_job_type"] = df["job_type"].value_counts().to_dict()
    
    if 'seniority' in df.columns:
        stats["by_seniority"] = df["seniority"].value_counts().to_dict()
    
    if 'country' in df.columns:
        stats["by_country"] = df["country"].value_counts().to_dict()
    
    if 'is_remote' in df.columns:
        stats["remote_ratio"] = round(df["is_remote"].mean() * 100, 1)
    
    # 打印统计
    print("\n" + "=" * 60)
    print("📊 合并数据最终统计")
    print("=" * 60)
    print(f"📋 总职位数: {total}")
    
    if 'is_remote' in df.columns:
        print(f"🏠 远程岗位比例: {stats.get('remote_ratio', 0)}%")
    
    if 'job_type' in df.columns:
        print("\n📈 岗位类型分布 (Top 15):")
        for job_type, count in list(stats["by_job_type"].items())[:15]:
            pct = count / total * 100
            bar = "█" * int(pct / 2)
            print(f"  {job_type}: {count} ({pct:.1f}%) {bar}")
    
    if 'seniority' in df.columns:
        print("\n📊 资历级别分布:")
        for level, count in stats["by_seniority"].items():
            pct = count / total * 100
            print(f"  {level}: {count} ({pct:.1f}%)")
    
    if 'country' in df.columns:
        print("\n🌍 地区分布 (Top 10):")
        for country, count in list(stats["by_country"].items())[:10]:
            pct = count / total * 100
            print(f"  • {country}: {count} ({pct:.1f}%)")
    
    print("=" * 60)
    
    return stats


def main():
    print("🔄 合并所有爬取数据...")
    print("=" * 60)
    
    # 合并数据
    merged_df = merge_all_data()
    
    if merged_df is None:
        return
    
    # 生成统计
    stats = generate_final_statistics(merged_df)
    
    # 保存合并后的数据
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存CSV
    merged_csv = os.path.join(DATA_DIR, f"merged_all_jobs_{timestamp}.csv")
    merged_df.to_csv(merged_csv, index=False, encoding="utf-8-sig")
    print(f"\n✅ 合并CSV: {merged_csv}")
    
    # 保存统计
    stats_file = os.path.join(DATA_DIR, f"merged_stats_{timestamp}.json")
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"✅ 统计JSON: {stats_file}")
    
    print(f"\n🎉 数据合并完成! 总计 {len(merged_df)} 条职位数据")


if __name__ == "__main__":
    main()
