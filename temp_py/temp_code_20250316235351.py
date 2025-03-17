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
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 检查必要的列是否存在
        required_columns = ["Category", "Item", "Price", "Date", "Week", "Month", "Sales", "Revenue"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"CSV文件缺少以下列: {', '.join(missing_columns)}")
        
        # 数据预处理
        # 转换日期列为日期类型
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # 处理缺失值
        df['Sales'].fillna(0, inplace=True)
        df['Revenue'].fillna(0, inplace=True)
        
        # 确保Sales和Revenue列是数值类型
        df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
        df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0)
        
        # 创建结果文件
        with open('analysis_results.txt', 'w', encoding='utf-8') as f:
            f.write("销售数据分析结果\n")
            f.write("=" * 50 + "\n\n")
            
            # 1. 基本统计信息
            f.write("1. 基本统计信息\n")
            f.write("-" * 30 + "\n")
            
            # 销售量和收入的基本统计
            sales_stats = df['Sales'].describe()
            revenue_stats = df['Revenue'].describe()
            
            f.write(f"销售量统计:\n")
            f.write(f"  总销售量: {df['Sales'].sum()}\n")
            f.write(f"  平均销售量: {sales_stats['mean']:.2f}\n")
            f.write(f"  最大销售量: {sales_stats['max']}\n")
            f.write(f"  最小销售量: {sales_stats['min']}\n")
            f.write(f"  销售量中位数: {sales_stats['50%']}\n\n")
            
            f.write(f"收入统计:\n")
            f.write(f"  总收入: {df['Revenue'].sum():.2f}\n")
            f.write(f"  平均收入: {revenue_stats['mean']:.2f}\n")
            f.write(f"  最大收入: {revenue_stats['max']:.2f}\n")
            f.write(f"  最小收入: {revenue_stats['min']:.2f}\n")
            f.write(f"  收入中位数: {revenue_stats['50%']:.2f}\n\n")
            
            # 2. 按类别分组分析
            f.write("2. 按类别分组分析\n")
            f.write("-" * 30 + "\n")
            
            category_stats = df.groupby('Category').agg({
                'Sales': 'sum',
                'Revenue': 'sum'
            }).reset_index()
            
            for _, row in category_stats.iterrows():
                f.write(f"类别: {row['Category']}\n")
                f.write(f"  总销售量: {row['Sales']}\n")
                f.write(f"  总收入: {row['Revenue']:.2f}\n\n")
            
            # 3. 按月份分组分析
            f.write("3. 按月份分组分析\n")
            f.write("-" * 30 + "\n")
            
            # 确保Month列存在且有效
            if 'Month' in df.columns and not df['Month'].isna().all():
                month_stats = df.groupby('Month').agg({
                    'Sales': 'sum',
                    'Revenue': 'sum'
                }).reset_index()
                
                # 按月份数字排序（如果Month是数字的话）
                try:
                    month_stats['Month'] = pd.to_numeric(month_stats['Month'])
                    month_stats = month_stats.sort_values('Month')
                except:
                    # 如果转换失败，保持原样
                    pass
                
                for _, row in month_stats.iterrows():
                    f.write(f"月份: {row['Month']}\n")
                    f.write(f"  总销售量: {row['Sales']}\n")
                    f.write(f"  总收入: {row['Revenue']:.2f}\n\n")
            else:
                # 如果Month列不可用，尝试从Date列提取月份
                if 'Date' in df.columns and not df['Date'].isna().all():
                    df['ExtractedMonth'] = df['Date'].dt.month
                    month_stats = df.groupby('ExtractedMonth').agg({
                        'Sales': 'sum',
                        'Revenue': 'sum'
                    }).reset_index().sort_values('ExtractedMonth')
                    
                    for _, row in month_stats.iterrows():
                        month_name = datetime(2000, int(row['ExtractedMonth']), 1).strftime('%B')
                        f.write(f"月份: {month_name} ({int(row['ExtractedMonth'])})\n")
                        f.write(f"  总销售量: {row['Sales']}\n")
                        f.write(f"  总收入: {row['Revenue']:.2f}\n\n")
                else:
                    f.write("无法进行月度分析：缺少有效的月份数据\n\n")
            
            # 4. 畅销商品分析
            f.write("4. 畅销商品分析\n")
            f.write("-" * 30 + "\n")
            
            top_items = df.groupby('Item').agg({
                'Sales': 'sum',
                'Revenue': 'sum'
            }).sort_values('Sales', ascending=False).head(5).reset_index()
            
            f.write("销量前5的商品:\n")
            for i, row in top_items.iterrows():
                f.write(f"  {i+1}. {row['Item']} - 销量: {row['Sales']}, 收入: {row['Revenue']:.2f}\n")
            
        print(f"分析完成，结果已保存到 analysis_results.txt")
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"错误: 文件 {file_path} 为空")
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"错误: 无法解析文件 {file_path}，请确保它是有效的CSV格式")
        sys.exit(1)
    except ValueError as e:
        print(f"值错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyze_sales_data(file_path)