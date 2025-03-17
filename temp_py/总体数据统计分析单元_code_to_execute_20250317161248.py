import pandas as pd
import os
import numpy as np
from datetime import datetime

def analyze_csv_data(file_path, output_path):
    """
    分析CSV文件并将结果保存为纯文本格式
    
    Args:
        file_path (str): CSV文件路径
        output_path (str): 输出文本文件路径
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")

        # 读取CSV文件
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 打开输出文件
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入基本信息
            f.write("=" * 80 + "\n")
            f.write(f"网络数据分析报告\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"数据源文件: {file_path}\n")
            f.write("=" * 80 + "\n\n")
            
            # 1. 数据集基本信息
            f.write("1. 数据集基本信息\n")
            f.write("-" * 50 + "\n")
            f.write(f"总行数: {len(df)}\n")
            f.write(f"总列数: {len(df.columns)}\n")
            f.write(f"数据集内存占用: {df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB\n\n")
            
            # 2. 数据类型概览
            f.write("2. 数据类型概览\n")
            f.write("-" * 50 + "\n")
            dtypes_info = {}
            for dtype in df.dtypes.unique():
                dtypes_info[str(dtype)] = sum(df.dtypes == dtype)
            
            for dtype, count in dtypes_info.items():
                f.write(f"{dtype}: {count} 列\n")
            f.write("\n")
            
            # 3. 时间分析 (假设Timestamp是正确的时间戳格式)
            f.write("3. 时间范围分析\n")
            f.write("-" * 50 + "\n")
            try:
                # 将Timestamp列转换为日期时间格式
                if 'Timestamp' in df.columns:
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                    f.write(f"时间范围: {df['Timestamp'].min()} 至 {df['Timestamp'].max()}\n")
                    f.write(f"数据跨度: {(df['Timestamp'].max() - df['Timestamp'].min()).days + 1} 天\n\n")
            except Exception as e:
                f.write(f"时间分析出错: {str(e)}\n\n")
            
            # 4. 分类变量分析
            categorical_columns = ['Region', 'Service_Type', 'Network_Type']
            f.write("4. 分类变量分析\n")
            f.write("-" * 50 + "\n")
            
            for col in categorical_columns:
                if col in df.columns:
                    f.write(f"{col} 分布:\n")
                    value_counts = df[col].value_counts()
                    for value, count in value_counts.items():
                        percentage = count / len(df) * 100
                        f.write(f"  - {value}: {count} 条记录 ({percentage:.2f}%)\n")
                    f.write("\n")
            
            # 5. 数值变量分析
            numeric_columns = ['Traffic_Volume_GB', 'Active_Users', 'Bandwidth_Utilization_Percent', 
                              'Average_Speed_Mbps', 'Peak_Speed_Mbps', 'Congestion_Level']
            
            f.write("5. 数值变量统计分析\n")
            f.write("-" * 50 + "\n")
            
            for col in numeric_columns:
                if col in df.columns:
                    f.write(f"{col} 统计:\n")
                    f.write(f"  - 最小值: {df[col].min():.2f}\n")
                    f.write(f"  - 最大值: {df[col].max():.2f}\n")
                    f.write(f"  - 平均值: {df[col].mean():.2f}\n")
                    f.write(f"  - 中位数: {df[col].median():.2f}\n")
                    f.write(f"  - 标准差: {df[col].std():.2f}\n")
                    
                    # 百分位数
                    percentiles = [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
                    perc_values = np.percentile(df[col].dropna(), [p*100 for p in percentiles])
                    f.write(f"  - 百分位数:\n")
                    for p, val in zip(percentiles, perc_values):
                        f.write(f"      {int(p*100) if p*100 == int(p*100) else p*100}%: {val:.2f}\n")
                    f.write("\n")
            
            # 6. 按区域和网络类型的统计
            f.write("6. 按区域和网络类型的流量分析\n")
            f.write("-" * 50 + "\n")
            
            if all(col in df.columns for col in ['Region', 'Network_Type', 'Traffic_Volume_GB']):
                # 按区域和网络类型计算平均流量
                region_network_stats = df.groupby(['Region', 'Network_Type'])['Traffic_Volume_GB'].agg(
                    ['mean', 'sum', 'count']).reset_index()
                
                for _, row in region_network_stats.iterrows():
                    region = row['Region']
                    network = row['Network_Type']
                    avg_traffic = row['mean']
                    total_traffic = row['sum']
                    record_count = row['count']
                    
                    f.write(f"区域: {region}, 网络类型: {network}\n")
                    f.write(f"  - 平均流量: {avg_traffic:.2f} GB\n")
                    f.write(f"  - 总流量: {total_traffic:.2f} GB\n")
                    f.write(f"  - 记录数: {record_count}\n")
                f.write("\n")
            
            # 7. 按服务类型的统计
            f.write("7. 按服务类型的性能分析\n")
            f.write("-" * 50 + "\n")
            
            if all(col in df.columns for col in ['Service_Type', 'Average_Speed_Mbps', 'Congestion_Level']):
                service_stats = df.groupby('Service_Type').agg({
                    'Average_Speed_Mbps': ['mean', 'min', 'max'],
                    'Congestion_Level': ['mean', 'min', 'max'],
                    'Traffic_Volume_GB': ['sum', 'mean']
                }).reset_index()
                
                for _, row in service_stats.iterrows():
                    service = row[('Service_Type', '')]
                    avg_speed = row[('Average_Speed_Mbps', 'mean')]
                    avg_congestion = row[('Congestion_Level', 'mean')]
                    total_traffic = row[('Traffic_Volume_GB', 'sum')]
                    
                    f.write(f"服务类型: {service}\n")
                    f.write(f"  - 平均速度: {avg_speed:.2f} Mbps\n")
                    f.write(f"  - 平均拥塞度: {avg_congestion:.2f}%\n")
                    f.write(f"  - 总流量: {total_traffic:.2f} GB\n")
                f.write("\n")
            
            # 8. 高峰期分析
            f.write("8. 网络高峰期分析\n")
            f.write("-" * 50 + "\n")
            
            if 'Timestamp' in df.columns and 'Traffic_Volume_GB' in df.columns:
                try:
                    # 提取小时
                    df['Hour'] = df['Timestamp'].dt.hour
                    
                    # 按小时统计平均流量
                    hourly_traffic = df.groupby('Hour')['Traffic_Volume_GB'].mean().reset_index()
                    peak_hour = hourly_traffic.loc[hourly_traffic['Traffic_Volume_GB'].idxmax()]['Hour']
                    off_peak_hour = hourly_traffic.loc[hourly_traffic['Traffic_Volume_GB'].idxmin()]['Hour']
                    
                    f.write(f"流量高峰时段: {peak_hour}:00\n")
                    f.write(f"流量低谷时段: {off_peak_hour}:00\n")
                    
                    # 列出各小时平均流量
                    f.write("各小时平均流量:\n")
                    for _, row in hourly_traffic.iterrows():
                        hour = row['Hour']
                        traffic = row['Traffic_Volume_GB']
                        f.write(f"  - {hour}:00: {traffic:.2f} GB\n")
                    f.write("\n")
                except Exception as e:
                    f.write(f"高峰期分析出错: {str(e)}\n\n")
            
            # 9. 总结
            f.write("9. 分析总结\n")
            f.write("-" * 50 + "\n")
            
            # 计算一些关键指标
            if all(col in df.columns for col in numeric_columns):
                avg_traffic = df['Traffic_Volume_GB'].mean()
                avg_users = df['Active_Users'].mean()
                avg_bandwidth = df['Bandwidth_Utilization_Percent'].mean()
                avg_speed = df['Average_Speed_Mbps'].mean()
                avg_congestion = df['Congestion_Level'].mean()
                
                f.write(f"数据集包含 {len(df)} 条网络性能记录，涵盖多个区域和服务类型。\n")
                f.write(f"平均流量为 {avg_traffic:.2f} GB，平均活跃用户数为 {avg_users:.2f}。\n")
                f.write(f"网络带宽利用率平均为 {avg_bandwidth:.2f}%，平均速度为 {avg_speed:.2f} Mbps。\n")
                f.write(f"网络拥塞度平均为 {avg_congestion:.2f}%。\n\n")
                
                # 如果存在高拥塞情况，进行说明
                high_congestion = df[df['Congestion_Level'] > 80]
                if len(high_congestion) > 0:
                    high_cong_percent = len(high_congestion) / len(df) * 100
                    f.write(f"高拥塞情况（拥塞度>80%）占总记录的 {high_cong_percent:.2f}%。\n")
                
            f.write("\n分析完成。")
        
        print(f"分析完成，结果已保存至: {output_path}")
        return True
    
    except Exception as e:
        print(f"分析过程出错: {str(e)}")
        return False

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317161158.csv"
    output_path = "pngs/analysis_results.txt"
    analyze_csv_data(file_path, output_path)