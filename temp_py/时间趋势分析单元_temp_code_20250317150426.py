import pandas as pd
import numpy as np
import os
from datetime import datetime
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose

def load_and_prepare_data(file_path):
    """Load CSV file and prepare the data for analysis."""
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Convert timestamp to datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Set timestamp as index
        df.set_index('timestamp', inplace=True)
        
        # Fill missing values with method that preserves time-dependent patterns
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            if df[col].isna().any():
                # Use ffill() and bfill() instead of deprecated fillna(method='ffill')
                df[col] = df[col].ffill().bfill()
        
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None

def analyze_time_trends(df):
    """Analyze overall trends in the time series data."""
    results = {}
    
    # Separate server and database records
    server_df = df[df['resource_type'] == 'server']
    db_df = df[df['resource_type'] == 'database']
    
    # Identify numeric columns only for resampling
    numeric_columns = server_df.select_dtypes(include=['float64', 'int64']).columns
    
    # Analyze daily and hourly patterns - only use numeric columns
    server_df_daily = server_df[numeric_columns].resample('D').mean()
    server_df_hourly = server_df[numeric_columns].resample('H').mean()
    
    # Get key metrics - ensure they exist and are numeric
    metrics = ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 
               'network_traffic_percent', 'temperature_celsius']
    available_metrics = [m for m in metrics if m in numeric_columns]
    
    # Calculate trends for server metrics
    for metric in available_metrics:
        if not server_df_daily[metric].isna().all():
            # Calculate trend using simple linear regression
            x = np.arange(len(server_df_daily))
            y = server_df_daily[metric].values
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            trend_direction = "increasing" if slope > 0 else "decreasing"
            trend_strength = abs(r_value)
            
            results[metric] = {
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'slope': slope,
                'p_value': p_value
            }
    
    return results

def detect_anomalies(df):
    """Detect anomalies in the time series data using Z-score method."""
    anomalies = {}
    
    # Key metrics to check for anomalies
    metrics = ['cpu_usage_percent', 'memory_usage_percent', 'disk_io_percent',
               'network_traffic_percent', 'avg_query_time_ms', 'temperature_celsius']
    
    # Only process numeric columns that exist and have data
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    available_metrics = [m for m in metrics if m in numeric_columns and not df[m].isna().all()]
    
    for metric in available_metrics:
        # Calculate Z-scores
        z_scores = np.abs(stats.zscore(df[metric].fillna(df[metric].median())))
        
        # Find anomalies (Z-score > 3)
        anomaly_indices = np.where(z_scores > 3)[0]
        
        if len(anomaly_indices) > 0:
            # Get timestamps of anomalies
            anomaly_times = df.index[anomaly_indices].tolist()
            anomaly_values = df[metric].iloc[anomaly_indices].tolist()
            
            # Store up to 10 anomalies
            anomalies[metric] = list(zip(
                [t.strftime('%Y-%m-%d %H:%M:%S') for t in anomaly_times[:10]], 
                anomaly_values[:10]
            ))
    
    return anomalies

def analyze_periodicity(df):
    """Analyze periodicity in the time series data."""
    results = {}
    
    # Select metrics to analyze
    metrics = ['cpu_usage_percent', 'memory_usage_percent', 'disk_io_percent',
               'network_traffic_percent', 'query_rate_per_sec']
    
    # Only process numeric columns that exist and have enough data
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    available_metrics = [m for m in metrics if m in numeric_columns and not df[m].isna().all() and len(df) > 24]
    
    for metric in available_metrics:
        try:
            # Resample to hourly data to reduce noise
            hourly_data = df[metric].resample('H').mean()
            
            # Only decompose if we have enough data points (at least 2 periods)
            if len(hourly_data) >= 48:  # At least 2 days worth of hourly data
                # Perform seasonal decomposition
                decomposition = seasonal_decompose(hourly_data, model='additive', period=24)
                
                # Calculate strength of seasonality
                seasonal_strength = np.std(decomposition.seasonal) / np.std(hourly_data)
                
                results[metric] = {
                    'has_daily_pattern': seasonal_strength > 0.1,
                    'seasonal_strength': seasonal_strength
                }
            else:
                results[metric] = {
                    'has_daily_pattern': 'Insufficient data',
                    'seasonal_strength': 'Insufficient data'
                }
                
        except Exception as e:
            results[metric] = {
                'has_daily_pattern': f'Error: {str(e)}',
                'seasonal_strength': 'N/A'
            }
    
    return results

