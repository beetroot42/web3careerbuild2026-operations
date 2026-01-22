"""
Web3 薪资可视化脚本
生成薪资分析相关图表
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 输出目录
OUTPUT_DIR = 'analysis_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 配色方案
COLORS = {
    'primary': '#6366f1',      # 紫色
    'secondary': '#22d3ee',    # 青色
    'accent': '#f59e0b',       # 橙色
    'success': '#10b981',      # 绿色
    'danger': '#ef4444',       # 红色
    'dark': '#1e293b',
    'light': '#f8fafc'
}

def create_salary_by_role_chart():
    """创建各岗位薪资对比图"""
    
    roles = [
        'Smart Contract Dev',
        'Rust/Solana Dev',
        'DeFi Engineer',
        'Blockchain Dev',
        'Frontend Dev',
        'Product Manager',
        'Designer',
        'Marketing/Growth',
        'Community'
    ]
    
    # 薪资数据 (Mid级别中位数, 单位: $k)
    junior_low = [80, 90, 80, 70, 60, 70, 50, 40, 30]
    junior_high = [120, 130, 120, 110, 90, 100, 80, 70, 50]
    mid_low = [120, 130, 120, 110, 90, 100, 80, 70, 50]
    mid_high = [180, 200, 180, 160, 140, 150, 120, 110, 80]
    senior_low = [180, 200, 180, 160, 140, 150, 120, 110, 80]
    senior_high = [300, 350, 300, 250, 200, 220, 180, 160, 120]
    
    # 计算中位数
    mid_median = [(l + h) / 2 for l, h in zip(mid_low, mid_high)]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 设置背景
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#1e293b')
    
    y_pos = np.arange(len(roles))
    
    # 绘制薪资范围条
    colors_gradient = plt.cm.viridis(np.linspace(0.3, 0.9, len(roles)))
    
    for i, (role, low, high) in enumerate(zip(roles, mid_low, mid_high)):
        # 绘制范围条
        ax.barh(i, high - low, left=low, height=0.6, 
                color=colors_gradient[i], alpha=0.8, edgecolor='white', linewidth=0.5)
        # 添加中位数标记
        median = (low + high) / 2
        ax.scatter(median, i, color='white', s=80, zorder=5, marker='|', linewidths=2)
        # 添加数值标签
        ax.text(high + 5, i, f'${low}k - ${high}k', 
                va='center', ha='left', color='white', fontsize=10, fontweight='bold')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(roles, fontsize=11, color='white')
    ax.set_xlabel('年薪 (USD, thousands)', fontsize=12, color='white', labelpad=10)
    ax.set_title('Web3 各岗位薪资范围 (Mid级别)', fontsize=16, color='white', pad=20, fontweight='bold')
    
    # 设置网格
    ax.xaxis.grid(True, linestyle='--', alpha=0.3, color='white')
    ax.set_axisbelow(True)
    
    # 设置坐标轴颜色
    ax.tick_params(axis='x', colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlim(0, 250)
    
    # 添加注释
    ax.text(0.02, -0.08, '📊 数据来源: Web3.career, Glassdoor, 行业报告 | 2026年1月', 
            transform=ax.transAxes, fontsize=9, color='#94a3b8')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/salary_by_role.png', dpi=150, facecolor='#0f172a', 
                edgecolor='none', bbox_inches='tight')
    plt.close()
    print("✅ 已生成: salary_by_role.png")


def create_salary_by_seniority_chart():
    """创建资历级别薪资对比图"""
    
    levels = ['Junior\n(0-2年)', 'Mid\n(2-4年)', 'Senior\n(4年+)', 'Lead\n(管理层)']
    
    # 技术岗 vs 非技术岗薪资
    tech_low = [80, 120, 180, 200]
    tech_high = [130, 200, 350, 400]
    non_tech_low = [35, 60, 100, 130]
    non_tech_high = [70, 110, 160, 200]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 设置背景
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#1e293b')
    
    x = np.arange(len(levels))
    width = 0.35
    
    # 计算误差条
    tech_mid = [(l + h) / 2 for l, h in zip(tech_low, tech_high)]
    tech_err = [(h - l) / 2 for l, h in zip(tech_low, tech_high)]
    non_tech_mid = [(l + h) / 2 for l, h in zip(non_tech_low, non_tech_high)]
    non_tech_err = [(h - l) / 2 for l, h in zip(non_tech_low, non_tech_high)]
    
    # 绘制柱状图
    bars1 = ax.bar(x - width/2, tech_mid, width, label='核心技术岗\n(智能合约/Rust/区块链)', 
                   color='#6366f1', edgecolor='white', linewidth=1)
    bars2 = ax.bar(x + width/2, non_tech_mid, width, label='非技术岗\n(Marketing/Community)', 
                   color='#22d3ee', edgecolor='white', linewidth=1)
    
    # 添加误差条
    ax.errorbar(x - width/2, tech_mid, yerr=tech_err, fmt='none', 
                ecolor='white', capsize=5, capthick=2, alpha=0.7)
    ax.errorbar(x + width/2, non_tech_mid, yerr=non_tech_err, fmt='none', 
                ecolor='white', capsize=5, capthick=2, alpha=0.7)
    
    # 添加数值标签
    for bar, mid in zip(bars1, tech_mid):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15, 
                f'${int(mid)}k', ha='center', va='bottom', color='white', 
                fontsize=10, fontweight='bold')
    
    for bar, mid in zip(bars2, non_tech_mid):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15, 
                f'${int(mid)}k', ha='center', va='bottom', color='white', 
                fontsize=10, fontweight='bold')
    
    ax.set_ylabel('年薪中位数 (USD, thousands)', fontsize=12, color='white')
    ax.set_title('Web3 技术岗 vs 非技术岗薪资对比', fontsize=16, color='white', pad=20, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(levels, fontsize=11, color='white')
    
    # 设置图例
    legend = ax.legend(loc='upper left', fontsize=10, facecolor='#334155', 
                       edgecolor='white', labelcolor='white')
    
    # 设置网格
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='white')
    ax.set_axisbelow(True)
    
    # 设置坐标轴颜色
    ax.tick_params(axis='both', colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_ylim(0, 320)
    
    # 添加倍数标注
    ax.annotate('', xy=(3 - width/2, 300), xytext=(3 + width/2, 165),
                arrowprops=dict(arrowstyle='<->', color='#f59e0b', lw=2))
    ax.text(3, 240, '~2x', fontsize=14, color='#f59e0b', fontweight='bold', ha='center')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/salary_tech_vs_nontech.png', dpi=150, facecolor='#0f172a', 
                edgecolor='none', bbox_inches='tight')
    plt.close()
    print("✅ 已生成: salary_tech_vs_nontech.png")


def create_competition_vs_salary_chart():
    """创建竞争程度vs薪资散点图"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 设置背景
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#1e293b')
    
    # 数据：岗位占比, 薪资中位数, 类别
    data = [
        ('Junior', 3.8, 65, '⭐⭐⭐⭐⭐ 极高竞争'),
        ('Mid', 58.5, 115, '⭐⭐⭐ 中等竞争'),
        ('Senior', 24.4, 185, '⭐⭐ 较低竞争'),
        ('Lead', 13.4, 230, '⭐⭐ 较低竞争'),
    ]
    
    colors = ['#ef4444', '#f59e0b', '#10b981', '#6366f1']
    sizes = [200, 800, 500, 350]
    
    for i, (label, ratio, salary, comp) in enumerate(data):
        ax.scatter(ratio, salary, s=sizes[i], c=colors[i], alpha=0.8, 
                   edgecolors='white', linewidths=2, zorder=5)
        
        # 添加标签
        offset_x = 2 if i == 0 else 3
        offset_y = 15 if i != 1 else -20
        ax.annotate(f'{label}\n{comp}', 
                    xy=(ratio, salary), 
                    xytext=(ratio + offset_x, salary + offset_y),
                    fontsize=10, color='white', fontweight='bold',
                    ha='left', va='center',
                    arrowprops=dict(arrowstyle='->', color='white', alpha=0.5))
    
    ax.set_xlabel('岗位占比 (%)', fontsize=12, color='white', labelpad=10)
    ax.set_ylabel('薪资中位数 ($k/年)', fontsize=12, color='white', labelpad=10)
    ax.set_title('Web3 岗位竞争程度 vs 薪资水平', fontsize=16, color='white', pad=20, fontweight='bold')
    
    # 设置网格
    ax.grid(True, linestyle='--', alpha=0.3, color='white')
    ax.set_axisbelow(True)
    
    # 设置坐标轴颜色
    ax.tick_params(axis='both', colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlim(0, 70)
    ax.set_ylim(0, 300)
    
    # 添加趋势说明
    ax.text(0.95, 0.05, '💡 Junior岗位少但竞争激烈\nSenior/Lead岗位多且薪资高', 
            transform=ax.transAxes, fontsize=10, color='#94a3b8',
            ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#334155', edgecolor='#475569'))
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/competition_vs_salary.png', dpi=150, facecolor='#0f172a', 
                edgecolor='none', bbox_inches='tight')
    plt.close()
    print("✅ 已生成: competition_vs_salary.png")


def create_top_companies_salary_chart():
    """创建头部公司薪资对比图"""
    
    companies = ['Coinbase', 'OpenSea', 'Uniswap', 'Alchemy', 'Consensys', 'Binance']
    
    # Senior工程师薪资范围 (low, high)
    salaries_low = [200, 180, 180, 170, 160, 150]
    salaries_high = [350, 300, 300, 280, 250, 280]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 设置背景
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#1e293b')
    
    y_pos = np.arange(len(companies))
    
    # 渐变色
    colors = plt.cm.plasma(np.linspace(0.2, 0.8, len(companies)))
    
    for i, (company, low, high) in enumerate(zip(companies, salaries_low, salaries_high)):
        # 绘制范围条
        ax.barh(i, high - low, left=low, height=0.6, 
                color=colors[i], alpha=0.9, edgecolor='white', linewidth=1)
        # 添加数值
        ax.text(high + 5, i, f'${low}k - ${high}k', 
                va='center', ha='left', color='white', fontsize=11, fontweight='bold')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(companies, fontsize=12, color='white', fontweight='bold')
    ax.set_xlabel('年薪 (USD, thousands)', fontsize=12, color='white', labelpad=10)
    ax.set_title('🏢 Web3 头部公司 Senior 工程师薪资', fontsize=16, color='white', pad=20, fontweight='bold')
    
    # 设置网格
    ax.xaxis.grid(True, linestyle='--', alpha=0.3, color='white')
    ax.set_axisbelow(True)
    
    # 设置坐标轴颜色
    ax.tick_params(axis='both', colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlim(100, 420)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/top_companies_salary.png', dpi=150, facecolor='#0f172a', 
                edgecolor='none', bbox_inches='tight')
    plt.close()
    print("✅ 已生成: top_companies_salary.png")


if __name__ == '__main__':
    print("\n" + "="*50)
    print("📊 生成 Web3 薪资可视化图表")
    print("="*50 + "\n")
    
    create_salary_by_role_chart()
    create_salary_by_seniority_chart()
    create_competition_vs_salary_chart()
    create_top_companies_salary_chart()
    
    print("\n" + "="*50)
    print(f"✅ 所有图表已保存到: {OUTPUT_DIR}/")
    print("="*50)
