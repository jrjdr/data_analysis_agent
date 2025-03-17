import pandas as pd
import sys
from datetime import datetime

def analyze_sales_data(file_path):
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 处理缺失值
        df = df.dropna()
        
        # 将Date列转换为datetime类型
        df['Date'] = pd.to_datetime(df['Date'])
        
        # 基础统计分析
        basic_stats = df[['Price', 'Sales', 'Revenue']].describe()
        
        # 按月份分组的销售统计
        monthly_sales = df.groupby('Month')[['Sales', 'Revenue']].sum().sort_values('Revenue', ascending=False)
        
        # 按类别分组的销售统计
        category_sales = df.groupby('Category')[['Sales', 'Revenue']].sum().sort_values('Revenue', ascending=False)
        
        # 计算最畅销商品
        best_selling_item = df.groupby('Item')['Sales'].sum().sort_values(ascending=False).head(1)
        
        # 计算平均每日销售额
        avg_daily_revenue = df.groupby('Date')['Revenue'].sum().mean()
        
        # 将结果写入文本文件
        with open('analysis_results.txt', 'w') as f:
            f.write("销售数据分析结果\n\n")
            f.write("1. 基础统计信息:\n")
            f.write(basic_stats.to_string())
            f.write("\n\n2. 月度销售统计:\n")
            f.write(monthly_sales.to_string())
            f.write("\n\n3. 类别销售统计:\n")
            f.write(category_sales.to_string())
            f.write("\n\n4. 最畅销商品:\n")
            f.write(best_selling_item.to_string())
            f.write(f"\n\n5. 平均每日销售额: {avg_daily_revenue:.2f}")
        
        print("分析完成，结果已保存到 analysis_results.txt")
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv_file_path>")
    else:
        analyze_sales_data(sys.argv[1])