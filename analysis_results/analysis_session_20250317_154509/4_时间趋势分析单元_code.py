import pandas as pd
import numpy as np
import os
from datetime import datetime
from collections import Counter

def load_csv_data(file_path):
    """加载CSV文件数据"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载CSV文件，共{len(df)}行数据")
        return df
    except Exception as e:
        print(f"加载CSV文件时出错: {e}")
        return None

def convert_date_columns(df):
    """将日期列转换为datetime格式"""
    try:
        # 转换日期列
        date_columns = ['Date_Reported', 'Resolution_Date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 计算每周和每月
        if 'Date_Reported' in df.columns:
            df['Year_Week'] = df['Date_Reported'].dt.strftime('%Y-%U')
            df['Year_Month'] = df['Date_Reported'].dt.strftime('%Y-%m')
        
        return df
    except Exception as e:
        print(f"转换日期列时出错: {e}")
        return df

def analyze_time_trends(df):
    """分析时间趋势"""
    results = []
    
    try:
        # 1. 按日期统计投诉数量
        daily_counts = df.groupby('Date_Reported').size()
        
        # 计算每日投诉的基本统计信息
        results.append("===== 每日投诉统计 =====")
        results.append(f"总投诉数: {len(df)}")
        results.append(f"日均投诉数: {daily_counts.mean():.2f}")
        results.append(f"最高单日投诉数: {daily_counts.max()} (日期: {daily_counts.idxmax().strftime('%Y-%m-%d')})")
        results.append(f"最低单日投诉数: {daily_counts.min()} (日期: {daily_counts.idxmin().strftime('%Y-%m-%d')})")
        results.append(f"投诉数标准差: {daily_counts.std():.2f}")
        
        # 2. 按周统计投诉趋势
        weekly_counts = df.groupby('Year_Week').size()
        results.append("\n===== 每周投诉趋势 =====")
        results.append(f"周均投诉数: {weekly_counts.mean():.2f}")
        results.append(f"投诉量最高的一周: {weekly_counts.idxmax()} (数量: {weekly_counts.max()})")
        results.append(f"投诉量最低的一周: {weekly_counts.idxmin()} (数量: {weekly_counts.min()})")
        
        # 计算周环比变化
        weekly_change = weekly_counts.pct_change() * 100
        results.append(f"周环比平均变化率: {weekly_change.mean():.2f}%")
        
        # 3. 按月统计投诉趋势
        monthly_counts = df.groupby('Year_Month').size()
        results.append("\n===== 每月投诉趋势 =====")
        results.append(f"月均投诉数: {monthly_counts.mean():.2f}")
        results.append(f"投诉量最高的月份: {monthly_counts.idxmax()} (数量: {monthly_counts.max()})")
        results.append(f"投诉量最低的月份: {monthly_counts.idxmin()} (数量: {monthly_counts.min()})")
        
        # 4. 分析投诉类型随时间的变化
        results.append("\n===== 投诉类型随时间变化 =====")
        complaint_type_monthly = df.groupby(['Year_Month', 'Complaint_Type']).size().unstack(fill_value=0)
        
        # 获取最近三个月的数据
        recent_months = sorted(df['Year_Month'].unique())[-3:]
        for month in recent_months:
            if month in complaint_type_monthly.index:
                results.append(f"\n月份: {month}")
                for complaint_type, count in complaint_type_monthly.loc[month].sort_values(ascending=False).items():
                    results.append(f"  {complaint_type}: {count}件")
        
        # 5. 分析解决时间趋势
        results.append("\n===== 解决时间趋势分析 =====")
        # 按月计算平均解决时间
        resolution_time_monthly = df.groupby('Year_Month')['Resolution_Time_Days'].mean()
        
        results.append("月度平均解决时间(天):")
        for month, avg_time in resolution_time_monthly.items():
            results.append(f"  {month}: {avg_time:.2f}天")
        
        # 计算解决时间趋势
        resolution_change = resolution_time_monthly.pct_change() * 100
        avg_change = resolution_change.mean()
        results.append(f"解决时间月环比平均变化率: {avg_change:.2f}%")
        
        if avg_change < 0:
            results.append("解决时间呈下降趋势，服务效率有所提高")
        elif avg_change > 0:
            results.append("解决时间呈上升趋势，服务效率有所下降")
        else:
            results.append("解决时间保持稳定")
        
        # 6. 分析客户满意度趋势
        results.append("\n===== 客户满意度趋势分析 =====")
        satisfaction_monthly = df.groupby('Year_Month')['Customer_Satisfaction'].mean()
        
        results.append("月度平均客户满意度(1-5分):")
        for month, avg_satisfaction in satisfaction_monthly.items():
            results.append(f"  {month}: {avg_satisfaction:.2f}")
        
        # 计算满意度趋势
        satisfaction_change = satisfaction_monthly.pct_change() * 100
        avg_satisfaction_change = satisfaction_change.mean()
        results.append(f"客户满意度月环比平均变化率: {avg_satisfaction_change:.2f}%")
        
        # 7. 识别异常点
        results.append("\n===== 异常点分析 =====")
        # 使用Z-score方法识别异常的日投诉量
        z_scores = (daily_counts - daily_counts.mean()) / daily_counts.std()
        outliers = daily_counts[abs(z_scores) > 2]
        
        if len(outliers) > 0:
            results.append(f"发现{len(outliers)}个异常日期(投诉量异常):")
            for date, count in outliers.items():
                z = z_scores[date]
                direction = "高于" if z > 0 else "低于"
                results.append(f"  {date.strftime('%Y-%m-%d')}: {count}件投诉 ({direction}平均值{abs(z):.2f}个标准差)")
        else:
            results.append("未发现明显的投诉量异常日期")
        
        return results
    except Exception as e:
        print(f"分析时间趋势时出错: {e}")
        return ["分析过程中出现错误，请检查数据格式和完整性"]

def save_results(results, output_path):
    """保存分析结果到文本文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("投诉数据时间趋势分析报告\n")
            f.write("=" * 50 + "\n\n")
            f.write("生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            
            for line in results:
                f.write(line + "\n")
                
        print(f"分析结果已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存结果时出错: {e}")
        return False

def main():
    # 文件路径
    csv_path = "temp_csv/excel_data_20250317154509.csv"
    output_path = "pngs/time_trend_results.txt"
    
    # 1. 加载数据
    df = load_csv_data(csv_path)
    if df is None:
        return
    
    # 2. 转换日期列
    df = convert_date_columns(df)
    
    # 3. 分析时间趋势
    results = analyze_time_trends(df)
    
    # 4. 保存结果
    save_results(results, output_path)

if __name__ == "__main__":
    main()