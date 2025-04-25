# 🌊 Water Plant Billing Software

A **FastAPI-based** billing and inventory management system for water plants, designed for local installation with daily Excel backups.

---

## 🚀 Features

- **Dashboard Overview**: Total revenue, pending payments, recent invoices, and activity logs.
- **Customer Management**: Add, edit, or delete customers with real-time balance tracking.
- **Product Management**: Track water products, prices, and stock quantities.
- **Invoice Management**: Create invoices with taxes, discounts, and multi-product support.
- **Reports**: Generate revenue charts, transaction history, and export to Excel/PDF.
- **Daily Backups**: Auto-save PostgreSQL data to Excel every 24 hours.
- **Local Installation**: Runs on client machines (no cloud dependency).

---

## ⚙️ Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: (To be added) React/HTML/CSS
- **Utilities**: Pandas (Excel backups), APScheduler (cron jobs)

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL installed locally ([Download](https://www.postgresql.org/download/))

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/water-billing-software.git
   cd water-billing-software
