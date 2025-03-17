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
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
        df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
        
        # 处理缺失值
        df.fillna({'Category': 'Unknown', 'Item': 'Unknown', 'Week': 'Unknown', 'Month': 'Unknown'}, inplace=True)
        
        # 处理数值列中的NaN值
        df = df.dropna(subset=['Price', 'Sales', 'Revenue'])
        
        # 处理日期列中的NaT值
        df = df.dropna(subset=['Date'])
        
        # 如果没有数据，提前返回
        if len(df) == 0:
            print("警告: 处理后没有有效数据")
            output_file = os.path.join(os.path.dirname(file_path), 'analysis_results.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("没有有效数据可供分析")
            print(f"分析完成，结果已保存到 {output_file}")
            return
        
        # 计算Revenue是否正确(Price * Sales)
        df['Calculated_Revenue'] = df['Price'] * df['Sales']
        revenue_mismatch = ((df['Revenue'] - df['Calculated_Revenue']).abs() > 0.01).sum()
        
        # 开始分析
        results = []
        results.append("===== 销售数据分析报告 =====")
        results.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        results.append(f"数据记录总数: {len(df)}")
        
        # 确保日期范围可以正确格式化
        if not df['Date'].empty:
            min_date = df['Date'].min()
            max_date = df['Date'].max()
            if pd.notna(min_date) and pd.notna(max_date):
                results.append(f"数据日期范围: {min_date.strftime('%Y-%m-%d')} 至 {max_date.strftime('%Y-%m-%d')}")
            else:
                results.append("数据日期范围: 无有效日期")
        else:
            results.append("数据日期范围: 无有效日期")
        results.append("")
        
        # 基础统计
        results.append("1. 基础统计数据")
        results.append(f"总销售额: {df['Revenue'].sum():.2f}")
        results.append(f"总销售量: {int(df['Sales'].sum())}")  # 确保销售量为整数
        
        # 避免除以零错误
        if df['Sales'].sum() > 0:
            results.append(f"平均单价: {df['Revenue'].sum() / df['Sales'].sum():.2f}")
        else:
            results.append("平均单价: N/A (无销售)")
            
        results.append(f"Revenue不匹配记录数: {revenue_mismatch}")
        results.append("")
        
        # 按类别分析
        results.append("2. 按产品类别分析")
        category_stats = df.groupby('Category').agg({
            'Sales': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        for _, row in category_stats.iterrows():
            results.append(f"类别: {row['Category']}, 销售量: {int(row['Sales'])}, 销售额: {row['Revenue']:.2f}")
        results.append("")
        
        # 按月份分析
        results.append("3. 按月份分析")
        # 确保Month列是有效的
        if 'Month' in df.columns and not df['Month'].isna().all():
            month_stats = df.groupby('Month').agg({
                'Sales': 'sum',
                'Revenue': 'sum'
            }).reset_index()
            # 尝试按月份数字排序
            try:
                month_stats['Month_num'] = pd.to_numeric(month_stats['Month'], errors='coerce')
                month_stats = month_stats.sort_values('Month_num').drop('Month_num', axis=1)
            except Exception:
                # 如果无法转换为数字，则按原始值排序
                month_stats = month_stats.sort_values('Month')
                
            for _, row in month_stats.iterrows():
                results.append(f"月份: {row['Month']}, 销售量: {int(row['Sales'])}, 销售额: {row['Revenue']:.2f}")
        else:
            results.append("月份数据不可用")
        results.append("")
        
        # 按周分析
        results.append("4. 按周分析")
        # 确保Week列是有效的
        if 'Week' in df.columns and not df['Week'].isna().all():
            week_stats = df.groupby('Week').agg({
                'Sales': 'sum',
                'Revenue': 'sum'
            }).reset_index()
            # 尝试按周数字排序
            try:
                week_stats['Week_num'] = pd.to_numeric(week_stats['Week'], errors='coerce')
                week_stats = week_stats.sort_values('Week_num').drop('Week_num', axis=1)
            except Exception:
                # 如果无法转换为数字，则按原始值排序
                week_stats = week_stats.sort_values('Week')
                
            for _, row in week_stats.iterrows():
                results.append(f"周: {row['Week']}, 销售量: {int(row['Sales'])}, 销售额: {row['Revenue']:.2f}")
        else:
            results.append("周数据不可用")
        results.append("")
        
        # 畅销商品分析
        results.append("5. 畅销商品Top 5")
        if 'Item' in df.columns and not df['Item'].isna().all():
            top_items = df.groupby('Item').agg({
                'Sales': 'sum',
                'Revenue': 'sum'
            }).sort_values('Sales', ascending=False).head(5).reset_index()
            for _, row in top_items.iterrows():
                results.append(f"商品: {row['Item']}, 销售量: {int(row['Sales'])}, 销售额: {row['Revenue']:.2f}")
        else:
            results.append("商品数据不可用")
        
        # 将结果写入文件
        output_file = os.path.join(os.path.dirname(file_path), 'analysis_results.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(results))
        
        print(f"分析完成，结果已保存到 {output_file}")
        
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        import traceback
        print(traceback.format_exc())  # 打印详细的错误堆栈
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