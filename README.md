# Chikitsa - Hospital Management System

A comprehensive **Hospital Management System (HMS)** built with modern web technologies to streamline healthcare operations. Chikitsa provides role-based access for Admins, Doctors, and Patients with features like appointment management, medical records, automated reminders, and comprehensive reporting.

The project was developed as a part of MAD-2 project submission at IIT Madras BS Program.
Plagarism check , critical evaluation and vivas were conducted by the course instructors.
Upon successful completion the project is pushed to public repository.

---

## Project Highlights

-  **Full-Stack Application** with REST API architecture
-  **Role-Based Authentication** with JWT tokens
-  **Automated Task Scheduling** using Celery
-  **Real-time Notifications** and email reminders
-  **Progressive Web App** capabilities
-  **Comprehensive API Documentation** (OpenAPI 3.0)
-  **Production-Ready** caching and optimization

---

## Features

###  For Admins
- **Dashboard Analytics**: Comprehensive statistics for users, departments, and appointments
- **User Management**: Manage doctors, patients, and system users
- **Department Management**: Create, update, and manage hospital departments
- **Report Generation**: Generate and export detailed performance reports

###  For Doctors
- **Appointment Management**: View, update, and manage patient appointments
- **Patient Records**: Access and update patient medical records
- **Monthly Reports**: Automated monthly performance reports via email
- **Schedule Management**: Manage availability and appointment slots

###  For Patients
- **Appointment Booking**: Book appointments with available doctors
- **Medical Records**: View personal medical history and records
- **Email Notifications**: Receive appointment reminders and updates
- **Profile Management**: Update personal information and preferences

###  System Features
- **JWT Authentication**: Secure token-based authentication with role-based access
- **Automated Reminders**: Daily appointment reminders via email using Celery
- **Background Tasks**: Scheduled task processing for notifications and reports
- **Redis Caching**: High-performance caching for improved response times
- **Progressive Web App**: Mobile-responsive design with offline capabilities

---

##  Architecture

**Modern Client-Server Architecture** with clear separation of concerns:

```
Chikitsa/
├── backend/                 # Flask REST API Server
│   ├── core/               # Core configurations, models & auth
│   ├── services/           # Business logic services
│   ├── auth/              # JWT authentication
│   ├── utils/             # Background tasks & utilities
│   └── api_specification.yaml
├── frontend/               # Vue.js 3 SPA
│   ├── src/
│   │   ├── components/    # Reusable Vue components
│   │   ├── views/         # Page-level components
│   │   ├── router/        # Vue Router configuration
│   │   └── store/         # Vuex state management
│   └── public/
└── documentation.pdf       # Complete project documentation
```

---

##  Technology Stack

### Backend (Flask Ecosystem)
- **Framework**: Flask with RESTful design
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Task Queue**: Celery with Redis broker
- **Email**: Flask-Mail for notifications
- **Caching**: Redis for performance optimization
- **Documentation**: OpenAPI 3.0 specification

### Frontend (Vue.js Ecosystem)
- **Framework**: Vue.js 3 with Composition API
- **State Management**: Vuex 4
- **Routing**: Vue Router 4
- **UI Framework**: Bootstrap 5 with responsive design
- **HTTP Client**: Axios with interceptors
- **Build Tool**: Vue CLI with modern JavaScript
- **PWA**: Service Workers for offline functionality

---

##  Quick Demo

### Default Credentials
```
Admin Access:
Username: admin
Password: admin123
```

### Key Endpoints
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **API Docs**: Available in `backend/api_specification.yaml`

---

##  Project Metrics

- **Frontend**: ~15 Vue components with responsive design
- **Backend**: ~20 REST API endpoints
- **Database**: 8 normalized tables with relationships
- **Background Tasks**: 2 automated Celery tasks
- **Test Coverage**: Comprehensive API testing
- **Code Quality**: Clean architecture with separation of concerns

---

##  Documentation

- **Detailed Documentation**: [documentation.pdf](documentation.pdf)
- **Backend Setup**: [backend/README.md](backend/README.md)
- **Frontend Setup**: [frontend/README.md](frontend/README.md)
- **API Reference**: [backend/api_specification.yaml](backend/api_specification.yaml)

---

## Development Workflow

### Prerequisites
- Python 3.10+
- Node.js 16+
- Redis Server
- Git

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd chikitsa

# Backend setup (see backend/README.md for details)
cd backend && python app.py

# Frontend setup (see frontend/README.md for details) 
cd frontend && npm run serve

# Optional: Celery for background tasks
redis-server
celery -A core.celery_config.celery_app worker --loglevel=info
```

---

## Learning Outcomes

This project demonstrates proficiency in:
- **Full-Stack Development** with modern frameworks
- **RESTful API Design** and implementation
- **Database Design** and ORM usage
- **Authentication & Authorization** with JWT
- **Asynchronous Task Processing** with Celery
- **State Management** in Vue.js applications
- **Progressive Web App** development
- **Production Deployment** considerations

---

## Academic Achievement

**Course**: Modern App Development - II (MAD-2)  
**Institution**: Indian Institute of Technology Madras (BS Program)  
**Final Score**: 92/100  
**Key Strengths**: Clean code architecture, comprehensive features, excellent documentation

---


##  Author

**Aaradhya Kulkarni**  
Student ID: 23f1001381  
Indian Institute of Technology Madras (BS Program)

*Developed as part of Modern App Development - II coursework*

---

## Connect

For technical details and implementation specifics, refer to the comprehensive [project documentation](documentation.pdf).