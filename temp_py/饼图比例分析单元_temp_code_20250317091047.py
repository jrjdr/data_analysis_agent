import pandas as pd
import numpy as np
import json
import sys
import os
from typing import Dict, Any, List

def load_data(file_path: str) -> pd.DataFrame:
    """加载CSV数据文件"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"加载数据失败: {e}")
        sys.exit(1)

def calculate_category_sales_proportion(df: pd.DataFrame) -> Dict[str, float]:
    """计算不同类别销售额占总销售额的比例"""
    try:
        category_revenue = df.groupby('Category')['Revenue'].sum()
        total_revenue = category_revenue.sum()
        proportions = (category_revenue / total_revenue * 100).round(2)
        return proportions.to_dict()
    except Exception as e:
        print(f"计算类别销售额比例失败: {e}")
        return {}

def calculate_item_sales_proportion(df: pd.DataFrame) -> Dict[str, float]:
    """计算不同商品销售额占总销售额的比例"""
    try:
        item_revenue = df.groupby('Item')['Revenue'].sum()
        total_revenue = item_revenue.sum()
        # 只保留前10个最大的项目，其余归为"其他"类别
        top_items = item_revenue.nlargest(10)
        others = pd.Series([item_revenue.sum() - top_items.sum()], index=['其他'])
        combined = pd.concat([top_items, others])
        proportions = (combined / total_revenue * 100).round(2)
        return proportions.to_dict()
    except Exception as e:
        print(f"计算商品销售额比例失败: {e}")
        return {}

def calculate_monthly_sales_proportion(df: pd.DataFrame) -> Dict[str, float]:
    """计算不同月份销售额占总销售额的比例"""
    try:
        monthly_revenue = df.groupby('Month')['Revenue'].sum()
        total_revenue = monthly_revenue.sum()
        proportions = (monthly_revenue / total_revenue * 100).round(2)
        
        # 确保月份按正确顺序排列
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        proportions = proportions.reindex(month_order)
        
        return proportions.to_dict()
    except Exception as e:
        print(f"计算月度销售额比例失败: {e}")
        return {}

def calculate_price_range_distribution(df: pd.DataFrame) -> Dict[str, float]:
    """计算不同价格区间的商品分布比例"""
    try:
        # 创建价格区间
        bins = [0, 50, 100, 150, 200]
        labels = ['0-50', '51-100', '101-150', '151-200']
        df['Price_Range'] = pd.cut(df['Price'], bins=bins, labels=labels, right=False)
        
        price_range_counts = df['Price_Range'].value_counts()
        total_count = price_range_counts.sum()
        proportions = (price_range_counts / total_count * 100).round(2)
        return proportions.to_dict()
    except Exception as e:
        print(f"计算价格区间分布失败: {e}")
        return {}

def calculate_sales_volume_distribution(df: pd.DataFrame) -> Dict[str, float]:
    """计算不同销售量区间的分布比例"""
    try:
        # 创建销售量区间
        bins = [0, 50, 100, 150, 200, 300]
        labels = ['0-50', '51-100', '101-150', '151-200', '201-300']
        df['Sales_Range'] = pd.cut(df['Sales'], bins=bins, labels=labels, right=False)
        
        sales_range_counts = df['Sales_Range'].value_counts()
        total_count = sales_range_counts.sum()
        proportions = (sales_range_counts / total_count * 100).round(2)
        return proportions.to_dict()
    except Exception as e:
        print(f"计算销售量区间分布失败: {e}")
        return {}

def analyze_data(file_path: str) -> Dict[str, Any]:
    """分析数据并返回适合饼图展示的结果"""
    df = load_data(file_path)
    
    results = {
        "category_sales_proportion": calculate_category_sales_proportion(df),
        "top_items_revenue_proportion": calculate_item_sales_proportion(df),
        "monthly_sales_proportion": calculate_monthly_sales_proportion(df),
        "price_range_distribution": calculate_price_range_distribution(df),
        "sales_volume_distribution": calculate_sales_volume_distribution(df)
    }
    
    return results

def save_results(results: Dict[str, Any], output_file: str = 'pie_chart_analysis_results.json') -> None:
    """将分析结果保存为JSON文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"分析结果已保存到 {output_file}")
    except Exception as e:
        print(f"保存结果失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    results = analyze_data(file_path)
    save_results(results)

if __name__ == "__main__":
    main()