import pandas as pd
import sys
import os
from datetime import datetime

def analyze_sales_data(file_path):
    """
    分析销售数据并将结果保存到文本文件
    
    参数:
        file_path: CSV文件路径
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 检查必要的列是否存在
        required_columns = ['Category', 'Item', 'Price', 'Date', 'Week', 'Month', 'Sales', 'Revenue']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"CSV文件缺少以下列: {', '.join(missing_columns)}")
        
        # 数据预处理
        # 转换日期列为日期类型
        df['Date'] = pd.to_datetime(df['Date'])
        
        # 处理缺失值
        missing_values = df.isnull().sum()
        df.fillna({'Sales': 0, 'Revenue': 0}, inplace=True)  # 销量和收入缺失值填充为0
        df.dropna(inplace=True)  # 删除其他列的缺失值行
        
        # 基础统计分析
        basic_stats = df[['Price', 'Sales', 'Revenue']].describe()
        
        # 按类别分组统计
        category_stats = df.groupby('Category').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        
        # 按月份分组统计
        monthly_stats = df.groupby('Month').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        
        # 按周分组统计
        weekly_stats = df.groupby('Week').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        
        # 计算最畅销商品
        top_items = df.groupby('Item').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).sort_values('Sales', ascending=False).head(5)
        
        # 计算平均单价
        avg_price = df['Price'].mean()
        
        # 计算总销售额和总销量
        total_sales = df['Sales'].sum()
        total_revenue = df['Revenue'].sum()
        
        # 将结果写入文本文件
        with open('analysis_results.txt', 'w', encoding='utf-8') as f:
            f.write("销售数据分析结果\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("1. 基础统计信息\n")
            f.write("-" * 50 + "\n")
            f.write(f"总销量: {total_sales}\n")
            f.write(f"总收入: {total_revenue:.2f}\n")
            f.write(f"平均单价: {avg_price:.2f}\n\n")
            
            f.write("2. 数值型字段统计\n")
            f.write("-" * 50 + "\n")
            f.write(basic_stats.to_string() + "\n\n")
            
            f.write("3. 缺失值统计\n")
            f.write("-" * 50 + "\n")
            f.write(missing_values.to_string() + "\n\n")
            
            f.write("4. 按类别统计\n")
            f.write("-" * 50 + "\n")
            f.write(category_stats.to_string(index=False) + "\n\n")
            
            f.write("5. 按月份统计\n")
            f.write("-" * 50 + "\n")
            f.write(monthly_stats.to_string(index=False) + "\n\n")
            
            f.write("6. 按周统计\n")
            f.write("-" * 50 + "\n")
            f.write(weekly_stats.to_string(index=False) + "\n\n")
            
            f.write("7. 最畅销商品(Top 5)\n")
            f.write("-" * 50 + "\n")
            f.write(top_items.to_string() + "\n")
            
        print(f"分析完成，结果已保存到 'analysis_results.txt'")
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{file_path}'")
    except pd.errors.EmptyDataError:
        print(f"错误: 文件 '{file_path}' 为空或格式不正确")
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv文件路径>")
    else:
        csv_path = sys.argv[1]
        analyze_sales_data(csv_path)