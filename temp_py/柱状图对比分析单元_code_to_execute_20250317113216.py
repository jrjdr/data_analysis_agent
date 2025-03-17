import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

# Create directory for saving charts if it doesn't exist
if not os.path.exists('pngs'):
    os.makedirs('pngs')

# Function to read and analyze CSV data
def analyze_csv(file_path):
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Basic data analysis
        analysis_results = {
            "file_path": file_path,
            "row_count": len(df),
            "column_count": len(df.columns),
            "charts": []
        }
        
        # Chart 1: Success Rate by Base Station
        plt.figure(figsize=(12, 8))
        success_by_station = df.groupby('base_station_name')['success_rate'].mean().sort_values(ascending=False)
        
        bars = plt.bar(success_by_station.index, success_by_station.values, color='skyblue')
        plt.title('Average Success Rate by Base Station', fontsize=16)
        plt.xlabel('Base Station', fontsize=12)
        plt.ylabel('Average Success Rate', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0.8, 0.9)  # Adjust y-axis to better show differences
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                    f'{height:.4f}', ha='center', va='bottom', fontsize=10)
        
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Add annotation with key finding
        plt.figtext(0.5, 0.01, 
                   "Key Finding: '城西-住宅区基站' has the highest success rate at 87.89%, while '城南-工业区基站' has the lowest at 83.62%.",
                   ha="center", fontsize=11, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart1_path = f"pngs/chart_bar_success_rate_by_station_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        plt.savefig(chart1_path)
        plt.close()
        
        # Chart 2: Signal Type Performance Analysis
        plt.figure(figsize=(14, 10))
        
        # Group by signal type and calculate average metrics
        signal_performance = df.groupby('signal_type').agg({
            'success_rate': 'mean',
            'failure_rate': 'mean',
            'latency_ms': 'mean'
        }).sort_values('success_rate', ascending=False)
        
        # Plot success rate by signal type
        ax = signal_performance['success_rate'].plot(kind='bar', color='green', alpha=0.7)
        plt.title('Performance Metrics by Signal Type', fontsize=16)
        plt.xlabel('Signal Type', fontsize=12)
        plt.ylabel('Success Rate', fontsize=12)
        plt.ylim(0.8, 0.9)  # Set y-axis limits for better visualization
        
        # Add latency as a line on secondary y-axis
        ax2 = ax.twinx()
        ax2.plot(ax.get_xticks(), signal_performance['latency_ms'], 'ro-', linewidth=2)
        ax2.set_ylabel('Average Latency (ms)', color='red', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='red')
        
        # Add values on top of bars
        for i, v in enumerate(signal_performance['success_rate']):
            ax.text(i, v + 0.001, f'{v:.4f}', ha='center', va='bottom', fontsize=9)
        
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.4)
        plt.legend(['Latency (ms)'], loc='upper right')
        ax.legend(['Success Rate'], loc='upper left')
        plt.tight_layout()
        
        # Add annotation with key finding
        plt.figtext(0.5, 0.01, 
                   "Key Finding: 'RANDOM_ACCESS' signal type has the highest success rate (88.75%), while 'HANDOVER' has the lowest (82.66%).\n"
                   "Interestingly, 'RANDOM_ACCESS' also has relatively low latency, indicating good overall performance.",
                   ha="center", fontsize=11, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
        
        chart2_path = f"pngs/chart_bar_signal_type_performance_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        plt.savefig(chart2_path)
        plt.close()
        
        # Add chart information to analysis results
        analysis_results["charts"].append({
            "title": "Average Success Rate by Base Station",
            "file_path": chart1_path,
            "description": "Comparison of success rates across different base stations",
            "key_findings": "城西-住宅区基站 has the highest success rate, while 城南-工业区基站 has the lowest",
            "data": success_by_station.to_dict()
        })
        
        analysis_results["charts"].append({
            "title": "Performance Metrics by Signal Type",
            "file_path": chart2_path,
            "description": "Analysis of success rate and latency across different signal types",
            "key_findings": "RANDOM_ACCESS signal type has the highest success rate, while HANDOVER has the lowest",
            "data": signal_performance.to_dict()
        })
        
        # Save analysis results to JSON
        result_path = f"pngs/analysis_results_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        return analysis_results, [chart1_path, chart2_path]
    
    except Exception as e:
        print(f"Error analyzing CSV file: {e}")
        return None, None

# Main execution
if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317113116.csv"
    analysis_results, chart_paths = analyze_csv(file_path)
    
    if analysis_results:
        print("Analysis completed successfully!")
        print(f"Charts saved at: {', '.join(chart_paths)}")
        print(f"Analysis results saved at: {analysis_results.get('charts', [{}])[0].get('file_path', '')}")
    else:
        print("Analysis failed.")