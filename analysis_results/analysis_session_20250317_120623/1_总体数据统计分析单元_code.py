import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
import os
from datetime import datetime

def analyze_base_station_data(file_path):
    """
    Analyze base station data from CSV file and generate statistics and visualizations.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        dict: Analysis results
    """
    try:
        # Create output directory for charts
        png_dir = "pngs"
        if not os.path.exists(png_dir):
            os.makedirs(png_dir)
            
        # Read the CSV file
        print(f"Reading data from {file_path}...")
        df = pd.read_csv(file_path)
        
        # Basic statistics
        results = {
            "file_info": {
                "file_path": file_path,
                "row_count": len(df),
                "column_count": len(df.columns),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "numerical_stats": {},
            "categorical_stats": {},
            "charts": []
        }
        
        # Identify numerical and categorical columns
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Calculate numerical statistics
        for col in numerical_cols:
            results["numerical_stats"][col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "25th_percentile": float(df[col].quantile(0.25)),
                "75th_percentile": float(df[col].quantile(0.75))
            }
        
        # Calculate categorical statistics
        for col in categorical_cols:
            value_counts = df[col].value_counts().to_dict()
            # Convert keys to strings for JSON serialization
            value_counts = {str(k): int(v) for k, v in value_counts.items()}
            results["categorical_stats"][col] = {
                "unique_values": len(value_counts),
                "most_common": {
                    "value": str(df[col].value_counts().index[0]),
                    "count": int(df[col].value_counts().iloc[0])
                },
                "value_counts": value_counts
            }
        
        # Generate Chart 1: Success Rate by Base Station
        plt.figure(figsize=(12, 8))
        sns.set_style("whitegrid")
        success_by_station = df.groupby('base_station_name')['success_rate'].mean().sort_values(ascending=False)
        
        ax = sns.barplot(x=success_by_station.index, y=success_by_station.values, palette="viridis")
        plt.title('Average Success Rate by Base Station', fontsize=16)
        plt.xlabel('Base Station', fontsize=14)
        plt.ylabel('Success Rate', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.ylim(min(success_by_station.values) * 0.9, 1.0)  # Start y-axis just below the minimum value
        
        # Add text annotations
        for i, v in enumerate(success_by_station.values):
            ax.text(i, v + 0.01, f'{v:.4f}', ha='center', fontsize=10)
            
        # Add a note about findings
        plt.figtext(0.5, 0.01, 
                   f"Key Finding: Success rates vary between {success_by_station.min():.4f} and {success_by_station.max():.4f} across stations.", 
                   ha="center", fontsize=12, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        chart1_path = os.path.join(png_dir, "chart_stats_success_rate_by_station.png")
        plt.tight_layout()
        plt.savefig(chart1_path)
        plt.close()
        
        results["charts"].append({
            "title": "Average Success Rate by Base Station",
            "path": chart1_path,
            "description": "Comparison of success rates across different base stations"
        })
        
        # Generate Chart 2: Performance metrics correlation heatmap
        plt.figure(figsize=(14, 10))
        performance_metrics = ['success_rate', 'signal_strength_dbm', 'signal_quality_db', 
                              'downlink_throughput_mbps', 'uplink_throughput_mbps', 
                              'latency_ms', 'packet_loss_percent']
        
        correlation_matrix = df[performance_metrics].corr()
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        cmap = sns.diverging_palette(230, 20, as_cmap=True)
        sns.heatmap(correlation_matrix, mask=mask, cmap=cmap, vmax=1, vmin=-1, center=0,
                   square=True, linewidths=.5, annot=True, fmt=".2f", cbar_kws={"shrink": .8})
        
        plt.title('Correlation Between Performance Metrics', fontsize=16)
        
        # Add a note about findings
        strongest_corr = correlation_matrix.unstack().sort_values(ascending=False)
        strongest_corr = strongest_corr[strongest_corr < 1.0].iloc[0]  # Get strongest correlation excluding self-correlations
        corr_text = f"Key Finding: Strongest correlation ({strongest_corr:.2f}) between {strongest_corr.index[0]} and {strongest_corr.index[1]}"
        
        plt.figtext(0.5, 0.01, corr_text, ha="center", fontsize=12, 
                   bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        chart2_path = os.path.join(png_dir, "chart_stats_performance_correlation.png")
        plt.tight_layout()
        plt.savefig(chart2_path)
        plt.close()
        
        results["charts"].append({
            "title": "Correlation Between Performance Metrics",
            "path": chart2_path,
            "description": "Heatmap showing correlations between key performance indicators"
        })
        
        # Generate Chart 3: Signal type distribution
        plt.figure(figsize=(12, 8))
        signal_counts = df['signal_type'].value_counts()
        
        ax = sns.barplot(x=signal_counts.index, y=signal_counts.values, palette="Set3")
        plt.title('Distribution of Signal Types', fontsize=16)
        plt.xlabel('Signal Type', fontsize=14)
        plt.ylabel('Count', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        
        # Add text annotations
        for i, v in enumerate(signal_counts.values):
            ax.text(i, v + 0.5, f'{v}', ha='center', fontsize=10)
            
        # Add a note about findings
        plt.figtext(0.5, 0.01, 
                   f"Key Finding: '{signal_counts.index[0]}' is the most common signal type with {signal_counts.iloc[0]} occurrences.", 
                   ha="center", fontsize=12, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        chart3_path = os.path.join(png_dir, "chart_stats_signal_type_distribution.png")
        plt.tight_layout()
        plt.savefig(chart3_path)
        plt.close()
        
        results["charts"].append({
            "title": "Distribution of Signal Types",
            "path": chart3_path,
            "description": "Frequency distribution of different signal types in the dataset"
        })
        
        # Save results to JSON
        json_path = "base_station_analysis_results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"Analysis complete. Results saved to {json_path}")
        print(f"Charts saved to {png_dir} directory")
        
        return results
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317120623.csv"
    analyze_base_station_data(file_path)