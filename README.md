# 
# Stocksly Documentation

## Overview

**Stocksly** allows you to easily retrieve stock data in JSON format. It provides several endpoints for accessing historical stock data, per-minute data, and data visualization charts.

## Available Endpoints

### 1. **Documentation Link**
- **URL**: [Visit Documentation](https://stocksly.onrender.com/)
- This link provides detailed API documentation for using Stocksly.

### 2. **Available Stock Names**
- **URL**: [View Available Stocks](https://stocksly.onrender.com/stocks/get_available_stocks/)
- Retrieves a list of all available stock names.

### 3. **Get Daily Data for Any Available Stock**
- **URL Format**: 
  ```
  https://stocksly.onrender.com/stocks/get_stock_daily_data/AKAM/
  ```
  - Fetches daily stock data for the past 30 days by default.
  - You can also specify custom start and end dates with the `start` and `end` parameters.

**Example URL:**
```
stocksly.onrender.com/stocks/get_stock_daily_data/AKAM/?start=2024-10-11end=2024-11-08
```

- **Code:**
```html
<a href="https://stocksly.onrender.com/stocks/get_stock_daily_data/AKAM/?start=2024-10-11&end=2024-11-08">View AKAM data from 2024-10-11 and 2024-11-08</a>
<code>https://stocksly.onrender.com/stocks/get_stock_daily_data/AKAM/?start=2024-10-11&end=2024-11-08</code>
```

- **Chart Data URL**:
```html
<a href="https://stocksly.onrender.com/stocks/get_stock_daily_data_chart/AKAM/?start=2024-10-11&end=2024-11-08">View AKAM data chart from 2024-10-11 and 2024-11-08</a>
<code>https://stocksly.onrender.com/stocks/get_stock_daily_data_chart/AKAM/?start=2024-10-11&end=2024-11-08</code>
```

- **Iframe Example:**
```html
<iframe src="https://stocksly.onrender.com/stocks/get_stock_daily_data_chart/AKAM/?start=2024-10-11&end=2024-11-08" frameborder="0" style="width: 90vw; height: 90vh;"></iframe>
```

### 4. **Get Per Minute Data for Any Available Stock**
- **URL Format**: 
  ```
  https://stocksly.onrender.com/stocks/get_stock_per_minute_data/AKAM/?start=2024-11-08%2000:00:00&end=2024-11-10%2000:00:00
  ```
  - Retrieves per-minute stock data within a specified time range.

**Example URL:**
```
https://stocksly.onrender.com/stocks/get_stock_per_minute_data/AKAM/?start=2024-11-08%2000:00:00&end=2024-11-10%2000:00:00
```

- **Code:**
```html
<a href="https://stocksly.onrender.com/stocks/get_stock_per_minute_data/AKAM/?start=2024-11-08%2000:00:00&end=2024-11-10%2000:00:00">View AKAM data from 2024-11-08 00:00:00 and 2024-11-10 00:00:00</a>
<code>https://stocksly.onrender.com/stocks/get_stock_per_minute_data/AKAM/?start=2024-11-08%2000:00:00&end=2024-11-10%2000:00:00</code>
```

- **Chart Data URL**:
```html
<a href="https://stocksly.onrender.com/stocks/get_stock_per_minute_data_chart/AKAM/?start=2024-11-08%2000:00:00&end=2024-11-10%2000:00:00">View AKAM chart from 2024-11-08 00:00:00 and 2024-11-10 00:00:00</a>
<code>https://stocksly.onrender.com/stocks/get_stock_per_minute_data/AKAM/?start=2024-11-08%2000:00:00&end=2024-11-10%2000:00:00</code>
```

- **Iframe Example:**
```html
<iframe src="https://stocksly.onrender.com/stocks/get_stock_per_minute_data_chart/AKAM/?start=2024-11-08%2000:00:00&end=2024-11-10%2000:00:00" frameborder="0" style="width: 90vw; height: 90vh;"></iframe>
```

---

**Created by**: [Ayush Khaire](https://www.linkedin.com/in/ayushkhaire)  
**Public Repository**: [AYUSHKHAIRE/stocksly](https://github.com/AYUSHKHAIRE/stocksly/)
