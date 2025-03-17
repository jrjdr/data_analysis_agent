import pandas as pd
import sys
from datetime import datetime

def analyze_sales_data(file_path):
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 处理缺失值
        df.fillna({'Sales': 0, 'Revenue': 0}, inplace=True)
        
        # 确保日期格式正确
        df['Date'] = pd.to_datetime(df['Date'])
        
        # 基础统计分析
        basic_stats = {
            'Total Sales': df['Sales'].sum(),
            'Total Revenue': df['Revenue'].sum(),
            'Average Price': df['Price'].mean(),
            'Median Sales per Week': df['Sales'].median(),
            'Max Weekly Sales': df['Sales'].max(),
            'Min Weekly Sales': df['Sales'].min()
        }
        
        # 按月份分组分析
        monthly_analysis = df.groupby('Month').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        
        # 按季度分析（根据月份推断季度）
        def get_quarter(month):
            month_to_num = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            month_num = month_to_num.get(month, 0)
            return (month_num - 1) // 3 + 1
        
        df['Quarter'] = df['Month'].apply(get_quarter)
        quarterly_analysis = df.groupby('Quarter').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        
        # 按类别分析
        category_analysis = df.groupby('Category').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        
        # 计算每个月的平均单价
        monthly_price = df.groupby('Month')['Price'].mean().reset_index()
        
        # 将结果写入文本文件
        with open('analysis_results.txt', 'w') as f:
            f.write("SALES DATA ANALYSIS\n")
            f.write("===================\n\n")
            
            f.write("BASIC STATISTICS\n")
            for key, value in basic_stats.items():
                f.write(f"{key}: {value:.2f}\n")
            
            f.write("\nMONTHLY ANALYSIS\n")
            f.write(monthly_analysis.to_string(index=False))
            
            f.write("\n\nQUARTERLY ANALYSIS\n")
            f.write(quarterly_analysis.to_string(index=False))
            
            f.write("\n\nCATEGORY ANALYSIS\n")
            f.write(category_analysis.to_string(index=False))
            
            f.write("\n\nMONTHLY AVERAGE PRICE\n")
            f.write(monthly_price.to_string(index=False))
            
            f.write("\n\nAnalysis completed on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        print(f"Analysis completed successfully. Results saved to 'analysis_results.txt'")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_csv_file>")
    else:
        analyze_sales_data(sys.argv[1])