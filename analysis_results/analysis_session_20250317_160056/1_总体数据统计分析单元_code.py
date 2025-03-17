import pandas as pd
import numpy as np
import os
from datetime import datetime

def analyze_csv_data(file_path, output_path):
    """
    分析CSV文件数据并将结果保存为纯文本格式
    
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
        result.append("CSV数据分析报告")
        result.append("=" * 80)
        result.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result.append(f"文件路径: {file_path}")
        result.append(f"数据行数: {len(df)}")
        result.append(f"数据列数: {len(df.columns)}")
        result.append("")
        
        # 基本描述性统计
        result.append("=" * 80)
        result.append("1. 基本描述性统计")
        result.append("=" * 80)
        
        # 处理数值列的描述性统计
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            result.append("\n数值列统计:")
            stats = df[numeric_cols].describe().T
            for col in stats.index:
                result.append(f"\n{col}:")
                result.append(f"  计数: {stats.loc[col, 'count']:.0f}")
                result.append(f"  均值: {stats.loc[col, 'mean']:.2f}")
                result.append(f"  标准差: {stats.loc[col, 'std']:.2f}")
                result.append(f"  最小值: {stats.loc[col, 'min']:.2f}")
                result.append(f"  25%分位数: {stats.loc[col, '25%']:.2f}")
                result.append(f"  中位数: {stats.loc[col, '50%']:.2f}")
                result.append(f"  75%分位数: {stats.loc[col, '75%']:.2f}")
                result.append(f"  最大值: {stats.loc[col, 'max']:.2f}")
                result.append(f"  缺失值数量: {df[col].isna().sum()}")
        
        # 分类列分析
        result.append("\n" + "=" * 80)
        result.append("2. 分类列分布分析")
        result.append("=" * 80)
        
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        for col in categorical_cols:
            result.append(f"\n{col}:")
            value_counts = df[col].value_counts()
            total = len(df)
            result.append(f"  唯一值数量: {df[col].nunique()}")
            result.append(f"  缺失值数量: {df[col].isna().sum()}")
            result.append("  前5个最常见值:")
            
            for i, (value, count) in enumerate(value_counts.head(5).items()):
                percentage = (count / total) * 100
                result.append(f"    {value}: {count} ({percentage:.2f}%)")
        
        # 时间分析 (假设Date_Reported和Resolution_Date是日期列)
        if 'Date_Reported' in df.columns and 'Resolution_Date' in df.columns:
            result.append("\n" + "=" * 80)
            result.append("3. 时间相关分析")
            result.append("=" * 80)
            
            # 转换日期列
            try:
                df['Date_Reported'] = pd.to_datetime(df['Date_Reported'])
                df['Resolution_Date'] = pd.to_datetime(df['Resolution_Date'])
                
                # 按月份统计投诉数量
                result.append("\n按月份统计投诉数量:")
                monthly_complaints = df['Date_Reported'].dt.to_period('M').value_counts().sort_index()
                for period, count in monthly_complaints.items():
                    result.append(f"  {period}: {count}")
                
                # 分析解决时间
                if 'Resolution_Time_Days' in df.columns:
                    result.append("\n解决时间分析:")
                    resolution_stats = df['Resolution_Time_Days'].describe()
                    result.append(f"  平均解决时间: {resolution_stats['mean']:.2f} 天")
                    result.append(f"  最短解决时间: {resolution_stats['min']:.2f} 天")
                    result.append(f"  最长解决时间: {resolution_stats['max']:.2f} 天")
                    result.append(f"  中位数解决时间: {resolution_stats['50%']:.2f} 天")
            except Exception as e:
                result.append(f"\n日期转换错误: {str(e)}")
        
        # 关联分析
        result.append("\n" + "=" * 80)
        result.append("4. 关联分析")
        result.append("=" * 80)
        
        # 投诉类型与优先级的关系
        if 'Complaint_Type' in df.columns and 'Priority' in df.columns:
            result.append("\n投诉类型与优先级的关系:")
            ct_priority = pd.crosstab(df['Complaint_Type'], df['Priority'], normalize='index') * 100
            for complaint_type in ct_priority.index:
                result.append(f"\n  {complaint_type}:")
                for priority in ct_priority.columns:
                    result.append(f"    {priority}: {ct_priority.loc[complaint_type, priority]:.2f}%")
        
        # 区域与投诉类型的关系
        if 'Region' in df.columns and 'Complaint_Type' in df.columns:
            result.append("\n区域与投诉类型的关系:")
            region_complaint = pd.crosstab(df['Region'], df['Complaint_Type'], normalize='index') * 100
            for region in region_complaint.index:
                result.append(f"\n  {region}:")
                for complaint_type in region_complaint.columns:
                    result.append(f"    {complaint_type}: {region_complaint.loc[region, complaint_type]:.2f}%")
        
        # 客户满意度分析
        if 'Customer_Satisfaction' in df.columns:
            result.append("\n" + "=" * 80)
            result.append("5. 客户满意度分析")
            result.append("=" * 80)
            
            satisfaction = df['Customer_Satisfaction'].dropna()
            result.append(f"\n客户满意度评分分布:")
            for score in sorted(satisfaction.unique()):
                count = (satisfaction == score).sum()
                percentage = (count / len(satisfaction)) * 100
                result.append(f"  评分 {score}: {count} ({percentage:.2f}%)")
            
            # 按服务类型的满意度
            if 'Service_Type' in df.columns:
                result.append("\n按服务类型的平均满意度:")
                service_satisfaction = df.groupby('Service_Type')['Customer_Satisfaction'].mean()
                for service, avg_score in service_satisfaction.items():
                    result.append(f"  {service}: {avg_score:.2f}")
        
        # 保存结果到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result))
        
        print(f"分析完成，结果已保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        return False

# 执行分析
if __name__ == "__main__":
    csv_path = "temp_csv/excel_data_20250317160056.csv"
    output_path = "pngs/analysis_results.txt"
    analyze_csv_data(csv_path, output_path)