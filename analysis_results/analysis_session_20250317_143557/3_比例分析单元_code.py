import pandas as pd
import os

def read_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def analyze_categorical_columns(df):
    categorical_columns = df.select_dtypes(include=['object']).columns
    results = []

    for col in categorical_columns:
        value_counts = df[col].value_counts()
        total_count = len(df)
        
        result = f"\n{col} Distribution:\n"
        result += "-" * 30 + "\n"
        
        for value, count in value_counts.items():
            percentage = (count / total_count) * 100
            result += f"{value}: {count} ({percentage:.2f}%)\n"
        
        results.append(result)

    return results

def save_results(results, output_file):
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Categorical Column Distribution Analysis\n")
            f.write("=" * 40 + "\n\n")
            for result in results:
                f.write(result)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    input_file = "temp_csv/excel_data_20250317143557.csv"
    output_file = "pngs/category_distribution_results.txt"

    df = read_csv(input_file)
    if df is None:
        return

    results = analyze_categorical_columns(df)
    save_results(results, output_file)

if __name__ == "__main__":
    main()