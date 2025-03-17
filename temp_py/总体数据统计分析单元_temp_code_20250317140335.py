import pandas as pd
import numpy as np
import os
from datetime import datetime

def analyze_csv_data(file_path, output_path):
    try:
        # 1. 读取CSV文件
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 创建结果字符串
        result = []
        result.append("=" * 80)
        result.append(f"CSV数据分析报告 - 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result.append(f"文件路径: {file_path}")
        result.append("=" * 80 + "\n")
        
        # 2. 基本数据信息
        result.append("1. 基本数据信息")
        result.append("-" * 40)
        result.append(f"行数: {df.shape[0]}")
        result.append(f"列数: {df.shape[1]}")
        result.append(f"列名: {', '.join(df.columns)}")
        result.append(f"内存使用: {df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB")
        
        # 缺失值统计
        missing_values = df.isnull().sum()
        result.append("\n缺失值统计:")
        for col, missing in missing_values.items():
            if missing > 0:
                result.append(f"  {col}: {missing} ({missing/len(df)*100:.2f}%)")
        result.append("\n")
        
        # 3. 数据类型分析
        result.append("2. 数据类型分析")
        result.append("-" * 40)
        
        # 分离数值列和分类列
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        result.append(f"数值型列 ({len(numeric_cols)}): {', '.join(numeric_cols)}")
        result.append(f"分类型列 ({len(categorical_cols)}): {', '.join(categorical_cols)}")
        result.append("\n")
        
        # 4. 数值列分析
        result.append("3. 数值列分析")
        result.append("-" * 40)
        
        for col in numeric_cols:
            # 跳过全是缺失值的列
            if df[col].isnull().all():
                continue
                
            result.append(f"\n列: {col}")
            result.append(f"  数据类型: {df[col].dtype}")
            result.append(f"  非空值数: {df[col].count()}")
            result.append(f"  唯一值数: {df[col].nunique()}")
            result.append(f"  最小值: {df[col].min():.4f}")
            result.append(f"  最大值: {df[col].max():.4f}")
            result.append(f"  平均值: {df[col].mean():.4f}")
            result.append(f"  中位数: {df[col].median():.4f}")
            result.append(f"  标准差: {df[col].std():.4f}")
            
            # 分位数
            q25, q50, q75 = df[col].quantile([0.25, 0.5, 0.75])
            result.append(f"  25%分位数: {q25:.4f}")
            result.append(f"  50%分位数: {q50:.4f}")
            result.append(f"  75%分位数: {q75:.4f}")
            
            # 异常值检测 (IQR方法)
            iqr = q75 - q25
            lower_bound = q25 - 1.5 * iqr
            upper_bound = q75 + 1.5 * iqr
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
            result.append(f"  异常值数量: {len(outliers)} ({len(outliers)/df[col].count()*100:.2f}%)")
        
        # 5. 分类列分析
        result.append("\n\n4. 分类列分析")
        result.append("-" * 40)
        
        for col in categorical_cols:
            result.append(f"\n列: {col}")
            result.append(f"  非空值数: {df[col].count()}")
            result.append(f"  唯一值数: {df[col].nunique()}")
            
            # 频率分析
            value_counts = df[col].value_counts()
            result.append(f"  最常见值: {value_counts.index[0]} (出现 {value_counts.iloc[0]} 次)")
            
            # 显示前5个最常见的值
            result.append("  值分布:")
            for val, count in value_counts.head(5).items():
                result.append(f"    - {val}: {count} ({count/len(df)*100:.2f}%)")
        
        # 6. 特殊分析 - 事件类型分布
        if 'event_type' in df.columns:
            result.append("\n\n5. 事件类型分析")
            result.append("-" * 40)
            event_counts = df['event_type'].value_counts()
            for event, count in event_counts.items():
                result.append(f"  {event}: {count} ({count/len(df)*100:.2f}%)")
        
        # 7. 服务器资源使用情况分析
        result.append("\n\n6. 服务器资源使用情况")
        result.append("-" * 40)
        
        # 按服务器分组分析CPU和内存使用情况
        if 'server_name' in df.columns and 'cpu_usage_percent' in df.columns:
            result.append("\n服务器CPU使用率:")
            server_cpu = df.groupby('server_name')['cpu_usage_percent'].agg(['mean', 'max', 'min']).reset_index()
            for _, row in server_cpu.iterrows():
                if not np.isnan(row['mean']):
                    result.append(f"  {row['server_name']}: 平均 {row['mean']:.2f}%, 最大 {row['max']:.2f}%, 最小 {row['min']:.2f}%")
        
        if 'server_name' in df.columns and 'memory_usage_percent' in df.columns:
            result.append("\n服务器内存使用率:")
            server_mem = df.groupby('server_name')['memory_usage_percent'].agg(['mean', 'max', 'min']).reset_index()
            for _, row in server_mem.iterrows():
                if not np.isnan(row['mean']):
                    result.append(f"  {row['server_name']}: 平均 {row['mean']:.2f}%, 最大 {row['max']:.2f}%, 最小 {row['min']:.2f}%")
        
        # 8. 数据库性能指标分析
        if 'query_rate_per_sec' in df.columns and 'avg_query_time_ms' in df.columns:
            result.append("\n\n7. 数据库性能指标")
            result.append("-" * 40)
            result.append(f"平均查询率: {df['query_rate_per_sec'].mean():.2f} 查询/秒")
            result.append(f"平均查询时间: {df['avg_query_time_ms'].mean():.2f} 毫秒")
            result.append(f"平均缓存命中率: {df['cache_hit_rate_percent'].mean():.2f}%")
            result.append(f"平均事务数: {df['transactions_per_sec'].mean():.2f} 事务/秒")
            result.append(f"读写比例: {df['read_percent'].mean():.2f}% 读, {df['write_percent'].mean():.2f}% 写")
            result.append(f"平均锁等待次数: {df['lock_wait_count'].mean():.2f}")
            result.append(f"死锁总数: {df['deadlock_count'].sum()}")
            result.append(f"慢查询总数: {df['slow_queries_count'].sum()}")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 将结果写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result))
        
        print(f"分析完成，结果已保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    csv_file = "temp_csv/excel_data_20250317140237.csv"
    output_file = "pngs/analysis_results.txt"
    analyze_csv_data(csv_file, output_file)