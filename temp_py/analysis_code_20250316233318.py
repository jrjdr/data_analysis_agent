import pandas as pd
import sys
import os
from datetime import datetime

def analyze_sales_data(file_path):
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 处理缺失值
        df.fillna({'Sales': 0, 'Revenue': 0}, inplace=True)
        missing_values = df.isnull().sum()
        
        # 确保Date列为日期类型
        df['Date'] = pd.to_datetime(df['Date'])
        
        # 基础统计分析
        basic_stats = df[['Price', 'Sales', 'Revenue']].describe()
        
        # 按类别分组统计
        category_stats = df.groupby('Category')[['Sales', 'Revenue']].agg(['sum', 'mean'])
        
        # 按月份分组统计
        monthly_stats = df.groupby('Month')[['Sales', 'Revenue']].sum()
        # 确保月份按正确顺序排列
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_stats = monthly_stats.reindex(month_order)
        
        # 计算畅销商品
        top_items = df.groupby('Item')[['Sales', 'Revenue']].sum().sort_values('Revenue', ascending=False).head(5)
        
        # 计算季节性趋势（按月）
        seasonal_trend = df.groupby('Month')['Sales'].sum()
        seasonal_trend = seasonal_trend.reindex(month_order)
        
        # 计算平均单价
        avg_price_by_category = df.groupby('Category')['Price'].mean()
        
        # 将结果写入文本文件
        with open('analysis_results.txt', 'w') as f:
            f.write("===== 销售数据分析报告 =====\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"数据文件: {os.path.basename(file_path)}\n\n")
            
            f.write("1. 数据概览\n")
            f.write(f"记录总数: {len(df)}\n")
            f.write(f"商品类别数: {df['Category'].nunique()}\n")
            f.write(f"商品数量: {df['Item'].nunique()}\n")
            f.write(f"缺失值统计:\n{missing_values}\n\n")
            
            f.write("2. 基础统计分析\n")
            f.write(f"{basic_stats}\n\n")
            
            f.write("3. 类别销售统计\n")
            f.write(f"{category_stats}\n\n")
            
            f.write("4. 月度销售统计\n")
            f.write(f"{monthly_stats}\n\n")
            
            f.write("5. 畅销商品 (Top 5)\n")
            f.write(f"{top_items}\n\n")
            
            f.write("6. 季节性趋势 (按月销量)\n")
            f.write(f"{seasonal_trend}\n\n")
            
            f.write("7. 类别平均单价\n")
            f.write(f"{avg_price_by_category}\n\n")
            
            f.write("===== 分析结束 =====\n")
        
        print(f"分析完成，结果已保存至 'analysis_results.txt'")
        return True
        
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在")
        return False
    except pd.errors.EmptyDataError:
        print(f"错误: 文件 '{file_path}' 为空或格式不正确")
        return False
    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv文件路径>")
    else:
        analyze_sales_data(sys.argv[1])