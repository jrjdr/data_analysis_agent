import pandas as pd
import os
import numpy as np
from datetime import datetime

def analyze_csv_data(file_path, output_path):
    """
    Analyze CSV data and save results to a text file
    
    Args:
        file_path (str): Path to the CSV file
        output_path (str): Path to save the analysis results
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"Reading CSV file: {file_path}")
        df = pd.read_csv(file_path)
        
        # Open output file
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write("=" * 80 + "\n")
            f.write(f"数据分析报告 - 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"文件: {file_path}\n")
            f.write("=" * 80 + "\n\n")
            
            # Basic dataset information
            f.write("1. 基本数据信息\n")
            f.write("-" * 80 + "\n")
            f.write(f"行数: {df.shape[0]}\n")
            f.write(f"列数: {df.shape[1]}\n")
            f.write(f"内存使用: {df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB\n\n")
            
            # Column information
            f.write("2. 列信息\n")
            f.write("-" * 80 + "\n")
            for col in df.columns:
                f.write(f"列名: {col}\n")
                f.write(f"  数据类型: {df[col].dtype}\n")
                f.write(f"  缺失值数量: {df[col].isna().sum()}\n")
                f.write(f"  唯一值数量: {df[col].nunique()}\n\n")
            
            # Categorical columns analysis
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            f.write("3. 分类列分析\n")
            f.write("-" * 80 + "\n")
            for col in categorical_cols:
                f.write(f"列名: {col}\n")
                value_counts = df[col].value_counts().head(10)
                f.write(f"  前10个最常见值:\n")
                for val, count in value_counts.items():
                    f.write(f"    {val}: {count} ({count/len(df)*100:.2f}%)\n")
                f.write("\n")
            
            # Numerical columns analysis
            numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
            f.write("4. 数值列分析\n")
            f.write("-" * 80 + "\n")
            for col in numerical_cols:
                f.write(f"列名: {col}\n")
                f.write(f"  最小值: {df[col].min():.4f}\n")
                f.write(f"  最大值: {df[col].max():.4f}\n")
                f.write(f"  平均值: {df[col].mean():.4f}\n")
                f.write(f"  中位数: {df[col].median():.4f}\n")
                f.write(f"  标准差: {df[col].std():.4f}\n")
                
                # Calculate quartiles
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                f.write(f"  第一四分位数 (Q1): {q1:.4f}\n")
                f.write(f"  第三四分位数 (Q3): {q3:.4f}\n")
                f.write(f"  四分位距 (IQR): {iqr:.4f}\n\n")
            
            # Time-based analysis for timestamp column
            if 'timestamp' in df.columns:
                f.write("5. 时间序列分析\n")
                f.write("-" * 80 + "\n")
                
                # Convert timestamp to datetime if it's not already
                if df['timestamp'].dtype != 'datetime64[ns]':
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Get data range
                min_date = df['timestamp'].min()
                max_date = df['timestamp'].max()
                date_range = max_date - min_date
                
                f.write(f"时间范围: {min_date} 至 {max_date}\n")
                f.write(f"时间跨度: {date_range}\n\n")
            
            # Correlation analysis
            f.write("6. 相关性分析\n")
            f.write("-" * 80 + "\n")
            correlation_matrix = df[numerical_cols].corr()
            
            # Find top 10 highest correlations (excluding self-correlations)
            correlations = []
            for i, col1 in enumerate(numerical_cols):
                for j, col2 in enumerate(numerical_cols):
                    if i < j:  # Avoid duplicates and self-correlations
                        correlations.append((col1, col2, correlation_matrix.loc[col1, col2]))
            
            # Sort by absolute correlation value
            correlations.sort(key=lambda x: abs(x[2]), reverse=True)
            
            f.write("前10个最强相关性:\n")
            for i, (col1, col2, corr) in enumerate(correlations[:10], 1):
                f.write(f"  {i}. {col1} 与 {col2}: {corr:.4f}\n")
            f.write("\n")
            
            # Base station analysis
            if 'base_station_id' in df.columns and 'base_station_name' in df.columns:
                f.write("7. 基站分析\n")
                f.write("-" * 80 + "\n")
                stations = df[['base_station_id', 'base_station_name']].drop_duplicates()
                f.write(f"基站数量: {len(stations)}\n")
                f.write("基站列表:\n")
                for _, row in stations.iterrows():
                    f.write(f"  - {row['base_station_id']}: {row['base_station_name']}\n")
                f.write("\n")
                
                # Aggregate metrics by base station
                f.write("每个基站的关键指标:\n")
                for _, station in stations.iterrows():
                    station_id = station['base_station_id']
                    station_df = df[df['base_station_id'] == station_id]
                    f.write(f"  基站: {station_id} ({station['base_station_name']})\n")
                    f.write(f"    记录数: {len(station_df)}\n")
                    f.write(f"    平均成功率: {station_df['success_rate'].mean():.4f}\n")
                    f.write(f"    平均失败率: {station_df['failure_rate'].mean():.4f}\n")
                    f.write(f"    平均信号强度 (dBm): {station_df['signal_strength_dbm'].mean():.4f}\n")
                    f.write(f"    平均下行吞吐量 (Mbps): {station_df['downlink_throughput_mbps'].mean():.4f}\n")
                    f.write(f"    平均上行吞吐量 (Mbps): {station_df['uplink_throughput_mbps'].mean():.4f}\n")
                    f.write(f"    平均延迟 (ms): {station_df['latency_ms'].mean():.4f}\n")
                    f.write(f"    平均丢包率 (%): {station_df['packet_loss_percent'].mean():.4f}\n")
                    f.write(f"    平均CPU使用率 (%): {station_df['cpu_usage_percent'].mean():.4f}\n")
                    f.write(f"    平均内存使用率 (%): {station_df['memory_usage_percent'].mean():.4f}\n")
                    f.write(f"    平均温度 (°C): {station_df['temperature_celsius'].mean():.4f}\n\n")
            
            # Signal type analysis
            if 'signal_type' in df.columns:
                f.write("8. 信号类型分析\n")
                f.write("-" * 80 + "\n")
                signal_types = df['signal_type'].unique()
                
                f.write(f"信号类型数量: {len(signal_types)}\n")
                f.write("每种信号类型的关键指标:\n")
                
                for signal_type in signal_types:
                    signal_df = df[df['signal_type'] == signal_type]
                    f.write(f"  信号类型: {signal_type}\n")
                    f.write(f"    记录数: {len(signal_df)}\n")
                    f.write(f"    平均成功率: {signal_df['success_rate'].mean():.4f}\n")
                    f.write(f"    平均失败率: {signal_df['failure_rate'].mean():.4f}\n")
                    f.write(f"    平均信号强度 (dBm): {signal_df['signal_strength_dbm'].mean():.4f}\n")
                    f.write(f"    平均信号质量 (dB): {signal_df['signal_quality_db'].mean():.4f}\n\n")
                
            # Summary and conclusions
            f.write("9. 总结与结论\n")
            f.write("-" * 80 + "\n")
            f.write("1. 数据集概述:\n")
            f.write(f"   - 共分析了 {df.shape[0]} 条记录，覆盖 {len(stations) if 'base_station_id' in df.columns else 'N/A'} 个基站\n")
            f.write(f"   - 数据包含 {len(categorical_cols)} 个分类列和 {len(numerical_cols)} 个数值列\n\n")
            
            f.write("2. 主要发现:\n")
            f.write(f"   - 整体成功率: 平均 {df['success_rate'].mean():.4f}，中位数 {df['success_rate'].median():.4f}\n")
            f.write(f"   - 信号强度: 平均 {df['signal_strength_dbm'].mean():.4f} dBm\n")
            f.write(f"   - 网络延迟: 平均 {df['latency_ms'].mean():.4f} ms\n")
            f.write(f"   - 丢包率: 平均 {df['packet_loss_percent'].mean():.4f}%\n\n")
            
            f.write("3. 性能指标:\n")
            f.write(f"   - 下行吞吐量: 平均 {df['downlink_throughput_mbps'].mean():.4f} Mbps\n")
            f.write(f"   - 上行吞吐量: 平均 {df['uplink_throughput_mbps'].mean():.4f} Mbps\n")
            f.write(f"   - 资源块使用率: 平均 {df['resource_block_usage_percent'].mean():.4f}%\n\n")
            
            f.write("4. 基站运行状况:\n")
            f.write(f"   - CPU使用率: 平均 {df['cpu_usage_percent'].mean():.4f}%\n")
            f.write(f"   - 内存使用率: 平均 {df['memory_usage_percent'].mean():.4f}%\n")
            f.write(f"   - 设备温度: 平均 {df['temperature_celsius'].mean():.4f}°C\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("分析完成\n")
            
        print(f"Analysis complete. Results saved to {output_path}")
        return True
    
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return False

# Main execution
if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317152243.csv"
    output_path = "pngs/analysis_results.txt"
    
    success = analyze_csv_data(file_path, output_path)
    if success:
        print("Analysis completed successfully.")
    else:
        print("Analysis failed.")