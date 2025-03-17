import pandas as pd
import os
from datetime import datetime

def analyze_csv_distributions(file_path, output_path):
    """
    分析CSV文件中分类列的分布情况，计算各类别的占比，并将结果保存为纯文本
    
    参数:
    file_path (str): CSV文件路径
    output_path (str): 输出结果的文本文件路径
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件未找到: {file_path}")
        
        # 读取CSV文件
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 确认数据加载成功
        print(f"成功加载数据，共 {len(df)} 行，{len(df.columns)} 列")
        
        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 准备写入分析结果
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入标题和时间戳
            f.write("=" * 80 + "\n")
            f.write(f"CSV文件分类数据分布分析\n")
            f.write(f"文件路径: {file_path}\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # 识别分类列（对象类型的列，除了Timestamp）
            categorical_columns = [col for col in df.columns if df[col].dtype == 'object' and col != 'Timestamp']
            f.write(f"分类列识别结果: {', '.join(categorical_columns)}\n\n")
            
            # 分析每个分类列的分布
            for column in categorical_columns:
                f.write("-" * 80 + "\n")
                f.write(f"{column} 分布情况\n")
                f.write("-" * 80 + "\n\n")
                
                # 计算分布数量和占比
                value_counts = df[column].value_counts()
                total_count = len(df)
                
                # 创建表格标题
                f.write(f"{'类别':<20} {'数量':<10} {'占比':<10}\n")
                f.write(f"{'-'*20} {'-'*10} {'-'*10}\n")
                
                # 写入各个类别的数量和占比
                for category, count in value_counts.items():
                    percentage = (count / total_count) * 100
                    f.write(f"{str(category):<20} {count:<10} {percentage:.2f}%\n")
                
                # 计算汇总信息
                f.write(f"{'-'*20} {'-'*10} {'-'*10}\n")
                f.write(f"{'总计':<20} {total_count:<10} 100.00%\n\n")
                
                # 添加额外的分析信息
                f.write(f"类别数量: {len(value_counts)}\n")
                f.write(f"最常见类别: {value_counts.index[0]} ({value_counts.iloc[0]} 次，占比 {(value_counts.iloc[0]/total_count)*100:.2f}%)\n")
                f.write(f"最少见类别: {value_counts.index[-1]} ({value_counts.iloc[-1]} 次，占比 {(value_counts.iloc[-1]/total_count)*100:.2f}%)\n\n")
            
            # 添加最后的总结
            f.write("=" * 80 + "\n")
            f.write("分析总结\n")
            f.write("=" * 80 + "\n\n")
            
            # 计算每个分类列的熵作为多样性指标
            for column in categorical_columns:
                probs = df[column].value_counts(normalize=True)
                entropy = -sum(probs * probs.apply(lambda x: pd.np.log2(x) if x > 0 else 0))
                normalized_entropy = entropy / pd.np.log2(len(probs)) if len(probs) > 1 else 0
                
                f.write(f"{column} 多样性指标: {normalized_entropy:.4f} (0表示单一值，1表示完全均匀分布)\n")
            
            f.write("\n分析完成！\n")
        
        print(f"分析结果已保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"处理数据时出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 文件路径
    csv_file_path = "temp_csv/excel_data_20250317161158.csv"
    output_file_path = "pngs/category_distribution_results.txt"
    
    # 执行分析
    success = analyze_csv_distributions(csv_file_path, output_file_path)
    
    if success:
        print("分析成功完成！")
    else:
        print("分析过程中出现错误。")