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
                # 跳过全是缺失值的列
                if df[col].isnull().all():
                    continue
                    
                f.write(f"列: {col}\n")
                
                # 计算基本统计量
                stats = df[col].describe()
                
                # 格式化输出统计量
                f.write(f"  - 计数: {stats['count']:.0f}\n")
                f.write(f"  - 平均值: {stats['mean']:.4f}\n")
                f.write(f"  - 标准差: {stats['std']:.4f}\n")
                f.write(f"  - 最小值: {stats['min']:.4f}\n")
                f.write(f"  - 25%分位数: {stats['25%']:.4f}\n")
                f.write(f"  - 中位数: {stats['50%']:.4f}\n")
                f.write(f"  - 75%分位数: {stats['75%']:.4f}\n")
                f.write(f"  - 最大值: {stats['max']:.4f}\n")
                
                # 计算其他统计量
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    f.write(f"  - 偏度: {non_null.skew():.4f}\n")
                    f.write(f"  - 峰度: {non_null.kurtosis():.4f}\n")
                    
                    # 计算异常值数量（使用IQR方法）
                    Q1 = non_null.quantile(0.25)
                    Q3 = non_null.quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = ((non_null < (Q1 - 1.5 * IQR)) | (non_null > (Q3 + 1.5 * IQR))).sum()
                    f.write(f"  - 潜在异常值数量: {outliers} ({outliers/len(non_null)*100:.2f}%)\n")
                f.write("\n")
            
            # 4. 总结发现
            f.write("4. 数据总结与发现\n")
            f.write("-" * 80 + "\n")
            
            # 资源使用率分析
            resource_cols = [col for col in df.columns if 'usage_percent' in col]
            if resource_cols:
                f.write("资源使用情况:\n")
                for col in resource_cols:
                    if not df[col].isnull().all():
                        high_usage = (df[col] > 80).sum()
                        if high_usage > 0:
                            f.write(f"  - {col}: 有 {high_usage} 条记录 ({high_usage/len(df)*100:.2f}%) 使用率超过80%\n")
            
            # 事件类型分析
            if 'event_type' in df.columns:
                f.write("\n事件类型分析:\n")
                event_counts = df['event_type'].value_counts()
                for event, count in event_counts.items():
                    if event != 'normal':
                        f.write(f"  - {event}: {count} 次 ({count/len(df)*100:.2f}%)\n")
            
            # 性能指标分析
            if 'slow_queries_count' in numeric_cols and not df['slow_queries_count'].isnull().all():
                total_slow = df['slow_queries_count'].sum()
                f.write(f"\n慢查询总数: {total_slow:.0f}\n")
            
            if 'deadlock_count' in numeric_cols and not df['deadlock_count'].isnull().all():
                total_deadlocks = df['deadlock_count'].sum()
                f.write(f"死锁总数: {total_deadlocks:.0f}\n")
            
            print(f"分析完成，结果已保存到: {output_path}")
            
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        raise

if __name__ == "__main__":
    csv_file = "temp_csv/excel_data_20250317143557.csv"
    output_file = "pngs/analysis_results.txt"
    
    analyze_csv_data(csv_file, output_file)