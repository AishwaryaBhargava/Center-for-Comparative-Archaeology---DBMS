Center for Comparative Archaeology - Database Management System
In the realm of archaeological research and resource management, the "Center for Comparative Archaeology" website stands as a pivotal platform designed to facilitate seamless access, contribution, and administration of databases pertinent to the archaeological domain. This user-friendly website offers a simple yet effective way for users to download existing databases and actively contribute to their growth.
This project is aimed at creating an accessible and user-friendly hub for managing, contributing to, and disseminating archaeological databases. Built using Python Flask, MySQL, SQLAlchemy, HTML, and CSS, this system enables users to view, download, contribute to existing datasets, and request new project creation after registering and logging in.

Features
Guest Access: View and download existing archaeological datasets in Excel and CSV formats.

Registered User Access: Submit requests to create new projects.
Contribute to existing projects by uploading Excel sheets with the same columns as the existing dataset.
Profile page to showcase previous projects and research interests.

Moderator Dashboard: Review and approve requests submitted by registered users (create new projects, contribute to existing ones).

Dependencies:
Ensure the following dependencies are installed in a virtual environment:
Flask
Flask-WTF
Flask-SQLAlchemy
Pandas
MySQL Connector for Python
Phonenumbers
Flask-Login
WTForms-Alchemy

Installation Steps:
Clone the repository: git clone https://github.com/yourusername/your-repo.git
Navigate to the project directory: cd your-repo
Create a virtual environment: python3 -m venv dbenv
Activate the virtual environment:
On macOS/Linux: source dbenv/bin/activate
On Windows: dbenv\Scripts\activate
Install dependencies:
Copy code
pip install Flask Flask-WTF Flask-SQLAlchemy pandas mysql-connector-python phonenumbers Flask-Login wtforms-alchemy
Set Flask environment variables:
arduino
Copy code
export FLASK_ENV=development
export FLASK_APP=script.py
Usage
Run the application: flask run
Access the application in your browser: http://127.0.0.1:5000

SYSTEM REQUIREMENTS
1. Web Server:
a. Flask web framework for Python, utilizing Werkzeug as the WSGI server.
b. Deployment on a web server capable of handling Flask applications (e.g., Gunicorn,
uWSGI).
c. Consideration for reverse proxy setup (e.g., Nginx, Apache) to enhance security and
performance.

2. Database Management System:
a. MySQL 8.0 for efficient data storage and retrieval.
b. Flask-SQLAlchemy for simplified database interactions within the Flask application.
c. Proper database schema design to accommodate user profiles, notifications,
contributions, and moderation logs.

3. Programming Languages:
a. Python 3.7 or later for server-side scripting using Flask.
b. HTML5, CSS3, and JavaScript for the front-end user interface.
c. Jinja2 templating engine for seamless integration of Python with HTML templates.

4. User Authentication and Security:
a. Flask-Security for user authentication and authorization.
b. Implementation of secure password hashing using libraries like Werkzeug.
c. Protection against common web vulnerabilities using Flask extensions and proper
input validation.

5. User Interface Compatibility:
a. Responsive design using HTML5 and CSS3 for optimal user experience across
devices.
b. JavaScript for client-side interactivity and dynamic content.

6. Notification System:
a. Implementation of real-time updates using Flask-SocketIO for WebSocket
functionality.
b. Integration with Flask-Mail or similar extensions for email notifications.

7. User Management:
a. Flask-Login for user session management.
b. User registration and profile management using Flask forms.
c. Account deletion functionality with appropriate data retention policies.

8. Moderation Tools:
a. Flask admin panel or custom moderation interfaces for reviewing and processing user
submissions.
b. Logging of moderator activities within the Flask application.

9. File Management:
a. Flask-Uploads or similar extensions for secure file upload and management.
b. File type verification to ensure the integrity of contributed content.

10. Compatibility Testing:
a. Cross-browser compatibility testing for major browsers (Chrome, Firefox, Safari).
b. Responsive design testing on various devices and screen resolutions.

11. Documentation and Help System:
a. Comprehensive documentation for developers on setting up, configuring, and
maintaining the Flask application.
b. Implementation of a help system within the web interface or a separate knowledge
base.

12. Backup and Recovery:
a. Regular automated backups of the MySQL database using tools like mysqldump.
b. A well-defined disaster recovery plan for minimal data loss and downtime.

Contributors: 
Aishwarya Bhargava, Anusha Shivakumar,  Bhavana Devulapally, Shusrita Venugopal.