import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)

# Define clothing categories and items
clothing_categories = {
    'Outerwear': ['Winter Coat', 'Light Jacket', 'Raincoat', 'Parka'],
    'Tops': ['T-Shirt', 'Blouse', 'Sweater', 'Hoodie'],
    'Bottoms': ['Jeans', 'Shorts', 'Skirt', 'Dress Pants'],
    'Dresses': ['Summer Dress', 'Evening Gown', 'Casual Dress', 'Formal Dress'],
    'Accessories': ['Scarf', 'Hat', 'Gloves', 'Sunglasses']
}

# Define base prices for each item
base_prices = {
    'Winter Coat': 120, 'Light Jacket': 80, 'Raincoat': 65, 'Parka': 150,
    'T-Shirt': 25, 'Blouse': 45, 'Sweater': 60, 'Hoodie': 55,
    'Jeans': 70, 'Shorts': 35, 'Skirt': 50, 'Dress Pants': 65,
    'Summer Dress': 75, 'Evening Gown': 200, 'Casual Dress': 60, 'Formal Dress': 150,
    'Scarf': 30, 'Hat': 25, 'Gloves': 20, 'Sunglasses': 40
}

# Define seasonal factors (multipliers) for each category by month
# Higher values mean higher sales in that month
seasonal_factors = {
    'Outerwear': [1.5, 1.3, 1.0, 0.7, 0.4, 0.3, 0.3, 0.5, 0.8, 1.2, 1.5, 1.7],  # Higher in winter
    'Tops': [0.8, 0.9, 1.0, 1.1, 1.3, 1.5, 1.5, 1.3, 1.1, 0.9, 0.8, 0.7],       # Higher in summer
    'Bottoms': [0.9, 0.9, 1.0, 1.1, 1.2, 1.4, 1.4, 1.2, 1.0, 0.9, 0.9, 0.8],    # Higher in summer
    'Dresses': [0.6, 0.7, 0.9, 1.1, 1.3, 1.5, 1.5, 1.3, 1.0, 0.8, 0.7, 0.6],    # Higher in summer
    'Accessories': [1.2, 1.1, 1.0, 0.9, 1.0, 1.1, 1.2, 1.1, 1.0, 1.0, 1.1, 1.3]  # Varied
}

# Define holidays and events that affect sales
holidays = {
    '2024-01-01': ('New Year', 1.3),
    '2024-02-14': ('Valentine\'s Day', 1.4),
    '2024-05-12': ('Mother\'s Day', 1.5),
    '2024-06-16': ('Father\'s Day', 1.3),
    '2024-07-04': ('Independence Day', 1.2),
    '2024-11-29': ('Black Friday', 2.0),
    '2024-12-25': ('Christmas', 1.8)
}

# Generate weekly dates for 2024
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
weekly_dates = []
current_date = start_date
while current_date <= end_date:
    weekly_dates.append(current_date)
    current_date += timedelta(days=7)

# Create data rows
data = []
for category, items in clothing_categories.items():
    for item in items:
        base_price = base_prices[item]
        # Add some price variation
        price = base_price * (1 + np.random.uniform(-0.1, 0.1))
        
        for week_idx, date in enumerate(weekly_dates):
            month_idx = date.month - 1
            seasonal_factor = seasonal_factors[category][month_idx]
            
            # Base weekly sales (random with seasonal influence)
            base_sales = int(np.random.normal(50, 15) * seasonal_factor)
            
            # Check if there's a holiday effect
            holiday_effect = 1.0
            for holiday_date, (holiday_name, effect) in holidays.items():
                holiday_date = datetime.strptime(holiday_date, '%Y-%m-%d')
                # If the holiday is within 7 days of the current week
                if abs((holiday_date - date).days) <= 7:
                    holiday_effect = effect
                    break
            
            # Calculate final sales with some randomness
            sales = int(base_sales * holiday_effect * (1 + np.random.uniform(-0.2, 0.2)))
            sales = max(5, sales)  # Ensure minimum sales
            
            # Add row to data
            data.append({
                'Category': category,
                'Item': item,
                'Price': round(price, 2),
                'Date': date.strftime('%Y-%m-%d'),
                'Week': f'Week {week_idx + 1}',
                'Month': date.strftime('%B'),
                'Sales': sales,
                'Revenue': round(price * sales, 2)
            })

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('clothing_sales_data.xlsx', index=False)
print('Created clothing_sales_data.xlsx with', len(df), 'rows of data')
