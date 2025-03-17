import pandas as pd
import numpy as np
import os
from datetime import datetime

def analyze_server_data(file_path, output_path):
    """
    Analyze server monitoring data from CSV file and save results as text
    
    Args:
        file_path (str): Path to the CSV file
        output_path (str): Path to save the analysis results
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Read the CSV file
        print(f"Reading data from {file_path}...")
        df = pd.read_csv(file_path)
        
        # Basic data information
        total_rows = len(df)
        total_columns = len(df.columns)
        
        # Convert timestamp to datetime
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            date_range = [df['timestamp'].min(), df['timestamp'].max()]
        except:
            date_range = ["Unknown", "Unknown"]
        
        # Identify numeric and categorical columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Basic statistics for numeric columns
        numeric_stats = df[numeric_cols].describe().T
        
        # Function to format float values
        def format_float(x):
            if isinstance(x, (int, float)) and not np.isnan(x):
                return f"{x:.4f}"
            return str(x)
        
        # Analysis of missing values
        missing_values = df.isnull().sum()
        missing_percent = (missing_values / total_rows * 100).round(2)
        
        # Categorical column analysis
        categorical_analysis = {}
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            unique_values = len(value_counts)
            most_common = value_counts.index[0]
            most_common_count = value_counts.iloc[0]
            least_common = value_counts.index[-1]
            least_common_count = value_counts.iloc[-1]
            
            categorical_analysis[col] = {
                'unique_values': unique_values,
                'most_common': most_common,
                'most_common_count': most_common_count,
                'most_common_percent': round(most_common_count / total_rows * 100, 2),
                'least_common': least_common,
                'least_common_count': least_common_count,
                'least_common_percent': round(least_common_count / total_rows * 100, 2)
            }
        
        # Time series analysis (if timestamp is present)
        time_analysis = {}
        if 'timestamp' in df.columns and pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            # Count events by day
            time_analysis['events_by_day'] = df.groupby(df['timestamp'].dt.date).size()
            
            # Check for patterns by hour
            time_analysis['events_by_hour'] = df.groupby(df['timestamp'].dt.hour).size()

        # Event type analysis
        event_analysis = {}
        if 'event_type' in df.columns:
            event_analysis = df['event_type'].value_counts().to_dict()
        
        # Server performance analysis
        # Find the top 5 metrics with highest average utilization
        if 'server_id' in df.columns and len(numeric_cols) > 0:
            usage_cols = [col for col in numeric_cols if 'usage' in col or 'percent' in col]
            if usage_cols:
                high_usage_metrics = numeric_stats.loc[usage_cols].sort_values('mean', ascending=False).head(5)
            else:
                high_usage_metrics = numeric_stats.sort_values('mean', ascending=False).head(5)
                
        # Write results to text file
        with open(output_path, 'w', encoding='utf-8') as f:
            # Title
            f.write("=================================\n")
            f.write("SERVER MONITORING DATA ANALYSIS\n")
            f.write("=================================\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source File: {file_path}\n\n")
            
            # Basic information
            f.write("DATASET OVERVIEW\n")
            f.write("-----------------\n")
            f.write(f"Total Records: {total_rows}\n")
            f.write(f"Total Columns: {total_columns}\n")
            f.write(f"Date Range: {date_range[0]} to {date_range[1]}\n")
            f.write(f"Numeric Columns: {len(numeric_cols)}\n")
            f.write(f"Categorical Columns: {len(categorical_cols)}\n\n")
            
            # Missing values analysis
            f.write("MISSING VALUES ANALYSIS\n")
            f.write("----------------------\n")
            for col, count in missing_values.items():
                if count > 0:
                    f.write(f"{col}: {count} missing values ({missing_percent[col]}%)\n")
            f.write("\n")
            
            # Categorical column analysis
            f.write("CATEGORICAL VARIABLES ANALYSIS\n")
            f.write("-----------------------------\n")
            for col, stats in categorical_analysis.items():
                f.write(f"{col}:\n")
                f.write(f"  Unique Values: {stats['unique_values']}\n")
                f.write(f"  Most Common: '{stats['most_common']}' ({stats['most_common_count']} occurrences, {stats['most_common_percent']}%)\n")
                f.write(f"  Least Common: '{stats['least_common']}' ({stats['least_common_count']} occurrences, {stats['least_common_percent']}%)\n\n")
            
            # Event type analysis
            if event_analysis:
                f.write("EVENT TYPE ANALYSIS\n")
                f.write("------------------\n")
                for event_type, count in event_analysis.items():
                    f.write(f"{event_type}: {count} ({round(count/total_rows*100, 2)}%)\n")
                f.write("\n")
            
            # Server performance analysis
            f.write("SERVER PERFORMANCE METRICS\n")
            f.write("-------------------------\n")
            f.write("Top 5 Metrics with Highest Average Values:\n")
            for idx, (metric, row) in enumerate(high_usage_metrics.iterrows(), 1):
                f.write(f"{idx}. {metric}:\n")
                f.write(f"   Mean: {format_float(row['mean'])}\n")
                f.write(f"   Min: {format_float(row['min'])}\n")
                f.write(f"   Max: {format_float(row['max'])}\n")
                f.write(f"   Std Dev: {format_float(row['std'])}\n\n")
            
            # Numeric column statistics
            f.write("NUMERIC COLUMN STATISTICS\n")
            f.write("------------------------\n")
            for col in numeric_cols:
                if col in numeric_stats.index:
                    f.write(f"{col}:\n")
                    f.write(f"  Count: {int(numeric_stats.loc[col, 'count'])}\n")
                    f.write(f"  Mean: {format_float(numeric_stats.loc[col, 'mean'])}\n")
                    f.write(f"  Std Dev: {format_float(numeric_stats.loc[col, 'std'])}\n")
                    f.write(f"  Min: {format_float(numeric_stats.loc[col, 'min'])}\n")
                    f.write(f"  25%: {format_float(numeric_stats.loc[col, '25%'])}\n")
                    f.write(f"  50% (Median): {format_float(numeric_stats.loc[col, '50%'])}\n")
                    f.write(f"  75%: {format_float(numeric_stats.loc[col, '75%'])}\n")
                    f.write(f"  Max: {format_float(numeric_stats.loc[col, 'max'])}\n\n")
            
            # Time analysis
            if time_analysis and 'events_by_hour' in time_analysis:
                f.write("TIME DISTRIBUTION ANALYSIS\n")
                f.write("--------------------------\n")
                
                f.write("Events by Hour of Day:\n")
                for hour, count in time_analysis['events_by_hour'].items():
                    f.write(f"  Hour {hour}: {count} events ({round(count/total_rows*100, 2)}%)\n")
                f.write("\n")
                
            f.write("=================================\n")
            f.write("END OF ANALYSIS\n")
            f.write("=================================\n")
            
        print(f"Analysis completed. Results saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error occurred during analysis: {str(e)}")
        return False

if __name__ == "__main__":
    # File paths
    csv_file = "temp_csv/excel_data_20250317145554.csv"
    output_file = "pngs/analysis_results.txt"
    
    # Run the analysis
    analyze_server_data(csv_file, output_file)