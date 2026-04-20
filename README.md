# 🚀 python-automation

A collection of practical Python automation scripts built to eliminate repetitive tasks. This repository houses various standalone automation tools and specialized sub-projects.

---

## 🛠 Included Features & Projects

### 1️⃣ Stock Market Automation Hub (`/stock-scrapper`)

This is a full-scale sub-project built with **FastAPI**. It provides a unified API to extract data from various Nepal Stock Market sources.

**Architecture Insight:**
The scraper is built using a **Modular Hybrid Design**:

- **API-based (`shareshansar`):** High-speed extraction using direct JSON endpoints.
- **Selenium-based (`merolagani`):** Handles websites requiring browser interaction; includes auto-blocking for notification popups.
- **Stealth-based (`nepsealpha`):** Uses `undetected-chromedriver` to bypass advanced bot detection for financial data.
- **Separation of Concerns:** `views.py` handles the API routes, while `utils.py` handles data formatting (CSV/JSON), keeping the scraper engines clean.

**Capabilities:**

- Single Stock Lookup (Get dividends, announcements, BV, or EPS instantly).
- Bulk Processing (Upload a JSON mapping file to scrape the entire market).
- Format Export (Download results directly as CSV or JSON).

---

### 2️⃣ Batch File Renamer

A utility to manage large directories by renaming multiple files using sequential or formatted naming conventions.

- Consistent structure for data logs.
- Prevents manual naming errors.

---

### 3️⃣ Job Automatic Leave Form *(WIP)*

An automation script intended to generate leave requests and send them via mail automatically.

- Status: 🚧 Under Development.
