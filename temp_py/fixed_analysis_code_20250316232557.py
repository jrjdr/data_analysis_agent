import pandas as pd
import sys

def analyze_data():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("错误：请提供CSV文件路径作为命令行参数")
        print("用法：python script.py <csv_file_path>")
        return
    
    try:
        # 读取CSV文件
        file_path = sys.argv[1]
        df = pd.read_csv(file_path)
        
        # 基本统计
        print(f"数据行数: {len(df)}")
        print(f"数据列数: {len(df.columns)}")
        
        # 计算平均年龄和薪资（修复拼写错误：maen -> mean）
        avg_age = df['age'].mean()  # 修复了这里的拼写错误
        avg_salary = df['salary'].mean()
        
        print(f"平均年龄: {avg_age}")
        print(f"平均薪资: {avg_salary}")
        
        # 保存结果
        with open('analysis_results.txt', 'w') as f:
            f.write(f"数据行数: {len(df)}\n")
            f.write(f"数据列数: {len(df.columns)}\n")
            f.write(f"平均年龄: {avg_age}\n")
            f.write(f"平均薪资: {avg_salary}\n")
        
        print("分析完成，结果已保存到 analysis_results.txt")
    except FileNotFoundError:
        print(f"错误：找不到文件 '{file_path}'")
    except KeyError as e:
        print(f"错误：数据集中缺少必要的列 {e}")
    except Exception as e:
        print(f"发生错误：{e}")

if __name__ == "__main__":
    analyze_data()