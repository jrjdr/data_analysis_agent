import pandas as pd
import numpy as np
import os

def analyze_correlations(file_path, output_path):
    try:
        # 1. 读取CSV文件
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 2. 只选择数值列进行相关性分析
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # 3. 计算相关性矩阵
        print("计算相关性矩阵...")
        corr_matrix = df[numeric_cols].corr()
        
        # 4. 识别高度相关和低度相关的变量对
        high_corr_threshold = 0.8
        low_corr_threshold = 0.2
        
        high_correlations = []
        low_correlations = []
        
        # 遍历相关性矩阵的上三角部分(不包括对角线)
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                col1, col2 = numeric_cols[i], numeric_cols[j]
                corr_value = corr_matrix.loc[col1, col2]
                
                # 忽略NaN值
                if pd.isna(corr_value):
                    continue
                
                # 记录高相关性对
                if abs(corr_value) >= high_corr_threshold:
                    high_correlations.append((col1, col2, corr_value))
                
                # 记录低相关性对
                elif abs(corr_value) <= low_corr_threshold:
                    low_correlations.append((col1, col2, corr_value))
        
        # 按相关性绝对值排序
        high_correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        low_correlations.sort(key=lambda x: abs(x[2]))
        
        # 5. 保存分析结果为纯文本格式
        print(f"保存分析结果到: {output_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 基本信息
            f.write("=== 服务器性能数据相关性分析 ===\n\n")
            f.write(f"数据文件: {file_path}\n")
            f.write(f"数据行数: {len(df)}\n")
            f.write(f"数值列数: {len(numeric_cols)}\n\n")
            
            # 高相关性变量对
            f.write("=== 高度相关变量对 (|r| >= 0.8) ===\n\n")
            if high_correlations:
                for col1, col2, corr in high_correlations:
                    f.write(f"{col1:<30} 与 {col2:<30} | r = {corr:.4f}\n")
            else:
                f.write("未发现高度相关的变量对\n")
            
            f.write("\n")
            
            # 低相关性变量对 (只展示前20个)
            f.write("=== 低度相关变量对 (|r| <= 0.2) ===\n\n")
            if low_correlations:
                for col1, col2, corr in low_correlations[:20]:  # 只显示前20个
                    f.write(f"{col1:<30} 与 {col2:<30} | r = {corr:.4f}\n")
                
                if len(low_correlations) > 20:
                    f.write(f"\n... 还有 {len(low_correlations) - 20} 个低相关性变量对 ...\n")
            else:
                f.write("未发现低度相关的变量对\n")
            
            f.write("\n")
            
            # 相关性矩阵 (格式化为易读的表格)
            f.write("=== 相关性矩阵 ===\n\n")
            
            # 格式化相关性矩阵为文本表格
            corr_text = corr_matrix.round(3).to_string()
            f.write(corr_text)
            
            f.write("\n\n=== 分析总结 ===\n\n")
            
            # 总结高相关性组
            if high_correlations:
                f.write(f"发现 {len(high_correlations)} 对高度相关变量 (|r| >= 0.8)\n")
                # 识别最强相关性
                strongest = high_correlations[0]
                f.write(f"最强相关性: {strongest[0]} 与 {strongest[1]}, r = {strongest[2]:.4f}\n\n")
            else:
                f.write("未发现高度相关的变量对\n\n")
            
            # 总结分析结果
            f.write("相关性分析可用于:\n")
            f.write("1. 识别冗余指标: 高度相关的指标可能提供相似信息\n")
            f.write("2. 发现性能关联: 了解哪些指标之间存在强关联\n")
            f.write("3. 简化监控: 可以减少需要密切监控的指标数量\n")
        
        print("分析完成!")
        return True
    
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    input_file = "temp_csv/excel_data_20250317141159.csv"
    output_file = "pngs/correlation_results.txt"
    
    analyze_correlations(input_file, output_file)