# 🛒 Flipkart Product Review Scraper 📊  

A real-time, automated data extraction pipeline that scrapes product reviews from Flipkart using Playwright and BeautifulSoup. The scraped reviews are cleaned and stored in CSV format, ready for sentiment analysis, feature comparison, or building dashboards.

---

## 📌 Project Objective

The objective is to extract **authentic customer feedback** directly from Flipkart product pages and prepare it for **data analysis**, **insight generation**, and **business intelligence**. The reviews serve as a foundation for understanding customer sentiment, preferences, and product performance.

---

## 🔧 Tech Stack

| Layer               | Tools Used                     |
|--------------------|---------------------------------|
| Web Scraping       | `BeautifulSoup`                |
| Debugging          | `HTML Snapshot` (`debug.html`)  |
| Data Storage       | `CSV` (`reviews_raw.csv`)       |
| Automation         | `Python`, `Pathlib`, `csv`      |
| Optional Add-ons   | `VADER`, `Streamlit`, `Airflow` |

---

## ⚙️ Features

✅ Extracts:
- Product name & model  
- Star rating  
- Review content  
- Page number (pagination supported)  

✅ Handles:
- Flipkart's queue system (`Retry in X sec`)  
- Dynamic review loading with Playwright  
- Structured CSV storage of reviews  

✅ Outputs:
- `data/reviews_raw.csv` — Extracted reviews  

---

## 📁 Project Structure

