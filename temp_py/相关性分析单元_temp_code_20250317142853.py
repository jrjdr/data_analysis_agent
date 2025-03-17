import pandas as pd
import numpy as np
import os

def load_data(file_path):
    """读取CSV文件并处理基本问题"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功读取数据: {df.shape[0]}行, {df.shape[1]}列")
        return df
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

def calculate_correlation(df):
    """计算数值列间的相关性"""
    try:
        # 选择数值型列
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        
        # 计算相关性矩阵
        correlation_matrix = df[numeric_cols].corr(method='pearson')
        return correlation_matrix, numeric_cols
    except Exception as e:
        print(f"计算相关性失败: {e}")
        return None, None

def identify_correlations(correlation_matrix, threshold_high=0.7, threshold_low=0.2):
    """识别高度相关和低度相关的变量对"""
    high_correlations = []
    low_correlations = []
    
    # 获取相关系数的上三角矩阵（排除对角线）
    corr_values = correlation_matrix.where(
        np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
    ).stack().reset_index()
    
    corr_values.columns = ['Variable 1', 'Variable 2', 'Correlation']
    
    # 按相关性绝对值降序排序
    corr_values['Abs_Correlation'] = corr_values['Correlation'].abs()
    corr_values = corr_values.sort_values('Abs_Correlation', ascending=False)
    
    # 获取高相关性对
    high_correlations = corr_values[corr_values['Abs_Correlation'] >= threshold_high]
    
    # 获取低相关性对
    low_correlations = corr_values[corr_values['Abs_Correlation'] <= threshold_low]
    
    return high_correlations, low_correlations

def save_results(correlation_matrix, high_correlations, low_correlations, numeric_cols, output_path):
    """将分析结果保存为纯文本格式"""
    try:
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 1. 添加标题
            f.write("=== 服务器性能监控数据相关性分析 ===\n\n")
            
            # 2. 数据概述
            f.write("== 分析概述 ==\n")
            f.write(f"分析了{len(numeric_cols)}个数值型变量之间的相关性。\n\n")
            
            # 3. 高度相关变量对
            f.write("== 高度相关变量 (|r| >= 0.7) ==\n")
            if len(high_correlations) > 0:
                for _, row in high_correlations.iterrows():
                    f.write(f"{row['Variable 1']} 与 {row['Variable 2']}: {row['Correlation']:.4f}\n")
            else:
                f.write("未发现高度相关的变量对。\n")
            f.write("\n")
            
            # 4. 低度相关变量对 (仅显示前20个)
            f.write("== 低度相关变量 (|r| <= 0.2) ==\n")
            if len(low_correlations) > 0:
                for _, row in low_correlations.head(20).iterrows():
                    f.write(f"{row['Variable 1']} 与 {row['Variable 2']}: {row['Correlation']:.4f}\n")
                if len(low_correlations) > 20:
                    f.write(f"... 还有{len(low_correlations)-20}对低相关变量 ...\n")
            else:
                f.write("未发现低度相关的变量对。\n")
            f.write("\n")
            
            # 5. 相关性摘要
            f.write("== 重要性能指标相关性 ==\n")
            key_metrics = ['cpu_usage_percent', 'memory_usage_percent', 'disk_io_percent', 
                           'network_traffic_percent', 'query_rate_per_sec', 'avg_query_time_ms']
            available_metrics = [m for m in key_metrics if m in correlation_matrix.index]
            
            if available_metrics:
                for metric in available_metrics:
                    f.write(f"\n{metric} 与其他指标的相关性:\n")
                    correlations = correlation_matrix[metric].sort_values(ascending=False)
                    # 排除自身
                    correlations = correlations[correlations.index != metric]
                    for var, corr in correlations.head(5).items():
                        f.write(f"  - {var}: {corr:.4f}\n")
            
            # 6. 完整相关性矩阵
            f.write("\n\n== 完整相关性矩阵 ==\n")
            # 格式化矩阵以便在文本文件中更好地显示
            matrix_str = correlation_matrix.round(3).to_string()
            f.write(matrix_str)
            
        print(f"结果已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存结果失败: {e}")
        return False

def main():
    # 文件路径
    file_path = "temp_csv/excel_data_20250317142408.csv"
    output_path = "pngs/correlation_results.txt"
    
    # 1. 读取CSV文件
    df = load_data(file_path)
    if df is None:
        return
    
    # 2. 计算相关性
    correlation_matrix, numeric_cols = calculate_correlation(df)
    if correlation_matrix is None:
        return
    
    # 3. 识别高度相关和低度相关的变量对
    high_correlations, low_correlations = identify_correlations(correlation_matrix)
    
    # 4. 保存结果
    save_results(correlation_matrix, high_correlations, low_correlations, numeric_cols, output_path)

if __name__ == "__main__":
    main()