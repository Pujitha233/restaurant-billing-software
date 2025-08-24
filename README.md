# 🍽️ Restaurant Billing Software  

## 📌 Overview  
The **Restaurant Billing Software** is a Python-based billing and sales management system that simplifies restaurant operations.  
It allows generating **itemized bills** for dine-in/takeaway orders, applies **GST & discounts**, supports **multiple payment modes**,  
and stores all transactions in a database for future reference.  

The system also provides **sales reports (daily, weekly, monthly)** and insights such as **most sold items**.  

---

## 🚀 Features  
- 📂 **Menu Management**: Upload and store menu items (with price & GST).  
- 🛒 **Order Handling**: Add/remove items, update quantities.  
- 💰 **Billing System**: Auto-calculate subtotal, GST, discounts, and total.  
- 💳 **Payment Options**: Cash, Card, UPI supported.  
- 🧾 **Bill Generation**: Itemized bill displayed and stored in DB.  
- 📊 **Sales Reports**: Export reports to CSV/JSON (daily/weekly/monthly).  
- 🔍 **Insights**: Identify most sold items.  

---

## 🛠️ Tools & Technologies  
- **Language**: Python  
- **Framework**: Streamlit (User Interface)  
- **Database**: SQLite  
- **Libraries**: `pandas`, `streamlit`, `sqlite3`, `datetime`, `json`, `csv`  
- **IDE**: VS Code / PyCharm  

---

## 📂 Project Structure  
restaurant_billing/
├── app.py # Main entry point
├── db/
│ └── restaurant.db # SQLite database
├── data/
│ ├── menu.csv # Sample menu file
│ ├── sample_bills.json # Example bills
│ └── sales_report.csv # Example sales report
├── ui/
│ └── main_ui.py # Streamlit UI
├── utils/
│ ├── calculator.py # Billing & GST calculation
│ └── db_utils.py # Database helper functions
└── README.md