def analyze_correlations(df):
    """Analyze correlations between different metrics."""
    # Check if we have server metrics
    server_metrics = ['cpu_usage_percent', 'memory_usage_percent', 'disk_io_percent',
                     'network_traffic_percent', 'temperature_celsius']
    
    # Filter to numeric metrics that exist in the dataframe
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    available_metrics = [m for m in server_metrics if m in numeric_columns and not df[m].isna().all()]
    
    if len(available_metrics) > 1:
        # Calculate correlation matrix
        corr_matrix = df[available_metrics].corr()
        
        # Find strong correlations (absolute value > 0.7)
        strong_corr = []
        for i in range(len(available_metrics)):
            for j in range(i+1, len(available_metrics)):
                metric1 = available_metrics[i]
                metric2 = available_metrics[j]
                corr_value = corr_matrix.loc[metric1, metric2]
                
                if abs(corr_value) > 0.7:
                    relationship = "positive" if corr_value > 0 else "negative"
                    strong_corr.append((metric1, metric2, corr_value, relationship))
        
        return strong_corr
    else:
        return []

def format_results_for_text(trend_results, anomaly_results, periodicity_results, correlation_results, df):
    """Format the analysis results as readable text."""
    text_output = "=== SERVER METRICS TIME TREND ANALYSIS ===\n"
    text_output += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text_output += f"Data Period: {df.index.min().strftime('%Y-%m-%d %H:%M:%S')} to {df.index.max().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text_output += f"Total Records: {len(df)}\n\n"
    
    # 1. Trend Analysis
    text_output += "--- TREND ANALYSIS ---\n"
    for metric, result in trend_results.items():
        text_output += f"\n{metric.upper()}:\n"
        text_output += f"  Direction: {result['trend_direction']}\n"
        text_output += f"  Strength (R-value): {result['trend_strength']:.4f}\n"
        text_output += f"  Slope: {result['slope']:.6f} per day\n"
        text_output += f"  Statistical Significance: {'Significant' if result['p_value'] < 0.05 else 'Not significant'}\n"
    
    # 2. Periodicity Analysis
    text_output += "\n\n--- PERIODICITY ANALYSIS ---\n"
    for metric, result in periodicity_results.items():
        text_output += f"\n{metric.upper()}:\n"
        
        if isinstance(result['has_daily_pattern'], bool):
            text_output += f"  Daily Pattern: {'Present' if result['has_daily_pattern'] else 'Not detected'}\n"
            text_output += f"  Seasonal Strength: {result['seasonal_strength']:.4f}\n"
        else:
            text_output += f"  Daily Pattern: {result['has_daily_pattern']}\n"
            text_output += f"  Seasonal Strength: {result['seasonal_strength']}\n"
    
    # 3. Anomaly Detection
    text_output += "\n\n--- ANOMALY DETECTION ---\n"
    if anomaly_results:
        for metric, anomalies in anomaly_results.items():
            if anomalies:
                text_output += f"\n{metric.upper()} Anomalies:\n"
                for timestamp, value in anomalies:
                    text_output += f"  {timestamp}: {value:.2f}\n"
            else:
                text_output += f"\n{metric.upper()}: No significant anomalies detected\n"
    else:
        text_output += "No significant anomalies detected in the dataset\n"
    
    # 4. Correlation Analysis
    text_output += "\n\n--- CORRELATION ANALYSIS ---\n"
    if correlation_results:
        for metric1, metric2, corr_value, relationship in correlation_results:
            text_output += f"\n{metric1} and {metric2}:\n"
            text_output += f"  Correlation: {corr_value:.4f} ({relationship} correlation)\n"
            text_output += f"  Interpretation: {'Strong' if abs(corr_value) > 0.8 else 'Moderate'} {relationship} relationship\n"
    else:
        text_output += "No strong correlations detected between the metrics\n"
    
    # 5. Summary
    text_output += "\n\n--- SUMMARY ---\n"
    # Find metrics with strongest trends
    if trend_results:
        strongest_trend = max(trend_results.items(), key=lambda x: abs(x[1]['trend_strength']))
        text_output += f"Strongest Trend: {strongest_trend[0]} ({strongest_trend[1]['trend_direction']})\n"
    
    # Count anomalies
    total_anomalies = sum(len(anomalies) for anomalies in anomaly_results.values())
    text_output += f"Total Anomalies Detected: {total_anomalies}\n"
    
    return text_output

def main(file_path, output_path):
    """Main function to perform the analysis and save results."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Load and prepare data
    df = load_and_prepare_data(file_path)
    if df is None:
        with open(output_path, 'w') as f:
            f.write("Error: Could not load or process the CSV file.")
        return
    
    # Perform analyses
    trend_results = analyze_time_trends(df)
    anomaly_results = detect_anomalies(df)
    periodicity_results = analyze_periodicity(df)
    correlation_results = analyze_correlations(df)
    
    # Format results as text
    text_output = format_results_for_text(
        trend_results, anomaly_results, periodicity_results, correlation_results, df
    )
    
    # Save to file
    try:
        with open(output_path, 'w') as f:
            f.write(text_output)
        print(f"Analysis results saved to {output_path}")
    except Exception as e:
        print(f"Error saving results: {str(e)}")

if __name__ == "__main__":
    csv_file_path = "temp_csv/excel_data_20250317145554.csv"
    output_file_path = "pngs/time_trend_results.txt"
    main(csv_file_path, output_file_path)