import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime

def analyze_for_bar_charts(file_path):
    """
    分析CSV数据，生成适合柱状图展示的数据
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 存储分析结果
        results = {}
        
        # 1. 按类别统计销售额和销量
        category_revenue = df.groupby('Category')['Revenue'].sum().sort_values(ascending=False).to_dict()
        category_sales = df.groupby('Category')['Sales'].sum().sort_values(ascending=False).to_dict()
        results['category_comparison'] = {
            'revenue_by_category': category_revenue,
            'sales_by_category': category_sales
        }
        
        # 2. 按月份统计销售额和销量
        monthly_revenue = df.groupby('Month')['Revenue'].sum().to_dict()
        monthly_sales = df.groupby('Month')['Sales'].sum().to_dict()
        
        # 确保月份按时间顺序排列
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        ordered_monthly_revenue = {month: monthly_revenue.get(month, 0) for month in month_order if month in monthly_revenue}
        ordered_monthly_sales = {month: monthly_sales.get(month, 0) for month in month_order if month in monthly_sales}
        
        results['monthly_comparison'] = {
            'revenue_by_month': ordered_monthly_revenue,
            'sales_by_month': ordered_monthly_sales
        }
        
        # 3. 销量最高的前10个商品
        top_items_by_sales = df.groupby('Item')['Sales'].sum().sort_values(ascending=False).head(10).to_dict()
        results['top_items'] = {
            'top_10_items_by_sales': top_items_by_sales
        }
        
        # 4. 按价格区间统计商品数量
        df['Price_Range'] = pd.cut(df['Price'], 
                                  bins=[0, 50, 100, 150, 200],
                                  labels=['0-50', '51-100', '101-150', '151-200'])
        price_range_counts = df['Price_Range'].value_counts().sort_index().to_dict()
        results['price_distribution'] = price_range_counts
        
        # 5. 每个类别的平均价格
        avg_price_by_category = df.groupby('Category')['Price'].mean().sort_values(ascending=False).to_dict()
        results['average_prices'] = {
            'avg_price_by_category': avg_price_by_category
        }
        
        # 6. 每个类别的商品数量
        item_count_by_category = df.groupby(['Category', 'Item']).size().groupby(level=0).count().to_dict()
        results['item_counts'] = {
            'item_count_by_category': item_count_by_category
        }
        
        # 7. 周销售趋势（取前10周）
        weekly_sales = df.groupby('Week')['Sales'].sum().head(10).to_dict()
        results['weekly_trends'] = {
            'sales_by_week': weekly_sales
        }
        
        # 8. 类别占总销售额的百分比
        total_revenue = df['Revenue'].sum()
        category_revenue_percent = (df.groupby('Category')['Revenue'].sum() / total_revenue * 100).to_dict()
        results['category_percentage'] = {
            'revenue_percent_by_category': category_revenue_percent
        }
        
        return results
    
    except Exception as e:
        return {"error": str(e)}

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
    results = analyze_for_bar_charts(file_path)
    
    # 保存结果到JSON文件
    output_file = 'bar_chart_analysis_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print(f"分析完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    main()