# 🚀 python-automation

A collection of practical Python automation scripts built to eliminate repetitive tasks and improve workflow efficiency.

This repository contains small, focused utilities designed for **data preparation**, **file management**, and **process automation**.  
Each automation solves a real-world problem encountered during daily development and data workflows.

---

## 📌 About

**python-automation** is an evolving repository where I build and maintain automation tools based on personal needs and real use cases.

The goal is simple:

- Reduce manual work
- Automate repetitive processes
- Create reusable utilities
- Learn by building practical automation systems

---

## 🛠 Automations Included

### 1️⃣ Batch File Renamer

Automatically renames multiple files inside a directory using a sequential naming format.

**Features**
- Batch rename files
- Consistent naming structure
- Saves manual renaming time

---

### 2️⃣ Job Automatic Leave Form & Mail Sender *(Work in Progress)*

Automation script intended to:
- Generate leave requests automatically
- Fill required details
- Send email notifications

>Status: 🚧 Currently under development

---

### 3️⃣ Stock History Automation (2012-01-01 → Present)

Automation pipeline for collecting Nepal stock market historical price data.

**Includes:**
- Fetch price history from **NEPSE Alpha**
- Retrieve dead stock data from **ShareSansar**
- Convert JSON data into CSV format for analysis
- Utility scripts for structured data collection

---

## 📊 Data Sources

- https://nepsealpha.com/
- https://www.sharesansar.com/

---

## ⚙️ Usage Guide (ShareSansar Data Extraction)

Since ShareSansar uses protected requests, authentication tokens must be updated periodically.

### Step 1 — Get Required Tokens

1. Open: [ShareSansar](https://www.sharesansar.com/)


2. Search for any stock.
3. Open **Developer Tools → Application → Cookies**.
4. Copy:
- `XSRF-TOKEN`
- ShareSansar session token

> ⚠️ Tokens expire regularly and must be refreshed.

---

### Step 2 — Update Request Headers

Modify the script headers with updated values:

```python
'x-csrf-token': 'YOUR_UPDATED_TOKEN',
'x-requested-with': 'XMLHttpRequest',
````

---

### ✅ Alternative (Recommended Method)

1. Search for a stock on ShareSansar.
2. Scroll to **Price History**.
3. Open **Developer Tools → Network Tab**.
4. Locate the JSON fetch request.
5. Right-click → **Copy as cURL**.
6. Paste into:

```
https://curlconverter.com/
```

7. Convert to Python.
8. Copy cookies and headers into the script.

Done ✅

---

## 🎯 Goals of This Repository

* Build practical automation tools
* Improve Python scripting skills
* Create reusable workflow utilities
* Document real automation solutions

---

## 🚧 Future Automations

Planned additions:


## 🤝 Contributions

This repository is primarily for personal learning and experimentation, but suggestions and improvements are always welcome.

---

## 📜 License

MIT License — free to use and modify.

---

## ⭐ Support

If you find this repository useful, consider giving it a star!


