import pandas as pd
import numpy as np
import os
from datetime import datetime

def analyze_csv_data(file_path, output_path):
    try:
        # 1. 读取CSV文件
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入分析报告标题和基本信息
            f.write("=" * 80 + "\n")
            f.write(f"CSV数据分析报告\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"文件路径: {file_path}\n")
            f.write("=" * 80 + "\n\n")
            
            # 2. 基本数据信息
            f.write("1. 基本数据信息\n")
            f.write("-" * 80 + "\n")
            f.write(f"行数: {df.shape[0]}\n")
            f.write(f"列数: {df.shape[1]}\n")
            f.write(f"数据大小: {df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB\n\n")
            
            # 3. 数据类型分布
            f.write("2. 数据类型分布\n")
            f.write("-" * 80 + "\n")
            type_counts = df.dtypes.value_counts()
            for dtype, count in type_counts.items():
                f.write(f"{dtype}: {count}列\n")
            f.write("\n")
            
            # 4. 缺失值分析
            f.write("3. 缺失值分析\n")
            f.write("-" * 80 + "\n")
            missing_values = df.isnull().sum()
            missing_percent = (missing_values / len(df)) * 100
            
            for col, missing in missing_values.items():
                if missing > 0:
                    f.write(f"{col}: {missing}个缺失值 ({missing_percent[col]:.2f}%)\n")
            
            if missing_values.sum() == 0:
                f.write("数据集中没有缺失值\n")
            f.write("\n")
            
            # 5. 分类列分析
            f.write("4. 分类列分析\n")
            f.write("-" * 80 + "\n")
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            for col in categorical_cols:
                f.write(f"列名: {col}\n")
                value_counts = df[col].value_counts()
                unique_count = len(value_counts)
                f.write(f"  唯一值数量: {unique_count}\n")
                
                if unique_count <= 10:  # 如果唯一值较少，显示所有值的分布
                    f.write("  值分布:\n")
                    for val, count in value_counts.items():
                        f.write(f"    {val}: {count}次 ({count/len(df)*100:.2f}%)\n")
                else:  # 否则只显示前5个最常见的值
                    f.write("  前5个最常见值:\n")
                    for val, count in value_counts.head(5).items():
                        f.write(f"    {val}: {count}次 ({count/len(df)*100:.2f}%)\n")
                f.write("\n")
            
            # 6. 数值列分析
            f.write("5. 数值列分析\n")
            f.write("-" * 80 + "\n")
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            for col in numeric_cols:
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:  # 确保列中有非空值
                    f.write(f"列名: {col}\n")
                    f.write(f"  非空值数量: {len(non_null_values)}\n")
                    f.write(f"  最小值: {non_null_values.min():.4f}\n")
                    f.write(f"  最大值: {non_null_values.max():.4f}\n")
                    f.write(f"  平均值: {non_null_values.mean():.4f}\n")
                    f.write(f"  中位数: {non_null_values.median():.4f}\n")
                    f.write(f"  标准差: {non_null_values.std():.4f}\n")
                    
                    # 计算分位数
                    percentiles = [0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
                    percentile_values = np.percentile(non_null_values, [p * 100 for p in percentiles])
                    f.write("  分位数:\n")
                    for p, val in zip(percentiles, percentile_values):
                        f.write(f"    {p*100}%: {val:.4f}\n")
                    f.write("\n")
            
            # 7. 特殊事件分析 (如果存在event_type列)
            if 'event_type' in df.columns:
                f.write("6. 事件类型分析\n")
                f.write("-" * 80 + "\n")
                event_counts = df['event_type'].value_counts()
                for event, count in event_counts.items():
                    f.write(f"{event}: {count}次 ({count/len(df)*100:.2f}%)\n")
                f.write("\n")
            
            # 8. 服务器性能指标分析
            f.write("7. 服务器性能关键指标\n")
            f.write("-" * 80 + "\n")
            
            # 计算高负载情况
            if 'cpu_usage_percent' in df.columns:
                high_cpu = df[df['cpu_usage_percent'] > 80].shape[0]
                f.write(f"CPU使用率 > 80%: {high_cpu}次 ({high_cpu/df['cpu_usage_percent'].count()*100:.2f}%)\n")
            
            if 'memory_usage_percent' in df.columns:
                high_mem = df[df['memory_usage_percent'] > 80].shape[0]
                f.write(f"内存使用率 > 80%: {high_mem}次 ({high_mem/df['memory_usage_percent'].count()*100:.2f}%)\n")
            
            if 'disk_usage_percent' in df.columns:
                high_disk = df[df['disk_usage_percent'] > 80].shape[0]
                f.write(f"磁盘使用率 > 80%: {high_disk}次 ({high_disk/df['disk_usage_percent'].count()*100:.2f}%)\n")
            
            # 9. 数据库性能指标分析 (如果存在相关列)
            if 'slow_queries_count' in df.columns:
                f.write("\n8. 数据库性能指标\n")
                f.write("-" * 80 + "\n")
                total_slow_queries = df['slow_queries_count'].sum()
                f.write(f"慢查询总数: {total_slow_queries}\n")
                
                if 'deadlock_count' in df.columns:
                    total_deadlocks = df['deadlock_count'].sum()
                    f.write(f"死锁总数: {total_deadlocks}\n")
                
                if 'cache_hit_rate_percent' in df.columns:
                    avg_cache_hit = df['cache_hit_rate_percent'].mean()
                    f.write(f"平均缓存命中率: {avg_cache_hit:.2f}%\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("分析报告生成完毕\n")
            
        print(f"分析完成，结果已保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    csv_file = "temp_csv/excel_data_20250317134204.csv"
    output_file = "pngs/analysis_results.txt"
    
    analyze_csv_data(csv_file, output_file)