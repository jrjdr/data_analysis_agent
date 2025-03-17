import pandas as pd
import numpy as np
from typing import List, Tuple

def read_csv(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return pd.DataFrame()

def calculate_correlation(df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    return df[numeric_columns].corr()

def identify_correlations(corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Tuple[str, str, float]]:
    high_corr = []
    low_corr = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) >= threshold:
                high_corr.append((col1, col2, corr_value))
            elif abs(corr_value) <= 1 - threshold:
                low_corr.append((col1, col2, corr_value))
    return high_corr, low_corr

def format_correlation_results(corr_matrix: pd.DataFrame, high_corr: List[Tuple[str, str, float]], low_corr: List[Tuple[str, str, float]]) -> str:
    result = "相关性分析结果\n" + "=" * 20 + "\n\n"
    
    result += "相关性矩阵：\n"
    result += corr_matrix.to_string() + "\n\n"
    
    result += "高度相关变量对：\n"
    for col1, col2, corr in high_corr:
        result += f"{col1} - {col2}: {corr:.4f}\n"
    result += "\n"
    
    result += "低度相关变量对：\n"
    for col1, col2, corr in low_corr:
        result += f"{col1} - {col2}: {corr:.4f}\n"
    
    return result

def save_results(results: str, output_path: str):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(results)
        print(f"Results saved to {output_path}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    input_file = "temp_csv/excel_data_20250317143557.csv"
    output_file = "pngs/correlation_results.txt"
    
    df = read_csv(input_file)
    if df.empty:
        return
    
    corr_matrix = calculate_correlation(df)
    high_corr, low_corr = identify_correlations(corr_matrix)
    results = format_correlation_results(corr_matrix, high_corr, low_corr)
    save_results(results, output_file)

if __name__ == "__main__":
    main()