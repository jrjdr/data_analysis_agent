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
            f.write(f"文件: {file_path}\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # 2. 基本数据信息
            f.write("1. 基本数据信息\n")
            f.write("-" * 80 + "\n")
            f.write(f"行数: {df.shape[0]}\n")
            f.write(f"列数: {df.shape[1]}\n")
            f.write(f"列名: {', '.join(df.columns)}\n\n")
            
            # 数据类型信息
            f.write("数据类型信息:\n")
            for col, dtype in df.dtypes.items():
                f.write(f"  - {col}: {dtype}\n")
            f.write("\n")
            
            # 缺失值信息
            missing_values = df.isnull().sum()
            f.write("缺失值信息:\n")
            for col, missing in missing_values.items():
                if missing > 0:
                    f.write(f"  - {col}: {missing} ({missing/len(df)*100:.2f}%)\n")
            f.write("\n")
            
            # 3. 分析数值列和分类列的分布
            # 区分数值列和分类列
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            # 分析分类列
            f.write("2. 分类列分析\n")
            f.write("-" * 80 + "\n")
            for col in categorical_cols:
                f.write(f"列: {col}\n")
                value_counts = df[col].value_counts()
                unique_count = len(value_counts)
                f.write(f"  - 唯一值数量: {unique_count}\n")
                
                # 如果唯一值较少，显示所有值的分布
                if unique_count <= 10:
                    f.write("  - 值分布:\n")
                    for val, count in value_counts.items():
                        f.write(f"    * {val}: {count} ({count/len(df)*100:.2f}%)\n")
                else:
                    f.write("  - 前5个最常见值:\n")
                    for val, count in value_counts.head(5).items():
                        f.write(f"    * {val}: {count} ({count/len(df)*100:.2f}%)\n")
                f.write("\n")
            
            # 分析数值列
            f.write("3. 数值列分析\n")
            f.write("-" * 80 + "\n")
            for col in numeric_cols:
                # 跳过全部为NaN的列
                if df[col].isna().all():
                    continue
                    
                f.write(f"列: {col}\n")
                stats = df[col].describe()
                
                # 将统计结果转换为普通Python类型，避免NumPy类型序列化问题
                f.write(f"  - 计数: {float(stats['count']):.0f}\n")
                f.write(f"  - 平均值: {float(stats['mean']):.4f}\n")
                f.write(f"  - 标准差: {float(stats['std']):.4f}\n")
                f.write(f"  - 最小值: {float(stats['min']):.4f}\n")
                f.write(f"  - 25%分位数: {float(stats['25%']):.4f}\n")
                f.write(f"  - 中位数: {float(stats['50%']):.4f}\n")
                f.write(f"  - 75%分位数: {float(stats['75%']):.4f}\n")
                f.write(f"  - 最大值: {float(stats['max']):.4f}\n")
                
                # 计算缺失值百分比
                missing_pct = df[col].isna().mean() * 100
                f.write(f"  - 缺失值: {df[col].isna().sum()} ({missing_pct:.2f}%)\n\n")
            
            # 4. 关键发现和总结
            f.write("4. 关键发现和总结\n")
            f.write("-" * 80 + "\n")
            
            # 资源使用情况分析
            if 'cpu_usage_percent' in numeric_cols:
                high_cpu = df[df['cpu_usage_percent'] > 80]['cpu_usage_percent'].count()
                f.write(f"- 高CPU使用率(>80%)出现次数: {high_cpu}\n")
            
            if 'memory_usage_percent' in numeric_cols:
                high_mem = df[df['memory_usage_percent'] > 80]['memory_usage_percent'].count()
                f.write(f"- 高内存使用率(>80%)出现次数: {high_mem}\n")
            
            if 'disk_usage_percent' in numeric_cols:
                high_disk = df[df['disk_usage_percent'] > 80]['disk_usage_percent'].count()
                f.write(f"- 高磁盘使用率(>80%)出现次数: {high_disk}\n")
            
            # 事件类型分析
            if 'event_type' in categorical_cols:
                error_events = df[df['event_type'] != 'normal']['event_type'].count()
                f.write(f"- 非正常事件数量: {error_events}\n")
                if error_events > 0:
                    f.write("  事件类型分布:\n")
                    event_counts = df[df['event_type'] != 'normal']['event_type'].value_counts()
                    for event, count in event_counts.items():
                        f.write(f"  - {event}: {count}\n")
            
            # 数据库性能分析
            if 'slow_queries_count' in numeric_cols:
                total_slow_queries = df['slow_queries_count'].sum()
                f.write(f"- 总慢查询数: {total_slow_queries:.0f}\n")
            
            if 'deadlock_count' in numeric_cols:
                total_deadlocks = df['deadlock_count'].sum()
                f.write(f"- 总死锁数: {total_deadlocks:.0f}\n")
            
            f.write("\n分析完成。\n")
            
        print(f"分析结果已保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    csv_file = "temp_csv/excel_data_20250317135634.csv"
    output_file = "pngs/analysis_results.txt"
    
    analyze_csv_data(csv_file, output_file)