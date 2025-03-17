import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime

def analyze_pie_chart_data(file_path):
    """
    分析CSV数据，生成适合饼图展示的比例数据
    
    Args:
        file_path: CSV文件路径
    
    Returns:
        包含饼图数据的字典
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 初始化结果字典
        pie_chart_data = {}
        
        # 1. 按类别(Category)分析销售额占比
        category_revenue = df.groupby('Category')['Revenue'].sum().reset_index()
        total_revenue = category_revenue['Revenue'].sum()
        category_revenue['Percentage'] = (category_revenue['Revenue'] / total_revenue * 100).round(2)
        pie_chart_data['category_revenue_distribution'] = category_revenue[['Category', 'Percentage']].to_dict('records')
        
        # 2. 按商品(Item)分析销售量占比
        item_sales = df.groupby('Item')['Sales'].sum().reset_index()
        total_sales = item_sales['Sales'].sum()
        item_sales['Percentage'] = (item_sales['Sales'] / total_sales * 100).round(2)
        # 只保留前10个商品，其余归为"其他"类别
        if len(item_sales) > 10:
            top_items = item_sales.nlargest(10, 'Percentage')
            other_percentage = 100 - top_items['Percentage'].sum()
            top_items = top_items.append({'Item': '其他', 'Sales': 0, 'Percentage': round(other_percentage, 2)}, 
                                        ignore_index=True)
            pie_chart_data['item_sales_distribution'] = top_items[['Item', 'Percentage']].to_dict('records')
        else:
            pie_chart_data['item_sales_distribution'] = item_sales[['Item', 'Percentage']].to_dict('records')
        
        # 3. 按月份(Month)分析销售额占比
        month_revenue = df.groupby('Month')['Revenue'].sum().reset_index()
        month_revenue['Percentage'] = (month_revenue['Revenue'] / total_revenue * 100).round(2)
        # 按月份顺序排序
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_revenue['Month'] = pd.Categorical(month_revenue['Month'], categories=month_order, ordered=True)
        month_revenue = month_revenue.sort_values('Month')
        pie_chart_data['monthly_revenue_distribution'] = month_revenue[['Month', 'Percentage']].to_dict('records')
        
        # 4. 价格区间分析
        # 创建价格区间
        bins = [0, 50, 100, 150, 200]
        labels = ['0-50', '51-100', '101-150', '151-200']
        df['Price_Range'] = pd.cut(df['Price'], bins=bins, labels=labels, right=False)
        price_range_count = df['Price_Range'].value_counts().reset_index()
        price_range_count.columns = ['Price_Range', 'Count']
        price_range_count['Percentage'] = (price_range_count['Count'] / len(df) * 100).round(2)
        pie_chart_data['price_range_distribution'] = price_range_count[['Price_Range', 'Percentage']].to_dict('records')
        
        # 5. 按周(Week)分析销售量占比
        # 只取前10周数据，其余归为"其他"类别
        week_sales = df.groupby('Week')['Sales'].sum().reset_index()
        week_sales['Percentage'] = (week_sales['Sales'] / total_sales * 100).round(2)
        if len(week_sales) > 10:
            top_weeks = week_sales.nlargest(10, 'Sales')
            other_percentage = 100 - top_weeks['Percentage'].sum()
            top_weeks = top_weeks.append({'Week': '其他周', 'Sales': 0, 'Percentage': round(other_percentage, 2)}, 
                                        ignore_index=True)
            pie_chart_data['weekly_sales_distribution'] = top_weeks[['Week', 'Percentage']].to_dict('records')
        else:
            pie_chart_data['weekly_sales_distribution'] = week_sales[['Week', 'Percentage']].to_dict('records')
        
        return pie_chart_data
        
    except Exception as e:
        print(f"分析数据时出错: {str(e)}")
        return None

def main():
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("用法: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    
    # 分析数据
    pie_chart_data = analyze_pie_chart_data(file_path)
    
    if pie_chart_data:
        # 将结果保存为JSON文件
        output_file = 'pie_chart_analysis_results.json'
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(pie_chart_data, f, ensure_ascii=False, indent=4)
            print(f"分析结果已保存到 {output_file}")
        except Exception as e:
            print(f"保存结果时出错: {str(e)}")
    else:
        print("分析失败，未生成结果")

if __name__ == "__main__":
    main()