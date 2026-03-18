# Create README
echo "# KuraVote — Digital School Election System

A secure, mobile-friendly digital election system built with Django and MySQL.

## Features
- Student login via admission number
- CSV bulk student import
- 3-step ballot with review before submission
- Live results dashboard with charts
- PDF and Excel report export
- Admin panel with full election management

## Setup
\`\`\`bash
pip install -r requirements.txt
cp .env.example .env  # fill in your DB credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
\`\`\`

## Tech Stack
- Django 5.2
- MySQL
- Bootstrap 5
- Chart.js
- Font Awesome
" > README.md

# Also create .env.example so others know what variables are needed
echo "SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=kuravote_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306" > .env.example

git add .
git commit -m "Add README and .env.example"
git push
