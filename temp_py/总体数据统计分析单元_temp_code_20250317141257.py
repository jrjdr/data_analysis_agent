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
            # 写入标题和基本信息
            f.write("=" * 80 + "\n")
            f.write(f"CSV数据分析报告\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"文件路径: {file_path}\n")
            f.write("=" * 80 + "\n\n")
            
            # 2. 基本数据集信息
            f.write("1. 基本数据集信息\n")
            f.write("-" * 40 + "\n")
            f.write(f"行数: {df.shape[0]}\n")
            f.write(f"列数: {df.shape[1]}\n")
            f.write(f"列名: {', '.join(df.columns)}\n\n")
            
            # 3. 数据类型和缺失值分析
            f.write("2. 数据类型和缺失值分析\n")
            f.write("-" * 40 + "\n")
            dtypes_info = pd.DataFrame({
                '数据类型': df.dtypes,
                '非空值数': df.count(),
                '缺失值数': df.isna().sum(),
                '缺失值百分比': (df.isna().sum() / len(df) * 100).round(2)
            })
            f.write(dtypes_info.to_string() + "\n\n")
            
            # 4. 分类列分析
            f.write("3. 分类列分析\n")
            f.write("-" * 40 + "\n")
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                f.write(f"列: {col}\n")
                value_counts = df[col].value_counts().head(10)
                f.write(f"唯一值数量: {df[col].nunique()}\n")
                f.write("前10个最常见值:\n")
                for val, count in value_counts.items():
                    f.write(f"  - {val}: {count} ({count/len(df)*100:.2f}%)\n")
                f.write("\n")
            
            # 5. 数值列分析
            f.write("4. 数值列分析\n")
            f.write("-" * 40 + "\n")
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            # 计算描述性统计
            desc_stats = df[numeric_cols].describe().T
            # 添加其他统计量
            desc_stats['中位数'] = df[numeric_cols].median()
            desc_stats['变异系数'] = df[numeric_cols].std() / df[numeric_cols].mean() * 100
            desc_stats['缺失值'] = df[numeric_cols].isna().sum()
            desc_stats['缺失比例'] = df[numeric_cols].isna().sum() / len(df) * 100
            
            # 格式化输出
            for col in numeric_cols:
                f.write(f"列: {col}\n")
                if df[col].isna().sum() == len(df):
                    f.write("  全部为缺失值\n\n")
                    continue
                    
                stats = desc_stats.loc[col]
                f.write(f"  最小值: {stats['min']:.2f}\n")
                f.write(f"  第一四分位数: {stats['25%']:.2f}\n")
                f.write(f"  中位数: {stats['50%']:.2f}\n")
                f.write(f"  平均值: {stats['mean']:.2f}\n")
                f.write(f"  第三四分位数: {stats['75%']:.2f}\n")
                f.write(f"  最大值: {stats['max']:.2f}\n")
                f.write(f"  标准差: {stats['std']:.2f}\n")
                f.write(f"  变异系数: {stats['变异系数']:.2f}%\n")
                f.write(f"  缺失值数量: {int(stats['缺失值'])}\n")
                f.write(f"  缺失值比例: {stats['缺失比例']:.2f}%\n\n")
            
            # 6. 资源类型分析
            if 'resource_type' in df.columns:
                f.write("5. 资源类型分析\n")
                f.write("-" * 40 + "\n")
                resource_types = df['resource_type'].unique()
                f.write(f"资源类型: {', '.join(resource_types)}\n\n")
                
                for res_type in resource_types:
                    f.write(f"资源类型 '{res_type}' 的统计信息:\n")
                    type_df = df[df['resource_type'] == res_type]
                    f.write(f"  记录数: {len(type_df)} ({len(type_df)/len(df)*100:.2f}%)\n\n")
            
            # 7. 事件类型分析
            if 'event_type' in df.columns:
                f.write("6. 事件类型分析\n")
                f.write("-" * 40 + "\n")
                event_counts = df['event_type'].value_counts()
                f.write("事件类型分布:\n")
                for event, count in event_counts.items():
                    f.write(f"  - {event}: {count} ({count/len(df)*100:.2f}%)\n")
                f.write("\n")
            
            # 8. 服务器分析
            if 'server_id' in df.columns and 'server_name' in df.columns:
                f.write("7. 服务器分析\n")
                f.write("-" * 40 + "\n")
                servers = df[['server_id', 'server_name']].drop_duplicates()
                f.write(f"服务器数量: {len(servers)}\n")
                f.write("服务器列表:\n")
                for _, row in servers.iterrows():
                    f.write(f"  - {row['server_id']}: {row['server_name']}\n")
                f.write("\n")
            
            # 9. 总结
            f.write("8. 数据总结\n")
            f.write("-" * 40 + "\n")
            f.write("主要发现:\n")
            
            # CPU使用率
            if 'cpu_usage_percent' in numeric_cols and not df['cpu_usage_percent'].isna().all():
                avg_cpu = df['cpu_usage_percent'].mean()
                max_cpu = df['cpu_usage_percent'].max()
                f.write(f"  - CPU平均使用率: {avg_cpu:.2f}%, 最高: {max_cpu:.2f}%\n")
            
            # 内存使用率
            if 'memory_usage_percent' in numeric_cols and not df['memory_usage_percent'].isna().all():
                avg_mem = df['memory_usage_percent'].mean()
                max_mem = df['memory_usage_percent'].max()
                f.write(f"  - 内存平均使用率: {avg_mem:.2f}%, 最高: {max_mem:.2f}%\n")
            
            # 磁盘使用率
            if 'disk_usage_percent' in numeric_cols and not df['disk_usage_percent'].isna().all():
                avg_disk = df['disk_usage_percent'].mean()
                max_disk = df['disk_usage_percent'].max()
                f.write(f"  - 磁盘平均使用率: {avg_disk:.2f}%, 最高: {max_disk:.2f}%\n")
            
            # 事件分析
            if 'event_type' in df.columns:
                normal_events = df[df['event_type'] == 'normal'].shape[0]
                abnormal_events = df[df['event_type'] != 'normal'].shape[0]
                f.write(f"  - 正常事件: {normal_events} ({normal_events/len(df)*100:.2f}%)\n")
                f.write(f"  - 异常事件: {abnormal_events} ({abnormal_events/len(df)*100:.2f}%)\n")
            
            # 数据库性能
            if 'avg_query_time_ms' in numeric_cols and not df['avg_query_time_ms'].isna().all():
                avg_query_time = df['avg_query_time_ms'].mean()
                f.write(f"  - 平均查询时间: {avg_query_time:.2f}ms\n")
            
            if 'cache_hit_rate_percent' in numeric_cols and not df['cache_hit_rate_percent'].isna().all():
                avg_cache_hit = df['cache_hit_rate_percent'].mean()
                f.write(f"  - 平均缓存命中率: {avg_cache_hit:.2f}%\n")
            
            if 'slow_queries_count' in numeric_cols and not df['slow_queries_count'].isna().all():
                total_slow_queries = df['slow_queries_count'].sum()
                f.write(f"  - 慢查询总数: {total_slow_queries:.0f}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("分析完成\n")
            
        print(f"分析完成，结果已保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    csv_file = "temp_csv/excel_data_20250317141159.csv"
    output_file = "pngs/analysis_results.txt"
    analyze_csv_data(csv_file, output_file)