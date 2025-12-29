# Chikitsa Backend

The **Chikitsa Backend** is the server-side implementation of the Chikitsa Hospital Management System (HMS). It is built using **Flask**, **Celery**, and other modern Python libraries to provide a robust and scalable backend for managing patients, doctors, appointments, and medical records.

---

## Features

- **Authentication & Authorization**:
  - JWT-based authentication for secure access.
  - Role-based access control for Admins, Doctors, and Patients.

- **Appointment Management**:
  - Book, update, and cancel appointments.
  - Automated daily reminders for upcoming appointments.

- **Medical Records**:
  - Manage patient medical records.
  - Export medical records to email.

- **Admin Dashboard**:
  - View statistics for users, departments, and appointments.
  - Manage departments and doctors.

- **Task Scheduling**:
  - Daily appointment reminders using Celery.
  - Monthly doctor reports generation.

- **Caching**:
  - Redis-based caching for improved performance.

- **Logging**:
  - Centralized logging for debugging and monitoring.

---

## Project Structure

The backend is organized into the following modules:

- **`core/`**:
  - Contains core configurations, database models, authentication, and caching logic.
- **`services/`**:
  - Implements business logic for Admin, Doctors, Patients, and Appointments.
- **`auth/`**:
  - Handles user authentication and token management.
- **`utils/`**:
  - Utility functions for tasks like email templates, CSV exports, and background tasks.
- **`api_specification.yaml`**:
  - OpenAPI 3.0 specification for the backend APIs.

---

## Prerequisites

- **Python 3.10+**
- **Redis** (for caching and Celery task queue)
- **PostgreSQL** (or any SQLAlchemy-supported database)

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd chikitsa/backend
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the `backend` directory with the following variables:
   ```env
    SQLALCHEMY_DATABASE_URI = "sqlite:///databse.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG = True 
    TESTING = False  
    SECRET_KEY=your_secret_key_here
    FLASK_APP = app.py
    FLASK_ENV = development
    ADMIN_USERNAME = admin
    ADMIN_PASSWORD = admin123
    HOSPITAL_PHONE = +1234567890

    JWT_SECRET_KEY=your_jwt_secret_key_here
    JWT_ACCESS_TOKEN_EXPIRES=3600
    JWT_REFRESH_TOKEN_EXPIRES=86400


    # EMAIL

    MAIL_SERVER=smtp.gmail.com  
    MAIL_PORT=587
    MAIL_USERNAME=your_mail
    MAIL_PASSWORD=your_password
    MAIL_DEFAULT_SENDER=your_mail
    MAIL_DEFAULT_SENDER_NAME=Chikitsa HMS


    # REDIS
    REDIS_URL='redis://localhost:6379/0'

    # Cron timings 
    # Daily reminders 
    DAILY_REMINDER_HOUR=7
    DAILY_REMINDER_MINUTE=0

    # Monthly reports 
    MONTHLY_REPORT_DAY=1
    MONTHLY_REPORT_HOUR=7
    MONTHLY_REPORT_MINUTE=0
   ```

5. **Initialize the Database**:
   ```bash
   flask db upgrade
   ```

6. **Run the Application**:
   ```bash
   python app.py
   ```

---

## Task Scheduling with Celery

The backend uses **Celery** for background tasks like sending reminders and generating reports.

1. **Start Redis**:
   Ensure Redis is running on your system.

2. **Start the Celery Worker**:
   ```bash
   celery -A core.celery_config.celery_app worker --loglevel=info
   ```

3. **Start the Celery Beat Scheduler**:
   ```bash
   celery -A core.celery_config.celery_app beat --loglevel=info
   ```

---

## API Documentation

The backend APIs are documented using **OpenAPI 3.0**. You can find the API specification in the `api_specification.yaml` file. Use tools like **Swagger Editor** or **Postman** to explore the APIs.

---

## Key Technologies

- **Flask**: Lightweight web framework for building REST APIs.
- **SQLAlchemy**: ORM for database interactions.
- **Celery**: Task queue for background jobs.
- **Redis**: In-memory data store for caching and task queues.
- **JWT**: Secure token-based authentication.


---

