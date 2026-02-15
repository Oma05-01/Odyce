## Odyce Perfume Store

A Django-powered e-commerce platform for browsing, reviewing, and purchasing men's and women's perfumes.

## 🚀 Overview
Odyce is a perfume e-commerce web application that allows customers to:
- Browse men's and women's perfumes
- View detailed product pages
- Leave ratings and reviews
- Add products to wishlist
- Checkout and upload proof of payment
- Manage orders


This project solves the problem of managing a simple but structured online store with:
- Role-based product management (admin)
- Customer-linked orders
- Controlled order creation (only after payment proof)
- Generic review system using Django ContentTypes

It was built to deepen understanding of Django architecture, relational modeling, authentication, and state-driven order flows.


## 🛠 Tech Stack
- Backend: Python, Django
- Database: SQLite (default) / PostgreSQL-ready
- Frontend: HTML, CSS (custom styling)
- Authentication: Django built-in auth system
- File Handling: Django Media uploads (receipt & product images)
- Tools: PyCharm, Git


## ⚙️ Key Features

- 🧴 Separate Men’s and Women’s perfume categories
- 📝 Product detail pages with reviews
- ⭐ Star-based rating system
- 🧠 Generic review system using Django ContentTypes
- 🛒 Checkout flow with session-based order state
- 📎 Payment confirmation with receipt upload
- 💖 Wishlist functionality
- 🔐 Login-required protected views
- 🛠 Admin product management (edit/delete)
- 📦 Controlled order creation (prevents duplicate unpaid orders)

## 🧠 Architecture / Design Decisions
**Why Django?**

Django was chosen because:
- Built-in authentication system
- ORM simplifies relational modeling
- Admin panel speeds up management
- ContentTypes framework enables generic relations

## Product Structure
Instead of a single Product model, we structured:
- MenPerfume
- WomenPerfume

This allows clear category separation while maintaining shared behavior.

## Generic Review System
We implemented reviews using:

ContentType.objects.get_for_model(ModelClass)


**This allows:**

- One Review model
- Linked to multiple product types
- Dynamic object association using:
    - content_type
    - object_id

This design avoids duplicating review tables per product type.

## Order State Logic
To prevent multiple unpaid orders:
Orders are only created when proof of payment is uploaded.
Checkout stores temporary data in session.
confirm_payment view finalizes order creation.
Avoids MultipleObjectsReturned issues from duplicate pending orders.

**This ensures:**
- Clean database state
- Controlled transactional flow

## Authentication Flow
- Django’s User model handles authentication.
- Each User is linked to a Customer model via OneToOneField.
- Protected views use:
    - @login_required


**This ensures only authenticated users can**:
- Leave reviews
- Checkout
- Confirm payments
- Access dashboard areas

## 📡 Key Views / Routes
| Method | Endpoint            | Description                   |
| ------ | ------------------- | ----------------------------- |
| GET    | /women/             | List all women's perfumes     |
| GET    | /men/               | List all men's perfumes       |
| GET    | /product/<id>/      | Product detail page           |
| POST   | /product/<id>/      | Submit review                 |
| GET    | /checkout/          | Review billing info           |
| POST   | /confirm-payment/   | Upload receipt & create order |
| GET    | /wishlist/          | View saved items              |
| GET    | /edit-product/<id>/ | Admin edit page               |


## 🗄 Database Design
**Core Models**

**User (Django built-in)**
⬇
**Customer**
- OneToOneField to User
- Stores billing & coupon info

**MenPerfume / WomenPerfume**
- name
- description
- price
- image (ImageField)

**Review**
- user (ForeignKey → Customer)
- content_type (ForeignKey → ContentType)
- object_id
- rating
- comment
- created_at

**Order**
- customer (ForeignKey → Customer)
- billing details
- total
- receipt (Image/FileField)
- status
- date_created (timestamp)

## Relationships
- OneToOne: User → Customer
- ForeignKey: Customer → Order
- GenericForeignKey: Review → Product models
- Session-based temporary checkout state


## 🧪 How to Run Locally
- git clone https://github.com/Oma05-01/Odyce
- cd odyce-perfume-store
- pip install -r requirements.txt
- python manage.py migrate
- python manage.py runserver

**Then visit:**
http://127.0.0.1:8000/

## 📌 Future Improvements
- Merge product models into unified Product model with category field
- Implement proper cart system
- Integrate real payment gateway (Stripe/Paystack)
- Add admin analytics dashboard
- Convert to REST API + frontend separation
- Improve media optimization & validation

## 👤 Author
Built by Esigbone Oma
Backend-focused Django developer exploring scalable application architecture.
