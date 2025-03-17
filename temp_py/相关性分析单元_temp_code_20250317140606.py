import pandas as pd
import numpy as np
import os

def analyze_correlations(file_path, output_path):
    try:
        # 1. 读取CSV文件
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 2. 基本数据清理和准备
        # 将timestamp列转换为datetime类型
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 只选择数值型列进行相关性分析
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        numeric_df = df[numeric_columns]
        
        # 3. 计算相关性矩阵
        print("计算相关性矩阵...")
        correlation_matrix = numeric_df.corr(method='pearson')
        
        # 4. 识别高度相关和低度相关的变量对
        # 创建变量对的相关性列表(不包括自相关)
        corr_pairs = []
        for i in range(len(numeric_columns)):
            for j in range(i+1, len(numeric_columns)):
                col1 = numeric_columns[i]
                col2 = numeric_columns[j]
                corr_value = correlation_matrix.loc[col1, col2]
                if not np.isnan(corr_value):  # 排除NaN值
                    corr_pairs.append((col1, col2, corr_value))
        
        # 按相关性绝对值排序
        corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        # 5. 准备输出结果
        print(f"正在保存结果到: {output_path}")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入标题和基本信息
            f.write("=== 数据相关性分析报告 ===\n\n")
            f.write(f"数据源: {file_path}\n")
            f.write(f"记录数: {len(df)}\n")
            f.write(f"数值型变量数: {len(numeric_columns)}\n\n")
            
            # 写入高度相关变量对
            f.write("=== 高度相关变量对 (|r| > 0.8) ===\n\n")
            high_corr = [pair for pair in corr_pairs if abs(pair[2]) > 0.8]
            if high_corr:
                for col1, col2, corr in high_corr:
                    f.write(f"{col1} <-> {col2}: {corr:.4f}\n")
            else:
                f.write("没有发现高度相关的变量对\n")
            
            # 写入中度相关变量对
            f.write("\n=== 中度相关变量对 (0.5 < |r| <= 0.8) ===\n\n")
            medium_corr = [pair for pair in corr_pairs if 0.5 < abs(pair[2]) <= 0.8]
            if medium_corr:
                for col1, col2, corr in medium_corr[:20]:  # 限制输出数量
                    f.write(f"{col1} <-> {col2}: {corr:.4f}\n")
                if len(medium_corr) > 20:
                    f.write(f"... 以及 {len(medium_corr) - 20} 个其他中度相关变量对\n")
            else:
                f.write("没有发现中度相关的变量对\n")
            
            # 写入低度相关变量对
            f.write("\n=== 低度相关变量对 (|r| < 0.2) ===\n\n")
            low_corr = [pair for pair in corr_pairs if abs(pair[2]) < 0.2]
            if low_corr:
                for col1, col2, corr in low_corr[:20]:  # 限制输出数量
                    f.write(f"{col1} <-> {col2}: {corr:.4f}\n")
                if len(low_corr) > 20:
                    f.write(f"... 以及 {len(low_corr) - 20} 个其他低度相关变量对\n")
            else:
                f.write("没有发现低度相关的变量对\n")
            
            # 写入完整相关性矩阵
            f.write("\n=== 完整相关性矩阵 ===\n\n")
            # 格式化相关性矩阵以便于阅读
            corr_text = correlation_matrix.round(4).to_string()
            f.write(corr_text)
            
            # 写入总结
            f.write("\n\n=== 分析总结 ===\n\n")
            f.write(f"总共分析了 {len(corr_pairs)} 个变量对的相关性\n")
            f.write(f"高度相关 (|r| > 0.8): {len(high_corr)} 对\n")
            f.write(f"中度相关 (0.5 < |r| <= 0.8): {len(medium_corr)} 对\n")
            f.write(f"低度相关 (|r| < 0.2): {len(low_corr)} 对\n")
            
        print("分析完成!")
        return True
    
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    input_file = "temp_csv/excel_data_20250317140237.csv"
    output_file = "pngs/correlation_results.txt"
    
    success = analyze_correlations(input_file, output_file)
    
    if success:
        print(f"相关性分析结果已保存到: {output_file}")
    else:
        print("相关性分析失败，请检查错误信息。")