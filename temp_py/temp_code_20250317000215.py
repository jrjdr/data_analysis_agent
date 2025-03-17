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
        
        # 数据类型转换
        df['Date'] = pd.to_datetime(df['Date'])
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
        df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
        
        # 处理缺失值
        df.fillna({'Category': 'Unknown', 'Item': 'Unknown', 'Week': 'Unknown', 'Month': 'Unknown'}, inplace=True)
        
        # 计算Revenue是否正确(Price * Sales)
        df['Calculated_Revenue'] = df['Price'] * df['Sales']
        revenue_mismatch = ((df['Revenue'] - df['Calculated_Revenue']).abs() > 0.01).sum()
        
        # 开始分析
        results = []
        results.append("===== 销售数据分析报告 =====")
        results.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        results.append(f"数据记录总数: {len(df)}")
        results.append(f"数据日期范围: {df['Date'].min().strftime('%Y-%m-%d')} 至 {df['Date'].max().strftime('%Y-%m-%d')}")
        results.append("")
        
        # 基础统计
        results.append("1. 基础统计数据")
        results.append(f"总销售额: {df['Revenue'].sum():.2f}")
        results.append(f"总销售量: {df['Sales'].sum()}")
        results.append(f"平均单价: {df['Price'].mean():.2f}")
        results.append(f"Revenue不匹配记录数: {revenue_mismatch}")
        results.append("")
        
        # 按类别分析
        results.append("2. 按产品类别分析")
        category_stats = df.groupby('Category').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        for _, row in category_stats.iterrows():
            results.append(f"类别: {row['Category']}, 销售量: {row['Sales']}, 销售额: {row['Revenue']:.2f}")
        results.append("")
        
        # 按月份分析
        results.append("3. 按月份分析")
        month_stats = df.groupby('Month').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        for _, row in month_stats.iterrows():
            results.append(f"月份: {row['Month']}, 销售量: {row['Sales']}, 销售额: {row['Revenue']:.2f}")
        results.append("")
        
        # 按周分析
        results.append("4. 按周分析")
        week_stats = df.groupby('Week').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        for _, row in week_stats.iterrows():
            results.append(f"周: {row['Week']}, 销售量: {row['Sales']}, 销售额: {row['Revenue']:.2f}")
        results.append("")
        
        # 畅销商品分析
        results.append("5. 畅销商品Top 5")
        top_items = df.groupby('Item').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).sort_values('Sales', ascending=False).head(5).reset_index()
        for _, row in top_items.iterrows():
            results.append(f"商品: {row['Item']}, 销售量: {row['Sales']}, 销售额: {row['Revenue']:.2f}")
        
        # 将结果写入文件
        with open('analysis_results.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(results))
        
        print(f"分析完成，结果已保存到 analysis_results.txt")
        
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    
    analyze_sales_data(file_path)