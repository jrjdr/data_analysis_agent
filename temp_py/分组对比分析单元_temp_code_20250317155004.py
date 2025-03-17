import pandas as pd
import numpy as np
import os
import time
from datetime import datetime

def load_data(file_path):
    """加载CSV文件数据"""
    try:
        # 添加低内存模式选项，适用于大文件
        df = pd.read_csv(file_path, low_memory=False)
        print(f"成功加载数据，共{len(df)}行，{len(df.columns)}列")
        return df
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

def analyze_column_distribution(df, sample_size=None):
    """分析数值列和分类列的分布，可选择使用样本数据"""
    start_time = time.time()
    result = []
    result.append("=" * 80)
    result.append("列分布分析")
    result.append("=" * 80)
    
    # 如果数据量大，使用样本
    if sample_size and len(df) > sample_size:
        df_sample = df.sample(sample_size, random_state=42)
        result.append(f"\n注意: 使用{sample_size}行样本数据进行分析")
    else:
        df_sample = df
    
    # 分析分类列
    categorical_cols = df_sample.select_dtypes(include=['object']).columns
    result.append("\n分类列分析:")
    for col in categorical_cols:
        # 检查处理时间，防止单列分析时间过长
        if time.time() - start_time > 30:
            result.append("\n警告: 分析时间过长，部分列分析被跳过")
            break
            
        result.append(f"\n列名: {col}")
        # 使用value_counts()的dropna参数处理缺失值
        value_counts = df_sample[col].value_counts(dropna=False)
        total = len(df_sample)
        result.append(f"  唯一值数量: {df_sample[col].nunique()}")
        result.append(f"  缺失值数量: {df_sample[col].isna().sum()}")
        result.append("  前5个最常见值:")
        # 限制处理的项目数
        for i, (val, count) in enumerate(value_counts.head(5).items()):
            val_str = str(val) if pd.notna(val) else "NaN"
            result.append(f"    - {val_str}: {count} ({count/total*100:.2f}%)")
    
    # 分析数值列
    numeric_cols = df_sample.select_dtypes(include=['int64', 'float64']).columns
    result.append("\n数值列分析:")
    for col in numeric_cols:
        # 检查处理时间
        if time.time() - start_time > 45:
            result.append("\n警告: 分析时间过长，部分列分析被跳过")
            break
            
        result.append(f"\n列名: {col}")
        result.append(f"  缺失值数量: {df_sample[col].isna().sum()}")
        # 使用try-except处理可能的错误
        try:
            result.append(f"  最小值: {df_sample[col].min()}")
            result.append(f"  最大值: {df_sample[col].max()}")
            result.append(f"  平均值: {df_sample[col].mean():.2f}")
            result.append(f"  中位数: {df_sample[col].median()}")
            result.append(f"  标准差: {df_sample[col].std():.2f}")
        except Exception as e:
            result.append(f"  计算统计数据时出错: {e}")
        
    return "\n".join(result)

def group_comparison(df, max_groups=10):
    """对数据进行分组统计，比较不同组之间的差异"""
    start_time = time.time()
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
    try:
        # 获取唯一区域值并限制数量
        unique_regions = df['Region'].value_counts().head(max_groups).index
        filtered_df = df[df['Region'].isin(unique_regions)]
        
        region_group = filtered_df.groupby('Region')
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
    except Exception as e:
        result.append(f"\n区域分组分析出错: {e}")
    
    # 检查是否超时
    if time.time() - start_time > 30:
        result.append("\n警告: 分析时间过长，跳过投诉类型分析")
        return "\n".join(result)
    
    # 按投诉类型分组分析
    result.append("\n按投诉类型(Complaint_Type)分组分析:")
    try:
        # 获取唯一投诉类型并限制数量
        unique_complaints = df['Complaint_Type'].value_counts().head(max_groups).index
        filtered_df = df[df['Complaint_Type'].isin(unique_complaints)]
        
        complaint_group = filtered_df.groupby('Complaint_Type')
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
    except Exception as e:
        result.append(f"\n投诉类型分组分析出错: {e}")
    
    return "\n".join(result)

def main():
    """主函数"""
    # 设置全局超时
    global_start_time = time.time()
    max_execution_time = 55  # 设置最大执行时间为55秒
    
    # 示例用法
    file_path = input("请输入CSV文件路径: ")
    if os.path.exists(file_path):
        df = load_data(file_path)
        if df is not None:
            # 检查数据大小，决定是否使用样本
            sample_size = 10000 if len(df) > 10000 else None
            
            # 检查是否超时
            if time.time() - global_start_time < max_execution_time:
                print(analyze_column_distribution(df, sample_size))
            else:
                print("警告: 执行时间过长，跳过列分布分析")
            
            # 再次检查是否超时
            if time.time() - global_start_time < max_execution_time:
                print(group_comparison(df))
            else:
                print("警告: 执行时间过长，跳过分组对比分析")
    else:
        print("文件不存在，请检查路径")

if __name__ == "__main__":
    main()