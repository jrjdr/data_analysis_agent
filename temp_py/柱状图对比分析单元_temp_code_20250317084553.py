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
        analysis_results = {}
        
        # 1. 按类别统计销售额和销量
        category_revenue = df.groupby('Category')['Revenue'].sum().sort_values(ascending=False).to_dict()
        category_sales = df.groupby('Category')['Sales'].sum().sort_values(ascending=False).to_dict()
        analysis_results['category_comparison'] = {
            'revenue_by_category': category_revenue,
            'sales_by_category': category_sales
        }
        
        # 2. 按月份统计销售额和销量
        monthly_revenue = df.groupby('Month')['Revenue'].sum().to_dict()
        monthly_sales = df.groupby('Month')['Sales'].sum().to_dict()
        
        # 确保月份按正确顺序排列
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        ordered_monthly_revenue = {month: monthly_revenue.get(month, 0) for month in month_order if month in monthly_revenue}
        ordered_monthly_sales = {month: monthly_sales.get(month, 0) for month in month_order if month in monthly_sales}
        
        analysis_results['monthly_comparison'] = {
            'revenue_by_month': ordered_monthly_revenue,
            'sales_by_month': ordered_monthly_sales
        }
        
        # 3. 销量最高的前10个商品
        top_items_by_sales = df.groupby('Item')['Sales'].sum().sort_values(ascending=False).head(10).to_dict()
        analysis_results['top_items'] = {
            'top_10_items_by_sales': top_items_by_sales
        }
        
        # 4. 按类别统计平均价格
        avg_price_by_category = df.groupby('Category')['Price'].mean().sort_values(ascending=False).to_dict()
        analysis_results['price_comparison'] = {
            'average_price_by_category': avg_price_by_category
        }
        
        # 5. 计算每个类别的商品数量占比
        item_count_by_category = df['Category'].value_counts().to_dict()
        total_items = sum(item_count_by_category.values())
        item_percentage_by_category = {category: (count / total_items) * 100 for category, count in item_count_by_category.items()}
        analysis_results['category_distribution'] = {
            'item_count_by_category': item_count_by_category,
            'item_percentage_by_category': item_percentage_by_category
        }
        
        # 6. 计算每个类别的平均销量
        avg_sales_by_category = df.groupby('Category')['Sales'].mean().sort_values(ascending=False).to_dict()
        analysis_results['average_sales'] = {
            'average_sales_by_category': avg_sales_by_category
        }
        
        # 7. 按周统计销售额趋势
        weekly_revenue = df.groupby('Week')['Revenue'].sum().to_dict()
        analysis_results['weekly_trend'] = {
            'revenue_by_week': weekly_revenue
        }
        
        # 8. 计算每个商品的总收入并找出收入最高的前10个商品
        top_items_by_revenue = df.groupby('Item')['Revenue'].sum().sort_values(ascending=False).head(10).to_dict()
        analysis_results['top_revenue_items'] = {
            'top_10_items_by_revenue': top_items_by_revenue
        }
        
        return analysis_results
        
    except Exception as e:
        return {"error": str(e)}

def save_to_json(data, output_file='bar_chart_analysis_results.json'):
    """
    将分析结果保存为JSON文件
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存JSON文件时出错: {e}")
        return False

def main():
    """
    主函数，处理命令行参数并执行分析
    """
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("请提供CSV文件路径作为命令行参数")
        print("用法: python script.py <csv_file_path>")
        return
    
    file_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    # 执行分析
    print(f"正在分析文件: {file_path}")
    results = analyze_for_bar_charts(file_path)
    
    # 保存结果
    if "error" not in results:
        if save_to_json(results):
            print(f"分析结果已保存到 bar_chart_analysis_results.json")
        else:
            print("保存分析结果时出错")
    else:
        print(f"分析过程中出错: {results['error']}")

if __name__ == "__main__":
    main()