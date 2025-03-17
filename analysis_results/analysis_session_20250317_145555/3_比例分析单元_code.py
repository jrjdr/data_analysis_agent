import pandas as pd
import os
from datetime import datetime

def read_csv_file(file_path):
    """
    Read CSV file and return a pandas DataFrame
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully read CSV file with {len(df)} rows and {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return None
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return None

def get_categorical_columns(df):
    """
    Identify categorical columns in the DataFrame
    """
    categorical_cols = []
    
    # Include object dtype columns
    categorical_cols.extend(df.select_dtypes(include=['object']).columns.tolist())
    
    # Include columns with few unique values (potential categorical variables)
    for col in df.select_dtypes(exclude=['object']).columns:
        unique_values = df[col].nunique()
        # Consider columns with <= 20 unique values as categorical
        if unique_values <= 20 and unique_values > 0:
            categorical_cols.append(col)
    
    return categorical_cols

def analyze_categorical_columns(df, categorical_cols):
    """
    Analyze the distribution of categorical columns
    """
    results = []
    
    for col in categorical_cols:
        # Get value counts and percentages
        counts = df[col].value_counts(dropna=False)
        percentages = df[col].value_counts(normalize=True, dropna=False) * 100
        
        # Combine counts and percentages
        distribution = pd.DataFrame({
            'Count': counts,
            'Percentage': percentages
        })
        
        # Sort by count in descending order
        distribution = distribution.sort_values('Count', ascending=False)
        
        # Add to results
        results.append((col, distribution))
    
    return results

def format_analysis_results(results):
    """
    Format analysis results as readable text
    """
    output = "=== SERVER DATA CATEGORY DISTRIBUTION ANALYSIS ===\n"
    output += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for col_name, distribution in results:
        output += f"=== {col_name.upper()} DISTRIBUTION ===\n"
        output += f"Total unique values: {distribution.shape[0]}\n\n"
        
        # Format each row
        for value, row in distribution.iterrows():
            # Handle NaN values properly
            value_str = "Missing/NaN" if pd.isna(value) else str(value)
            output += f"{value_str}: {row['Count']:,} ({row['Percentage']:.2f}%)\n"
        
        output += "\n" + "-" * 50 + "\n\n"
    
    return output

def save_results_to_file(results_text, output_path):
    """
    Save results to a text file
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write results to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(results_text)
        
        print(f"Results saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving results: {str(e)}")
        return False

def add_summary_statistics(df, results_text):
    """
    Add summary statistics for the dataset
    """
    summary = "\n=== DATASET SUMMARY ===\n"
    summary += f"Total rows: {len(df):,}\n"
    summary += f"Total columns: {len(df.columns):,}\n"
    
    # Count of categorical and numerical columns
    cat_cols = df.select_dtypes(include=['object']).columns
    num_cols = df.select_dtypes(exclude=['object']).columns
    summary += f"Categorical columns: {len(cat_cols):,}\n"
    summary += f"Numerical columns: {len(num_cols):,}\n\n"
    
    return results_text + summary

def main():
    # CSV file path
    file_path = "temp_csv/excel_data_20250317145554.csv"
    output_path = "pngs/category_distribution_results.txt"
    
    # Read CSV file
    df = read_csv_file(file_path)
    if df is None:
        return
    
    # Get categorical columns
    categorical_cols = get_categorical_columns(df)
    print(f"Identified {len(categorical_cols)} categorical columns: {categorical_cols}")
    
    # Analyze categorical columns
    results = analyze_categorical_columns(df, categorical_cols)
    
    # Format results
    results_text = format_analysis_results(results)
    
    # Add summary statistics
    results_text = add_summary_statistics(df, results_text)
    
    # Save results to file
    save_results_to_file(results_text, output_path)

if __name__ == "__main__":
    main()