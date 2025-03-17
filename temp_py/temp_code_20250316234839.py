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
        required_columns = ["Category", "Item", "Price", "Date", "Week", "Month", "Sales", "Revenue"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"CSV文件缺少以下列: {', '.join(missing_columns)}")
        
        # 数据预处理
        # 转换日期列为日期类型
        df['Date'] = pd.to_datetime(df['Date'])
        # 处理缺失值
        df['Sales'].fillna(0, inplace=True)
        df['Revenue'].fillna(df['Price'] * df['Sales'], inplace=True)
        
        # 创建结果文件
        with open('analysis_results.txt', 'w', encoding='utf-8') as f:
            # 1. 基本统计信息
            f.write("===== 基本统计信息 =====\n")
            f.write(f"数据记录总数: {len(df)}\n")
            f.write(f"日期范围: {df['Date'].min().strftime('%Y-%m-%d')} 至 {df['Date'].max().strftime('%Y-%m-%d')}\n\n")
            
            # 2. 销售和收入统计
            f.write("===== 销售和收入统计 =====\n")
            sales_stats = df['Sales'].describe()
            revenue_stats = df['Revenue'].describe()
            f.write(f"销售数量统计:\n")
            f.write(f"  总销售量: {df['Sales'].sum()}\n")
            f.write(f"  平均销售量: {sales_stats['mean']:.2f}\n")
            f.write(f"  最大销售量: {sales_stats['max']}\n")
            f.write(f"  最小销售量: {sales_stats['min']}\n\n")
            
            f.write(f"销售收入统计:\n")
            f.write(f"  总收入: {df['Revenue'].sum():.2f}\n")
            f.write(f"  平均收入: {revenue_stats['mean']:.2f}\n")
            f.write(f"  最大收入: {revenue_stats['max']:.2f}\n")
            f.write(f"  最小收入: {revenue_stats['min']:.2f}\n\n")
            
            # 3. 按月份分组分析
            f.write("===== 月度销售分析 =====\n")
            monthly_sales = df.groupby('Month')[['Sales', 'Revenue']].sum().reset_index()
            # 按月份排序
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            monthly_sales['Month'] = pd.Categorical(monthly_sales['Month'], categories=month_order, ordered=True)
            monthly_sales = monthly_sales.sort_values('Month')
            
            for _, row in monthly_sales.iterrows():
                f.write(f"{row['Month']}: 销售量 {row['Sales']}, 收入 {row['Revenue']:.2f}\n")
            f.write("\n")
            
            # 4. 按周分组分析
            f.write("===== 周度销售分析 =====\n")
            weekly_sales = df.groupby('Week')[['Sales', 'Revenue']].sum().reset_index()
            for _, row in weekly_sales.iterrows():
                f.write(f"{row['Week']}: 销售量 {row['Sales']}, 收入 {row['Revenue']:.2f}\n")
            f.write("\n")
            
            # 5. 按产品类别分析
            f.write("===== 产品类别分析 =====\n")
            category_sales = df.groupby('Category')[['Sales', 'Revenue']].sum().reset_index()
            for _, row in category_sales.iterrows():
                f.write(f"{row['Category']}: 销售量 {row['Sales']}, 收入 {row['Revenue']:.2f}\n")
            f.write("\n")
            
            # 6. 按商品分析
            f.write("===== 商品销售分析 =====\n")
            item_sales = df.groupby('Item')[['Sales', 'Revenue']].sum().reset_index()
            item_sales = item_sales.sort_values('Revenue', ascending=False)
            for _, row in item_sales.iterrows():
                f.write(f"{row['Item']}: 销售量 {row['Sales']}, 收入 {row['Revenue']:.2f}\n")
        
        print(f"分析完成，结果已保存到 'analysis_results.txt'")
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{file_path}'")
    except pd.errors.EmptyDataError:
        print(f"错误: 文件 '{file_path}' 为空或格式不正确")
    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv文件路径>")
    else:
        csv_path = sys.argv[1]
        analyze_sales_data(csv_path)