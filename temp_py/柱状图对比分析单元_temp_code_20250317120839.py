import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

def analyze_csv_data(file_path):
    """
    Analyze CSV data and generate bar charts
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        print(f"Successfully read CSV file with {len(df)} rows and {len(df.columns)} columns.")
        
        # Create output directory if it doesn't exist
        output_dir = "pngs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")
        
        # Analysis results dictionary
        analysis_results = {
            "file_info": {
                "file_path": file_path,
                "row_count": len(df),
                "column_count": len(df.columns)
            },
            "charts": []
        }
        
        # Chart 1: Success rate by base station
        chart1_path = create_success_rate_by_station_chart(df, output_dir)
        analysis_results["charts"].append({
            "chart_file": chart1_path,
            "description": "Success rate comparison across different base stations",
            "statistics": df.groupby('base_station_name')['success_rate'].mean().to_dict()
        })
        
        # Chart 2: Signal type distribution
        chart2_path = create_signal_type_distribution_chart(df, output_dir)
        analysis_results["charts"].append({
            "chart_file": chart2_path,
            "description": "Signal type distribution and their frequencies",
            "statistics": df['signal_type'].value_counts().to_dict()
        })
        
        # Chart 3: Resource usage by base station
        chart3_path = create_resource_usage_chart(df, output_dir)
        analysis_results["charts"].append({
            "chart_file": chart3_path,
            "description": "Resource utilization across base stations",
            "statistics": {
                "cpu": df.groupby('base_station_name')['cpu_usage_percent'].mean().to_dict(),
                "memory": df.groupby('base_station_name')['memory_usage_percent'].mean().to_dict(),
                "resource_blocks": df.groupby('base_station_name')['resource_block_usage_percent'].mean().to_dict()
            }
        })
        
        # Save analysis results as JSON
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        json_path = f"analysis_results_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        print(f"Analysis complete. Results saved to {json_path}")
        return analysis_results
        
    except Exception as e:
        print(f"Error analyzing CSV data: {str(e)}")
        return {"error": str(e)}

def create_success_rate_by_station_chart(df, output_dir):
    """Create a bar chart showing success rate by base station"""
    try:
        # Group by base station and calculate mean success rate
        station_success = df.groupby('base_station_name')['success_rate'].mean().sort_values(ascending=False)
        
        # Create figure
        plt.figure(figsize=(12, 6))
        ax = station_success.plot(kind='bar', color='steelblue')
        
        # Add title and labels
        plt.title('Average Success Rate by Base Station', fontsize=14, fontweight='bold')
        plt.xlabel('Base Station', fontsize=12)
        plt.ylabel('Success Rate', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0.5, 1.0)  # Set y-axis to start from 0.5 for better visualization
        
        # Add text annotations
        for i, v in enumerate(station_success):
            ax.text(i, v + 0.01, f'{v:.2%}', ha='center', fontsize=10)
        
        # Add a horizontal line at the overall mean
        overall_mean = df['success_rate'].mean()
        plt.axhline(y=overall_mean, color='red', linestyle='--', 
                    label=f'Overall Mean: {overall_mean:.2%}')
        
        # Add findings annotation
        best_station = station_success.index[0]
        worst_station = station_success.index[-1]
        findings = (f"Key finding: {best_station} has the highest success rate ({station_success[0]:.2%}), "
                    f"while {worst_station} has the lowest ({station_success[-1]:.2%}).")
        plt.figtext(0.5, 0.01, findings, ha='center', fontsize=10, 
                   bbox=dict(facecolor='lightyellow', alpha=0.5))
        
        plt.legend()
        plt.tight_layout()
        
        # Save chart
        chart_path = os.path.join(output_dir, "chart_bar_success_rate_by_station.png")
        plt.savefig(chart_path, dpi=300)
        plt.close()
        print(f"Created chart: {chart_path}")
        
        return chart_path
    
    except Exception as e:
        print(f"Error creating success rate chart: {str(e)}")
        return "Error"

def create_signal_type_distribution_chart(df, output_dir):
    """Create a bar chart showing distribution of signal types"""
    try:
        # Count signal types
        signal_counts = df['signal_type'].value_counts().sort_values(ascending=False).head(10)
        
        # Create figure
        plt.figure(figsize=(12, 6))
        ax = signal_counts.plot(kind='bar', color='lightseagreen')
        
        # Add title and labels
        plt.title('Top 10 Signal Types Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Signal Type', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # Add text annotations
        for i, v in enumerate(signal_counts):
            ax.text(i, v + 5, f'{v}', ha='center', fontsize=10)
            ax.text(i, v/2, f'{v/len(df):.1%}', ha='center', fontsize=10, color='white')
        
        # Add findings annotation
        most_common = signal_counts.index[0]
        findings = (f"Key finding: '{most_common}' is the most common signal type, "
                    f"representing {signal_counts[0]/len(df):.1%} of all signals.")
        plt.figtext(0.5, 0.01, findings, ha='center', fontsize=10, 
                   bbox=dict(facecolor='lightyellow', alpha=0.5))
        
        plt.tight_layout()
        
        # Save chart
        chart_path = os.path.join(output_dir, "chart_bar_signal_type_distribution.png")
        plt.savefig(chart_path, dpi=300)
        plt.close()
        print(f"Created chart: {chart_path}")
        
        return chart_path
    
    except Exception as e:
        print(f"Error creating signal type chart: {str(e)}")
        return "Error"

def create_resource_usage_chart(df, output_dir):
    """Create a bar chart showing resource usage by base station"""
    try:
        # Group by base station and calculate mean usage metrics
        resource_usage = df.groupby('base_station_name').agg({
            'cpu_usage_percent': 'mean',
            'memory_usage_percent': 'mean',
            'resource_block_usage_percent': 'mean'
        })
        
        # Sort by CPU usage
        resource_usage = resource_usage.sort_values('cpu_usage_percent', ascending=False)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Set width of bars
        barWidth = 0.25
        
        # Set positions of bar on X axis
        r1 = np.arange(len(resource_usage))
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
        
        # Make the plot
        cpu_bars = ax.bar(r1, resource_usage['cpu_usage_percent'], width=barWidth, 
                edgecolor='grey', label='CPU Usage %', color='indianred')
        mem_bars = ax.bar(r2, resource_usage['memory_usage_percent'], width=barWidth, 
                edgecolor='grey', label='Memory Usage %', color='royalblue')
        rb_bars = ax.bar(r3, resource_usage['resource_block_usage_percent'], width=barWidth, 
                edgecolor='grey', label='Resource Block Usage %', color='mediumseagreen')
        
        # Add title and labels
        ax.set_title('Resource Utilization by Base Station', fontsize=14, fontweight='bold')
        ax.set_xlabel('Base Station', fontsize=12)
        ax.set_ylabel('Utilization (%)', fontsize=12)
        ax.set_xticks([r + barWidth for r in range(len(resource_usage))])
        ax.set_xticklabels(resource_usage.index, rotation=45, ha='right')
        
        # Create legend
        ax.legend()
        
        # Add findings annotation
        highest_cpu = resource_usage.index[0]
        findings = (f"Key finding: {highest_cpu} has the highest CPU utilization "
                    f"({resource_usage['cpu_usage_percent'].iloc[0]:.1f}%).")
        plt.figtext(0.5, 0.01, findings, ha='center', fontsize=10, 
                    bbox=dict(facecolor='lightyellow', alpha=0.5))
        
        plt.tight_layout()
        
        # Save chart
        chart_path = os.path.join(output_dir, "chart_bar_resource_usage_by_station.png")
        plt.savefig(chart_path, dpi=300)
        plt.close()
        print(f"Created chart: {chart_path}")
        
        return chart_path
    
    except Exception as e:
        print(f"Error creating resource usage chart: {str(e)}")
        return "Error"

if __name__ == "__main__":
    # File path from the provided information
    csv_file_path = "temp_csv/excel_data_20250317120623.csv"
    
    # Analyze the data
    results = analyze_csv_data(csv_file_path)