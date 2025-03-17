import pandas as pd
import sys
from datetime import datetime

def analyze_sales_data(file_path):
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 检查必要的列是否存在
        required_columns = ['Category', 'Item', 'Price', 'Date', 'Week', 'Month', 'Sales', 'Revenue']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"缺少必要的列: {', '.join(missing_columns)}")
        
        # 数据预处理
        # 转换日期列为日期类型
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # 处理可能的缺失值
        df.fillna({'Sales': 0, 'Revenue': 0}, inplace=True)
        
        # 创建结果文件
        with open('analysis_results.txt', 'w') as f:
            # 基本统计信息
            f.write("=== 销售数据基本统计 ===\n\n")
            f.write(f"数据记录总数: {len(df)}\n")
            f.write(f"数据时间范围: {df['Date'].min().strftime('%Y-%m-%d')} 至 {df['Date'].max().strftime('%Y-%m-%d')}\n\n")
            
            # 销售和收入统计
            f.write("=== 销售和收入统计 ===\n\n")
            sales_stats = df['Sales'].describe()
            revenue_stats = df['Revenue'].describe()
            f.write(f"销售数量统计:\n{sales_stats.to_string()}\n\n")
            f.write(f"销售收入统计:\n{revenue_stats.to_string()}\n\n")
            f.write(f"总销售量: {df['Sales'].sum()}\n")
            f.write(f"总收入: {df['Revenue'].sum():.2f}\n\n")
            
            # 按类别分组分析
            f.write("=== 按产品类别分组分析 ===\n\n")
            category_stats = df.groupby('Category').agg({
                'Sales': ['sum', 'mean'],
                'Revenue': ['sum', 'mean']
            })
            f.write(f"{category_stats.to_string()}\n\n")
            
            # 按月份分组分析
            f.write("=== 按月份分组分析 ===\n\n")
            month_stats = df.groupby('Month').agg({
                'Sales': 'sum',
                'Revenue': 'sum'
            }).reset_index()
            
            # 定义月份顺序以便正确排序
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            month_stats['Month'] = pd.Categorical(month_stats['Month'], categories=month_order, ordered=True)
            month_stats = month_stats.sort_values('Month')
            
            f.write(f"{month_stats.to_string(index=False)}\n\n")
            
            # 按周分组分析
            f.write("=== 按周分组分析 ===\n\n")
            week_stats = df.groupby('Week').agg({
                'Sales': 'sum',
                'Revenue': 'sum'
            })
            f.write(f"{week_stats.to_string()}\n\n")
            
            # 商品表现分析
            f.write("=== 商品表现分析 ===\n\n")
            item_stats = df.groupby('Item').agg({
                'Sales': 'sum',
                'Revenue': 'sum',
                'Price': 'mean'
            }).sort_values('Revenue', ascending=False)
            f.write(f"{item_stats.to_string()}\n\n")
            
            f.write("=== 分析完成 ===\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        print(f"分析完成，结果已保存到 'analysis_results.txt'")
        return True
        
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv_file_path>")
    else:
        analyze_sales_data(sys.argv[1])