"""
分析入门级岗位
"""
import pandas as pd

df = pd.read_csv('data/jobs_data.csv')

print('='*60)
print('【入门级岗位分析】')
print('='*60)

# Junior岗位
junior = df[df['seniority'] == 'Junior']
print(f'\n📊 Junior级别岗位: {len(junior)} 条 ({len(junior)/len(df)*100:.1f}%)')

# 入门友好的岗位类型
entry_friendly_types = ['Community', 'Marketing/Growth', 'Designer', 'Research/Analyst', 'QA/Testing']
entry_friendly = df[df['job_type'].isin(entry_friendly_types)]
print(f'📊 入门友好岗位类型: {len(entry_friendly)} 条')

print('\n【Junior岗位类型分布】')
if len(junior) > 0:
    for jt, count in junior['job_type'].value_counts().items():
        print(f'  • {jt}: {count}')

print('\n【Junior岗位示例】')
if len(junior) > 0:
    for _, row in junior.head(10).iterrows():
        title = row['title']
        company = row['company']
        print(f'  • {title} @ {company}')

print('\n【入门友好岗位类型分布】')
for jt, count in entry_friendly['job_type'].value_counts().items():
    pct = count / len(df) * 100
    print(f'  • {jt}: {count} ({pct:.1f}%)')

print('\n【远程 vs 非远程 (入门友好岗)】')
remote = entry_friendly[entry_friendly['is_remote'] == True]
print(f'  远程: {len(remote)} ({len(remote)/len(entry_friendly)*100:.1f}%)')
print(f'  非远程: {len(entry_friendly) - len(remote)} ({(len(entry_friendly)-len(remote))/len(entry_friendly)*100:.1f}%)')

# 新人最可能的入行路径
print('\n' + '='*60)
print('【新人入行路径分析】')
print('='*60)

# 按入门难度分类
print('\n🟢 低门槛岗位 (无需技术背景):')
low_barrier = df[df['job_type'].isin(['Community', 'Marketing/Growth'])]
print(f'   共 {len(low_barrier)} 个岗位')
for jt, count in low_barrier['job_type'].value_counts().items():
    print(f'   • {jt}: {count}')

print('\n🟡 中等门槛 (需要相关经验):')
mid_barrier = df[df['job_type'].isin(['Designer', 'Research/Analyst', 'Product Manager'])]
print(f'   共 {len(mid_barrier)} 个岗位')
for jt, count in mid_barrier['job_type'].value_counts().items():
    print(f'   • {jt}: {count}')

print('\n🔴 高门槛 (需要技术背景):')
high_barrier = df[df['job_type'].isin(['Blockchain Developer', 'Smart Contract Developer', 'Rust/Solana Developer', 'DeFi Engineer'])]
print(f'   共 {len(high_barrier)} 个岗位')
for jt, count in high_barrier['job_type'].value_counts().items():
    print(f'   • {jt}: {count}')

# 保存入门级分析
entry_level_jobs = pd.concat([junior, entry_friendly]).drop_duplicates()
entry_level_jobs.to_csv('data/entry_level_jobs.csv', index=False, encoding='utf-8-sig')
print(f'\n💾 已保存入门级岗位数据: data/entry_level_jobs.csv ({len(entry_level_jobs)} 条)')
