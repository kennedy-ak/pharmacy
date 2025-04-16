# Pharmacy Management System

This is a Django-based web application for managing pharmacy operations, including inventory, transactions, and user authentication.





## Features

- **Dashboard**: Provides an overview of pharmacy operations.
- **Inventory Management**: Manage stock levels, add new items, and track inventory.
- **Transactions**: Record and manage sales and purchases.
- **User Authentication**: Login, logout, and password management using Django's built-in authentication system.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pharmacy

2.Collecting workspace informationHere is a `README.md` file for your project:

```markdown
# Pharmacy Management System

This is a Django-based web application for managing pharmacy operations, including inventory, transactions, and user authentication.

## Project Structure

```
pharmacy/
├── db.sqlite3
├── manage.py
├── requirements.txt
├── dashboard/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── templates/
├── inventory/
│   ├── __init__.py
│   ├── admin.py
│   ├── api_view.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── templates/
├── pharmacy/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── templates/
│       ├── base_auth.html
│       ├── base.html
│       └── registration/
└── transactions/
    ├── __init__.py
    ├── admin.py
    ├── ...
```

## Features

- **Dashboard**: Provides an overview of pharmacy operations.
- **Inventory Management**: Manage stock levels, add new items, and track inventory.
- **Transactions**: Record and manage sales and purchases.
- **User Authentication**: Login, logout, and password management using Django's built-in authentication system.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pharmacy
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Access the application at `http://127.0.0.1:8000/`.

## Configuration

### Database

The project uses SQLite by default. You can configure the database in [`pharmacy/settings.py`](pharmacy/settings.py) under the `DATABASES` section.

### Static Files

Static files are served from the `static/` directory. Configure static file settings in [`pharmacy/settings.py`](pharmacy/settings.py) under the `STATIC_URL`, `STATICFILES_DIRS`, and `STATIC_ROOT` sections.

### Email

Email settings can be configured in [`pharmacy/settings.py`](pharmacy/settings.py) under the `EMAIL_BACKEND` section. Uncomment and update the email settings as needed.

## URLs

- **Dashboard**: `/dashboard/`
- **Inventory**: `/inventory/`
- **Transactions**: `/transactions/`
- **Authentication**: `/accounts/`

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
```

Similar code found with 1 license type
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate