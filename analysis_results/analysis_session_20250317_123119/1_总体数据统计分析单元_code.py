import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime

def load_and_analyze_data(file_path):
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Basic descriptive statistics
        desc_stats = df.describe().to_dict()
        
        # Analyze distribution of numerical and categorical columns
        num_cols = df.select_dtypes(include=['float64', 'int64']).columns
        cat_cols = df.select_dtypes(include=['object']).columns
        
        num_dist = {col: df[col].value_counts().to_dict() for col in num_cols}
        cat_dist = {col: df[col].value_counts().to_dict() for col in cat_cols}
        
        # Generate charts
        charts = generate_charts(df)
        
        # Prepare results
        results = {
            "descriptive_stats": desc_stats,
            "numerical_distribution": num_dist,
            "categorical_distribution": cat_dist,
            "charts": charts
        }
        
        return results
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def generate_charts(df):
    charts = []
    
    # Create 'pngs' directory if it doesn't exist
    if not os.path.exists('pngs'):
        os.makedirs('pngs')
    
    # Chart 1: Signal Strength vs Signal Quality
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='signal_strength_dbm', y='signal_quality_db', hue='base_station_name')
    plt.title('Signal Strength vs Signal Quality by Base Station')
    plt.xlabel('Signal Strength (dBm)')
    plt.ylabel('Signal Quality (dB)')
    plt.legend(title='Base Station', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    chart_path = f"pngs/chart_stats_signal_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    plt.savefig(chart_path)
    plt.close()
    charts.append({"path": chart_path, "description": "Scatter plot showing the relationship between signal strength and quality for different base stations."})

    # Chart 2: Success Rate Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='success_rate', kde=True)
    plt.title('Distribution of Success Rate')
    plt.xlabel('Success Rate')
    plt.ylabel('Frequency')
    plt.text(0.7, plt.gca().get_ylim()[1]*0.9, f"Mean: {df['success_rate'].mean():.2f}\nMedian: {df['success_rate'].median():.2f}", 
             bbox=dict(facecolor='white', alpha=0.5))
    chart_path = f"pngs/chart_stats_success_rate_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    plt.savefig(chart_path)
    plt.close()
    charts.append({"path": chart_path, "description": "Histogram showing the distribution of success rates across all data points."})

    return charts

def save_results(results, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317123118.csv"
    output_file = "analysis_results.json"
    
    results = load_and_analyze_data(file_path)
    if results:
        save_results(results, output_file)
        print(f"Analysis complete. Results saved to {output_file}")