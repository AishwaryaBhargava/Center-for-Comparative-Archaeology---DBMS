# Center for Comparative Archaeology - Database Management System

## Overview
The Center for Comparative Archaeology website is a comprehensive database management system designed for archaeological research and resource management. Built using Python Flask, MySQL, SQLAlchemy, HTML, and CSS, this platform enables seamless access, contribution, and administration of archaeological databases.

## Features

### Guest Access
- View existing archaeological datasets
- Download datasets in Excel and CSV formats

### Registered User Access
- Submit requests to create new projects
- Contribute to existing projects by uploading Excel sheets (matching column structure)
- Access personal profile page to showcase projects and research interests

### Moderator Dashboard
- Review and approve user requests
- Manage project creation and contributions
- Monitor system activities

## Technical Requirements

### Development Stack
- **Backend**: Python 3.7+, Flask framework
- **Database**: MySQL 8.0
- **Frontend**: HTML5, CSS3, JavaScript
- **Template Engine**: Jinja2

### Dependencies
```
Flask
Flask-WTF
Flask-SQLAlchemy
Pandas
MySQL Connector for Python
Phonenumbers
Flask-Login
WTForms-Alchemy
```

### System Components

#### 1. Web Server
- Flask web framework with Werkzeug WSGI server
- Support for deployment with Gunicorn/uWSGI
- Reverse proxy setup (Nginx/Apache) recommended

#### 2. Security
- Flask-Security for authentication and authorization
- Secure password hashing
- Protection against web vulnerabilities
- Input validation implementation

#### 3. User Interface
- Responsive design for cross-device compatibility
- Dynamic content handling with JavaScript
- Cross-browser compatibility (Chrome, Firefox, Safari)

#### 4. Additional Features
- Real-time updates using Flask-SocketIO
- Email notification system
- File upload management with type verification
- Comprehensive logging system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

2. Create and activate virtual environment:
```bash
# Create virtual environment
python3 -m venv dbenv

# Activate virtual environment
# For macOS/Linux:
source dbenv/bin/activate
# For Windows:
dbenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install Flask Flask-WTF Flask-SQLAlchemy pandas mysql-connector-python phonenumbers Flask-Login wtforms-alchemy
```

4. Set environment variables:
```bash
export FLASK_ENV=development
export FLASK_APP=script.py
```

## Usage
1. Start the application:
```bash
flask run
```

2. Access the application:
```
http://127.0.0.1:5000
```

## Maintenance

### Backup and Recovery
- Regular automated MySQL database backups using mysqldump
- Implemented disaster recovery plan
- Data retention policies in place

### Documentation
- Developer documentation for setup and configuration
- In-app help system
- Knowledge base for users

## Contributors
- Aishwarya Bhargava
- Anusha Shivakumar
- Bhavana Devulapally
- Shusrita Venugopal
