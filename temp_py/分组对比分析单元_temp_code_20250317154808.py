import pandas as pd
import numpy as np
import os
from datetime import datetime

def load_data(file_path):
    """加载CSV文件数据"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共{len(df)}行，{len(df.columns)}列")
        return df
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

def analyze_column_distribution(df):
    """分析数值列和分类列的分布"""
    result = []
    result.append("=" * 80)
    result.append("列分布分析")
    result.append("=" * 80)
    
    # 分析分类列
    categorical_cols = df.select_dtypes(include=['object']).columns
    result.append("\n分类列分析:")
    for col in categorical_cols:
        result.append(f"\n列名: {col}")
        value_counts = df[col].value_counts()
        total = len(df)
        result.append(f"  唯一值数量: {len(value_counts)}")
        result.append(f"  缺失值数量: {df[col].isna().sum()}")
        result.append("  前5个最常见值:")
        for val, count in value_counts.head(5).items():
            result.append(f"    - {val}: {count} ({count/total*100:.2f}%)")
    
    # 分析数值列
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    result.append("\n数值列分析:")
    for col in numeric_cols:
        result.append(f"\n列名: {col}")
        result.append(f"  缺失值数量: {df[col].isna().sum()}")
        result.append(f"  最小值: {df[col].min()}")
        result.append(f"  最大值: {df[col].max()}")
        result.append(f"  平均值: {df[col].mean():.2f}")
        result.append(f"  中位数: {df[col].median()}")
        result.append(f"  标准差: {df[col].std():.2f}")
        
    return "\n".join(result)

def group_comparison(df):
    """对数据进行分组统计，比较不同组之间的差异"""
    result = []
    result.append("\n" + "=" * 80)
    result.append("分组对比分析")
    result.append("=" * 80)
    
    # 检查必要的列是否存在
    required_columns = ['Region', 'Complaint_Type', 'Resolution_Time_Days', 'Customer_Satisfaction']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        result.append(f"\n警告：缺少必要的列: {', '.join(missing_columns)}")
        return "\n".join(result)
    
    # 按区域分组分析
    result.append("\n按区域(Region)分组分析:")
    region_group = df.groupby('Region')
    region_stats = region_group[['Resolution_Time_Days', 'Customer_Satisfaction']].agg(['count', 'mean', 'median'])
    
    result.append("\n解决时间(天)统计:")
    for region in region_stats.index:
        count = region_stats.loc[region, ('Resolution_Time_Days', 'count')]
        mean = region_stats.loc[region, ('Resolution_Time_Days', 'mean')]
        median = region_stats.loc[region, ('Resolution_Time_Days', 'median')]
        result.append(f"  {region}: 数量={count}, 平均={mean:.2f}, 中位数={median:.2f}")
    
    result.append("\n客户满意度统计:")
    for region in region_stats.index:
        count = region_stats.loc[region, ('Customer_Satisfaction', 'count')]
        mean = region_stats.loc[region, ('Customer_Satisfaction', 'mean')]
        median = region_stats.loc[region, ('Customer_Satisfaction', 'median')]
        result.append(f"  {region}: 数量={count}, 平均={mean:.2f}, 中位数={median:.2f}")
    
    # 按投诉类型分组分析
    result.append("\n按投诉类型(Complaint_Type)分组分析:")
    complaint_group = df.groupby('Complaint_Type')
    complaint_stats = complaint_group[['Resolution_Time_Days', 'Customer_Satisfaction']].agg(['count', 'mean', 'median'])
    
    result.append("\n解决时间(天)统计:")
    for complaint in complaint_stats.index:
        count = complaint_stats.loc[complaint, ('Resolution_Time_Days', 'count')]
        mean = complaint_stats.loc[complaint, ('Resolution_Time_Days', 'mean')]
        median = complaint_stats.loc[complaint, ('Resolution_Time_Days', 'median')]
        result.append(f"  {complaint}: 数量={count}, 平均={mean:.2f}, 中位数={median:.2f}")
    
    result.append("\n客户满意度统计:")
    for complaint in complaint_stats.index:
        count = complaint_stats.loc[complaint, ('Customer_Satisfaction', 'count')]
        mean = complaint_stats.loc[complaint, ('Customer_Satisfaction', 'mean')]
        median = complaint_stats.loc[complaint, ('Customer_Satisfaction', 'median')]
        result.append(f"  {complaint}: 数量={count}, 平均={mean:.2f}, 中位数={median:.2f}")
    
    return "\n".join(result)

def main():
    """主函数"""
    # 示例用法
    file_path = input("请输入CSV文件路径: ")
    if os.path.exists(file_path):
        df = load_data(file_path)
        if df is not None:
            print(analyze_column_distribution(df))
            print(group_comparison(df))
    else:
        print("文件不存在，请检查路径")

if __name__ == "__main__":
    main()