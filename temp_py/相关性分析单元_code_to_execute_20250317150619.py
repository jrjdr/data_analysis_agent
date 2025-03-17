import pandas as pd
import numpy as np
import os
from datetime import datetime

def analyze_correlations(file_path, output_path, high_corr_threshold=0.8, low_corr_threshold=0.2):
    """
    Analyze correlations in a CSV dataset and save results to a text file.
    
    Args:
        file_path: Path to the CSV file
        output_path: Path to save the results
        high_corr_threshold: Threshold for high correlation (default: 0.8)
        low_corr_threshold: Threshold for low correlation (default: 0.2)
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Read the CSV file
        print(f"Reading data from {file_path}...")
        df = pd.read_csv(file_path)
        
        # Get numeric columns only
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # Calculate correlation matrix
        print("Calculating correlation matrix...")
        corr_matrix = df[numeric_cols].corr()
        
        # Find highly correlated pairs (excluding self-correlations)
        high_corr_pairs = []
        low_corr_pairs = []
        
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                col1, col2 = numeric_cols[i], numeric_cols[j]
                correlation = corr_matrix.loc[col1, col2]
                
                # Skip if correlation is NaN
                if pd.isna(correlation):
                    continue
                    
                corr_abs = abs(correlation)
                if corr_abs >= high_corr_threshold:
                    high_corr_pairs.append((col1, col2, correlation))
                elif corr_abs <= low_corr_threshold:
                    low_corr_pairs.append((col1, col2, correlation))
        
        # Sort the pairs by absolute correlation value (descending for high, ascending for low)
        high_corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        low_corr_pairs.sort(key=lambda x: abs(x[2]))
        
        # Write results to text file
        print(f"Writing results to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write("=" * 80 + "\n")
            f.write(f"服务器监控数据相关性分析报告\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"数据文件: {file_path}\n")
            f.write(f"数据行数: {len(df)}\n")
            f.write(f"数值型列数: {len(numeric_cols)}\n")
            f.write("=" * 80 + "\n\n")
            
            # Write high correlation pairs
            f.write("-" * 80 + "\n")
            f.write(f"高度相关变量对 (|r| >= {high_corr_threshold}):\n")
            f.write("-" * 80 + "\n")
            
            if high_corr_pairs:
                for col1, col2, corr in high_corr_pairs:
                    f.write(f"{col1.ljust(30)} | {col2.ljust(30)} | {corr:.4f}\n")
            else:
                f.write("未发现高度相关的变量对\n")
            f.write("\n")
            
            # Write low correlation pairs (top 20 only to keep the output manageable)
            f.write("-" * 80 + "\n")
            f.write(f"低度相关变量对 (|r| <= {low_corr_threshold}):\n")
            f.write("-" * 80 + "\n")
            
            if low_corr_pairs:
                # Limit to top 20 to keep the output manageable
                for col1, col2, corr in low_corr_pairs[:20]:
                    f.write(f"{col1.ljust(30)} | {col2.ljust(30)} | {corr:.4f}\n")
                if len(low_corr_pairs) > 20:
                    f.write(f"... 及其他 {len(low_corr_pairs) - 20} 对低相关变量\n")
            else:
                f.write("未发现低度相关的变量对\n")
            f.write("\n")
            
            # Write correlation matrix with clean formatting
            f.write("-" * 80 + "\n")
            f.write("相关性矩阵:\n")
            f.write("-" * 80 + "\n")
            
            # Format the correlation matrix for better readability
            # First write the header row
            header_row = "变量名".ljust(30) + " | "
            for col in numeric_cols:
                header_row += f"{col[:10].ljust(10)} | "
            f.write(header_row + "\n")
            f.write("-" * len(header_row) + "\n")
            
            # Then write each row of the correlation matrix
            for row_col in numeric_cols:
                row_str = row_col.ljust(30) + " | "
                for col in numeric_cols:
                    val = corr_matrix.loc[row_col, col]
                    if pd.isna(val):
                        row_str += "N/A".ljust(10) + " | "
                    else:
                        row_str += f"{val:.2f}".ljust(10) + " | "
                f.write(row_str + "\n")
            
            # Write key observations and metrics
            f.write("\n" + "-" * 80 + "\n")
            f.write("关键观察结果:\n")
            f.write("-" * 80 + "\n")
            
            # Count metrics with high correlation to performance indicators
            performance_indicators = ['cpu_usage_percent', 'memory_usage_percent', 'disk_io_percent', 'network_traffic_percent']
            f.write("性能指标相关性分析:\n\n")
            
            for indicator in performance_indicators:
                if indicator in numeric_cols:
                    f.write(f"{indicator} 的主要相关指标:\n")
                    correlations = corr_matrix[indicator].drop(indicator).sort_values(ascending=False)
                    top_pos = correlations.head(3)
                    top_neg = correlations.tail(3)
                    
                    f.write("  正相关 (Top 3):\n")
                    for col, val in top_pos.items():
                        if not pd.isna(val):
                            f.write(f"    {col.ljust(30)}: {val:.4f}\n")
                    
                    f.write("  负相关 (Top 3):\n")
                    for col, val in top_neg.items():
                        if not pd.isna(val):
                            f.write(f"    {col.ljust(30)}: {val:.4f}\n")
                    f.write("\n")
            
            # Success message
            f.write("\n" + "=" * 80 + "\n")
            f.write("分析完成\n")
            f.write("=" * 80 + "\n")
        
        print("Analysis completed successfully!")
        return True
    
    except Exception as e:
        print(f"Error during correlation analysis: {str(e)}")
        return False

if __name__ == "__main__":
    # 定义文件路径
    csv_file = "temp_csv/excel_data_20250317145554.csv"
    output_file = "pngs/correlation_results.txt"
    
    # 执行分析
    success = analyze_correlations(
        file_path=csv_file,
        output_path=output_file,
        high_corr_threshold=0.8,
        low_corr_threshold=0.2
    )
    
    if success:
        print(f"结果已保存到: {output_file}")
    else:
        print("分析过程中发生错误，请检查日志。")