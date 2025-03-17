import pandas as pd
import numpy as np
import os
from datetime import datetime

def read_csv_file(file_path):
    """读取CSV文件并返回DataFrame"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功读取CSV文件，共{len(df)}行数据")
        return df
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在")
        return None
    except Exception as e:
        print(f"读取CSV文件时出错: {str(e)}")
        return None

def analyze_column_distribution(df):
    """分析数值列和分类列的分布"""
    result = []
    result.append("=== 数据列分布分析 ===\n")
    
    # 分析分类列
    categorical_cols = ['Region', 'Service_Type', 'Network_Type']
    result.append("--- 分类列分布 ---")
    
    for col in categorical_cols:
        result.append(f"\n{col}分布:")
        value_counts = df[col].value_counts()
        for value, count in value_counts.items():
            percentage = count / len(df) * 100
            result.append(f"  {value}: {count}条记录 ({percentage:.2f}%)")
    
    # 分析数值列
    numeric_cols = ['Traffic_Volume_GB', 'Active_Users', 'Bandwidth_Utilization_Percent', 
                    'Average_Speed_Mbps', 'Peak_Speed_Mbps', 'Congestion_Level']
    
    result.append("\n\n--- 数值列统计 ---")
    for col in numeric_cols:
        result.append(f"\n{col}统计:")
        result.append(f"  最小值: {df[col].min():.2f}")
        result.append(f"  最大值: {df[col].max():.2f}")
        result.append(f"  平均值: {df[col].mean():.2f}")
        result.append(f"  中位数: {df[col].median():.2f}")
        result.append(f"  标准差: {df[col].std():.2f}")
        
        # 分位数
        q25, q75 = df[col].quantile([0.25, 0.75])
        result.append(f"  25%分位数: {q25:.2f}")
        result.append(f"  75%分位数: {q75:.2f}")
    
    return "\n".join(result)

def group_comparison_analysis(df):
    """对数据进行分组统计，比较不同组之间的差异"""
    result = []
    result.append("\n\n=== 分组对比分析 ===\n")
    
    # 数值型指标
    metrics = ['Traffic_Volume_GB', 'Active_Users', 'Bandwidth_Utilization_Percent', 
              'Average_Speed_Mbps', 'Peak_Speed_Mbps', 'Congestion_Level']
    
    # 按Region分组分析
    result.append("--- 按Region分组分析 ---\n")
    region_group = df.groupby('Region')[metrics].agg(['mean', 'median', 'max'])
    result.append(format_group_results(region_group))
    
    # 按Network_Type分组分析
    result.append("\n--- 按Network_Type分组分析 ---\n")
    network_group = df.groupby('Network_Type')[metrics].agg(['mean', 'median', 'max'])
    result.append(format_group_results(network_group))
    
    # 按Service_Type分组分析
    result.append("\n--- 按Service_Type分组分析 ---\n")
    service_group = df.groupby('Service_Type')[metrics].agg(['mean', 'median', 'max'])
    result.append(format_group_results(service_group))
    
    # 交叉分组: Region x Network_Type
    result.append("\n--- 交叉分组: Region x Network_Type ---\n")
    cross_group = df.groupby(['Region', 'Network_Type'])['Traffic_Volume_GB', 'Congestion_Level'].mean()
    result.append(format_cross_group_results(cross_group))
    
    # 按时间段分组分析
    result.append("\n--- 按时间段分组分析 ---\n")
    # 确保Timestamp列是datetime类型
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Hour'] = df['Timestamp'].dt.hour
    
    # 定义时间段
    time_periods = {
        '凌晨 (00:00-05:59)': (0, 5),
        '上午 (06:00-11:59)': (6, 11),
        '下午 (12:00-17:59)': (12, 17),
        '晚上 (18:00-23:59)': (18, 23)
    }
    
    time_stats = []
    for period, (start, end) in time_periods.items():
        period_df = df[(df['Hour'] >= start) & (df['Hour'] <= end)]
        traffic_mean = period_df['Traffic_Volume_GB'].mean()
        users_mean = period_df['Active_Users'].mean()
        congestion_mean = period_df['Congestion_Level'].mean()
        
        time_stats.append(f"{period}:\n"
                          f"  平均流量: {traffic_mean:.2f} GB\n"
                          f"  平均活跃用户: {users_mean:.2f}\n"
                          f"  平均拥塞度: {congestion_mean:.2f}%")
    
    result.append("\n".join(time_stats))
    
    # 高负载分析
    result.append("\n\n--- 高负载分析 ---\n")
    high_load = df[df['Congestion_Level'] > 70]
    result.append(f"高负载记录数 (拥塞度 > 70%): {len(high_load)}条 ({len(high_load)/len(df)*100:.2f}%)")
    
    if len(high_load) > 0:
        # 高负载区域分布
        region_load = high_load['Region'].value_counts()
        result.append("\n高负载区域分布:")
        for region, count in region_load.items():
            result.append(f"  {region}: {count}条 ({count/len(high_load)*100:.2f}%)")
        
        # 高负载网络类型分布
        network_load = high_load['Network_Type'].value_counts()
        result.append("\n高负载网络类型分布:")
        for network, count in network_load.items():
            result.append(f"  {network}: {count}条 ({count/len(high_load)*100:.2f}%)")
        
        # 高负载服务类型分布
        service_load = high_load['Service_Type'].value_counts()
        result.append("\n高负载服务类型分布:")
        for service, count in service_load.items():
            result.append(f"  {service}: {count}条 ({count/len(high_load)*100:.2f}%)")
    
    return "\n".join(result)

def format_group_results(group_df):
    """格式化分组结果为可读文本"""
    result = []
    
    # 获取组索引
    groups = group_df.index.tolist()
    
    # 遍历每个指标
    for metric in group_df.columns.levels[0]:
        result.append(f"{metric}:")
        
        # 遍历每个统计量
        for stat in ['mean', 'median', 'max']:
            result.append(f"  {stat.capitalize()}:")
            
            # 遍历每个组
            for group in groups:
                value = group_df.loc[group, (metric, stat)]
                result.append(f"    {group}: {value:.2f}")
    
    return "\n".join(result)

def format_cross_group_results(cross_group):
    """格式化交叉分组结果为可读文本"""
    result = []
    
    # 重塑DataFrame以便更容易格式化
    formatted_df = cross_group.reset_index()
    
    for metric in ['Traffic_Volume_GB', 'Congestion_Level']:
        result.append(f"{metric}:")
        
        # 获取唯一的Region和Network_Type值
        regions = formatted_df['Region'].unique()
        network_types = formatted_df['Network_Type'].unique()
        
        for region in regions:
            region_data = []
            region_data.append(f"  {region}:")
            
            for network_type in network_types:
                value = formatted_df[(formatted_df['Region'] == region) & 
                                    (formatted_df['Network_Type'] == network_type)][metric]
                
                if not value.empty:
                    region_data.append(f"    {network_type}: {value.values[0]:.2f}")
            
            result.append("\n".join(region_data))
    
    return "\n".join(result)

def main(file_path, output_path):
    """主函数，执行数据分析和结果输出"""
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 读取CSV文件
    df = read_csv_file(file_path)
    if df is None:
        return
    
    try:
        # 分析列分布
        distribution_analysis = analyze_column_distribution(df)
        
        # 执行分组对比分析
        group_analysis = group_comparison_analysis(df)
        
        # 组合所有分析结果
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"网络数据分组对比分析报告\n生成时间: {current_time}\n文件: {file_path}\n记录数: {len(df)}\n\n"
        
        # 保存结果到文本文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write(distribution_analysis)
            f.write(group_analysis)
        
        print(f"分析结果已保存到 {output_path}")
    
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317161158.csv"
    output_path = "pngs/group_comparison_results.txt"
    main(file_path, output_path)