import pandas as pd
import sys
from datetime import datetime

def analyze_sales_data(file_path):
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 处理缺失值
        df.fillna({'Sales': 0, 'Revenue': 0}, inplace=True)
        
        # 确保Date列为日期类型
        df['Date'] = pd.to_datetime(df['Date'])
        
        # 基础统计分析
        basic_stats = {
            'Total Sales': df['Sales'].sum(),
            'Total Revenue': df['Revenue'].sum(),
            'Average Price': df['Price'].mean(),
            'Median Sales per Week': df['Sales'].median(),
            'Number of Products': df['Item'].nunique(),
            'Number of Categories': df['Category'].nunique()
        }
        
        # 按月份分组分析
        monthly_analysis = df.groupby('Month').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        
        # 按类别分组分析
        category_analysis = df.groupby('Category').agg({
            'Sales': 'sum',
            'Revenue': 'sum',
            'Item': 'count'
        }).rename(columns={'Item': 'Product Count'}).reset_index()
        
        # 找出销售最好的产品
        best_selling = df.groupby('Item').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).sort_values('Sales', ascending=False).head(3).reset_index()
        
        # 季节性分析（简化为按月份的销售趋势）
        df['Month_Num'] = df['Date'].dt.month
        seasonal_trend = df.groupby('Month_Num').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        
        # 将结果写入文本文件
        with open('analysis_results.txt', 'w') as f:
            f.write("RETAIL SALES DATA ANALYSIS\n")
            f.write("==========================\n\n")
            
            f.write("BASIC STATISTICS\n")
            for key, value in basic_stats.items():
                f.write(f"{key}: {value:.2f}\n")
            
            f.write("\nMONTHLY SALES ANALYSIS\n")
            f.write(monthly_analysis.to_string(index=False))
            
            f.write("\n\nCATEGORY ANALYSIS\n")
            f.write(category_analysis.to_string(index=False))
            
            f.write("\n\nTOP 3 BEST SELLING PRODUCTS\n")
            f.write(best_selling.to_string(index=False))
            
            f.write("\n\nSEASONAL TRENDS (BY MONTH NUMBER)\n")
            f.write(seasonal_trend.to_string(index=False))
            
        print(f"Analysis complete. Results saved to 'analysis_results.txt'")
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <csv_file_path>")
    else:
        analyze_sales_data(sys.argv[1])