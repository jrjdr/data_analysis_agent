import pandas as pd
import numpy as np
import os
from datetime import datetime

def analyze_csv_data(file_path, output_path):
    """
    分析CSV文件数据并生成统计报告
    
    参数:
        file_path: CSV文件路径
        output_path: 输出结果文件路径
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 读取CSV文件
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 准备分析结果文本
        result = []
        
        # 添加标题和基本信息
        result.append("=" * 80)
        result.append("客户投诉数据分析报告")
        result.append("=" * 80)
        result.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result.append(f"数据文件: {file_path}")
        result.append(f"记录数量: {len(df)}")
        result.append(f"字段数量: {len(df.columns)}")
        result.append("")
        
        # 1. 基本数据概览
        result.append("-" * 80)
        result.append("1. 基本数据概览")
        result.append("-" * 80)
        
        # 数据类型和缺失值信息
        result.append("数据类型和缺失值:")
        dtype_info = []
        for col in df.columns:
            missing = df[col].isna().sum()
            missing_percent = (missing / len(df)) * 100
            dtype_info.append(f"  {col}: 类型={df[col].dtype}, 缺失值={missing} ({missing_percent:.2f}%)")
        result.extend(dtype_info)
        result.append("")
        
        # 2. 数值列分析
        result.append("-" * 80)
        result.append("2. 数值列分析")
        result.append("-" * 80)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            for col in numeric_cols:
                result.append(f"\n{col} 统计分析:")
                stats = df[col].describe()
                result.append(f"  计数: {stats['count']:.0f}")
                result.append(f"  均值: {stats['mean']:.2f}")
                result.append(f"  标准差: {stats['std']:.2f}")
                result.append(f"  最小值: {stats['min']:.2f}")
                result.append(f"  25%分位数: {stats['25%']:.2f}")
                result.append(f"  中位数: {stats['50%']:.2f}")
                result.append(f"  75%分位数: {stats['75%']:.2f}")
                result.append(f"  最大值: {stats['max']:.2f}")
                
                # 计算分布情况
                if not pd.isna(df[col]).all():
                    value_counts = df[col].value_counts().sort_index()
                    result.append(f"  值分布:")
                    for val, count in value_counts.items():
                        result.append(f"    {val}: {count} ({count/len(df)*100:.2f}%)")
        else:
            result.append("没有发现数值列")
        
        # 3. 分类列分析
        result.append("\n" + "-" * 80)
        result.append("3. 分类列分析")
        result.append("-" * 80)
        
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        for col in categorical_cols:
            result.append(f"\n{col} 分布:")
            value_counts = df[col].value_counts()
            unique_count = len(value_counts)
            result.append(f"  唯一值数量: {unique_count}")
            
            # 如果唯一值太多，只显示前10个
            if unique_count > 10:
                result.append("  前10个最常见值:")
                for val, count in value_counts.head(10).items():
                    result.append(f"    {val}: {count} ({count/len(df)*100:.2f}%)")
            else:
                result.append("  所有值分布:")
                for val, count in value_counts.items():
                    result.append(f"    {val}: {count} ({count/len(df)*100:.2f}%)")
        
        # 4. 特定业务分析
        result.append("\n" + "-" * 80)
        result.append("4. 业务特定分析")
        result.append("-" * 80)
        
        # 按区域分析投诉类型
        if 'Region' in df.columns and 'Complaint_Type' in df.columns:
            result.append("\n按区域分析投诉类型:")
            region_complaint = pd.crosstab(df['Region'], df['Complaint_Type'])
            result.append(str(region_complaint))
        
        # 按服务类型分析优先级
        if 'Service_Type' in df.columns and 'Priority' in df.columns:
            result.append("\n按服务类型分析优先级:")
            service_priority = pd.crosstab(df['Service_Type'], df['Priority'])
            result.append(str(service_priority))
        
        # 分析解决时间
        if 'Resolution_Time_Days' in df.columns:
            result.append("\n解决时间分析:")
            resolution_by_type = df.groupby('Complaint_Type')['Resolution_Time_Days'].agg(['mean', 'median', 'min', 'max']).round(2)
            result.append(str(resolution_by_type))
        
        # 客户满意度分析
        if 'Customer_Satisfaction' in df.columns:
            result.append("\n客户满意度分析:")
            satisfaction_by_type = df.groupby('Complaint_Type')['Customer_Satisfaction'].agg(['mean', 'median', 'min', 'max', 'count']).round(2)
            result.append(str(satisfaction_by_type))
        
        # 5. 结论和建议
        result.append("\n" + "-" * 80)
        result.append("5. 结论和建议")
        result.append("-" * 80)
        
        # 计算一些关键指标
        if 'Status' in df.columns:
            open_cases = df[df['Status'] != 'Closed'].shape[0]
            open_percent = (open_cases / len(df)) * 100
            result.append(f"• 未关闭案例: {open_cases} ({open_percent:.2f}%)")
        
        if 'Resolution_Time_Days' in df.columns:
            avg_resolution = df['Resolution_Time_Days'].mean()
            result.append(f"• 平均解决时间: {avg_resolution:.2f} 天")
        
        if 'Customer_Satisfaction' in df.columns:
            low_satisfaction = df[df['Customer_Satisfaction'] <= 2].shape[0]
            low_percent = (low_satisfaction / df['Customer_Satisfaction'].count()) * 100
            result.append(f"• 低满意度案例(≤2): {low_satisfaction} ({low_percent:.2f}%)")
        
        # 写入结果到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result))
        
        print(f"分析完成，结果已保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    csv_file = "temp_csv/excel_data_20250317154509.csv"
    output_file = "pngs/analysis_results.txt"
    analyze_csv_data(csv_file, output_file)