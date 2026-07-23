# FoodExpress - Food Delivery Application

A full-stack web-based food delivery platform built with **Django**, **HTML**, **CSS**, **JavaScript**, and **SQLite**.

## Features

### Customer
- Register & Login
- Browse Restaurants & Search
- View Menu & Add to Cart
- Place Orders with Online Payment (Card, UPI, Wallet, COD)
- Live Order Tracking
- Ratings & Reviews
- Coupon discounts

### Restaurant
- Manage Profile & Menu
- Accept/Reject Orders
- Update Order Status
- View Sales Reports

### Delivery Partner
- View & Accept Assigned Orders
- Update Delivery Status
- View Earnings

### Admin
- Manage Users, Restaurants, Delivery Partners
- Manage Orders, Categories, Coupons
- View Reports & Analytics

## Setup

```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py download_images
python manage.py runserver
```

Open **http://127.0.0.1:8000/**

## Demo Accounts

| Role       | Username     | Password      |
|------------|--------------|---------------|
| Admin      | admin        | admin123      |
| Customer   | customer1    | customer123   |
| Delivery   | delivery1    | delivery123   |
| Restaurant | pizzapalace  | restaurant123 |

## Coupon Codes

- `WELCOME20` - 20% off (max ₹150)
- `FLAT50` - Flat ₹50 off on orders above ₹299

## Demo Payment Details

| Method | Demo Details |
|--------|-------------|
| **Card** | `4242 4242 4242 4242` · CVV: `123` · Expiry: `12/28` |
| **UPI** | `customer@upi` or `9876543210@paytm` |
| **Wallet** | PIN: `1234` |
| **COD** | No validation needed |

Payment is validated (client + server) before the order is confirmed.

## Order Confirmation Emails

After placing an order, a confirmation email is sent to the customer's registered email.
Emails are saved to the **`sent_emails/`** folder in the project directory (open the `.log` files to read them).

To use real SMTP email, update `EMAIL_BACKEND` in `settings.py`.

## Ratings & Reviews

After an order is **delivered**, customers can rate (1–5 stars) and write a review from the order detail page. Reviews appear on the restaurant page.

## Deploy on Render

This project is ready to deploy on [Render](https://dashboard.render.com/) with PostgreSQL.

1. Push this repo to GitHub (see below).
2. In Render, click **New +** → **Blueprint**.
3. Connect your GitHub account and select the **FoodExpress** repository.
4. Render reads `render.yaml` and creates the web service + PostgreSQL database.
5. After deploy finishes, open your app URL (e.g. `https://foodexpress.onrender.com`).

The build script runs migrations, seeds demo data, and collects static files automatically.

## GitHub

Repository: [github.com/Poonghuzhali/FoodExpress](https://github.com/Poonghuzhali/FoodExpress)
