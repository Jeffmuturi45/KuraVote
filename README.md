<div align="center">

# 🗳️ KuraVote

### Digital School Election System

**A secure, fast, and mobile-friendly digital voting platform built for Kenyan schools.**

![Django](https://img.shields.io/badge/Django-5.2-166534?style=flat-square&logo=django&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-166534?style=flat-square&logo=mysql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-166534?style=flat-square&logo=bootstrap&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-166534?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-eab308?style=flat-square)
![CI](https://github.com/YOUR_USERNAME/kuravote/actions/workflows/django.yml/badge.svg)

[Features](#features) •
[Screenshots](#screenshots) •
[Setup](#setup) •
[Usage](#usage) •
[Tech Stack](#tech-stack)

</div>

---

## Overview

KuraVote is a full-stack digital election management system designed
specifically for schools. It replaces manual paper ballots with a
secure, transparent, and fast digital voting experience — students
vote from their phones, admins manage everything from a PC dashboard,
and results update live as votes come in.

Built as a final year project by **Jeff Muturi W** (Adm: 43861)
under the supervision of **James Mburu**.

---

## Features

### Student Side — Mobile Friendly
- 🔐 Login with admission number — no username needed
- 🔑 Forced password change on first login
- 🗳️ 3-step ballot — browse candidates, review selections, submit all
- 📊 Live results with animated progress bars
- 🔔 Real-time notifications — election start, vote confirmation, results
- 👤 Profile page with account status and voting history
- ⏱️ Live countdown timer to election deadline

### Admin Side — PC Dashboard
- 📋 Full election management — create, activate, close elections
- 👥 Bulk student import via CSV — 10,000 students in under 5 seconds
- 🏆 Candidate management with photo upload and manifesto
- 📈 Live results dashboard — bar charts, doughnut charts, turnout stats
- 📄 Export results as PDF and Excel
- 🟢 Active users tracker — see who is online in real time
- 📢 Election announcements — broadcast messages to all students
- 🔒 Audit log — complete record of all admin actions

### Security
- Triple-layer duplicate vote prevention
  - View-level check
  - `select_for_update()` atomic transactions
  - Database `unique_together` constraint
- Bcrypt password hashing
- CSRF protection on all forms
- Rate limiting on login — 5 attempts per minute per IP
- Deactivated accounts blocked from voting at login and ballot

### Performance
- `bulk_create` for CSV imports — 3,000+ students per second
- Database indexes on all query-critical fields
- `select_related` and `prefetch_related` preventing N+1 queries
- 5-second cache on results API
- GZip middleware for compressed responses

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 |
| Database | MySQL 8.0 |
| Frontend | Bootstrap 5.3 + Font Awesome 6 |
| Charts | Chart.js 4.4 |
| Fonts | Sora + DM Sans (Google Fonts) |
| Auth | Custom `AbstractBaseUser` with admission number login |
| PDF Export | ReportLab |
| Excel Export | OpenPyXL |
| Cache | Django LocMemCache |

---

## Setup

### Prerequisites
- Python 3.11+
- MySQL 8.0+
- pip

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/Jeffmuturi45/kuravote.git
cd kuravote

# 2. Create virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment file
cp .env.example .env
# Edit .env with your database credentials

# 5. Create MySQL database
mysql -u root -p
CREATE DATABASE kuravote_db CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
exit;

# 6. Run migrations
python manage.py migrate

# 7. Create admin account
python manage.py createsuperuser

# 8. Run the server
python manage.py runserver
```

### Environment Variables

Create a `.env` file in the project root:
```env
SECRET_KEY=your-very-long-random-secret-key
DEBUG=True
DB_NAME=kuravote_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

---

## Usage

### Admin Workflow
```
1. Login at /admin-panel/ with superuser credentials
2. Upload student CSV at Students → CSV Upload
3. Create election at Elections → New Election
4. Add positions at Positions → New Position
5. Register candidates at Candidates → Register Candidate
6. Activate election — students can now vote
7. Monitor live results at Results → Live Results
8. Close election — results are final
9. Export PDF or Excel report
```

### CSV Format

The student CSV must have exactly these columns:
```csv
admission_number,first_name,last_name,email
43861,Jeff,Muturi,jeff@school.ac.ke
43862,Jane,Wanjiku,jane@school.ac.ke
```

### Student Workflow
```
1. Visit the system URL on phone or PC
2. Enter admission number — default password is admission number
3. Change password on first login
4. Select candidates for each position
5. Review selections
6. Submit all votes at once
7. View live results
```

---

## Database Schema
```
STUDENT     — admission_number, first_name, last_name, email
ELECTION    — election_name, start_date, end_date, status, announcement
POSITION    — election_id FK, position_name, max_votes
CANDIDATE   — student_id FK, position_id FK, manifesto, photo
VOTE        — student_id FK, candidate_id FK, position_id FK, election_id FK
NOTIFICATION— student_id FK, title, message, type, is_read
```

All tables are in **3rd Normal Form (3NF)**.

---

## Security Features

- **No plain text passwords** — all passwords hashed with PBKDF2
- **One vote per position** — enforced at view, transaction, and DB level
- **Deactivated accounts** — blocked at login and at ballot
- **CSRF tokens** — on every form submission
- **Staff-only admin routes** — students cannot access admin URLs
- **Audit log** — every admin action is recorded with timestamp

---

## Project Structure
```
kuravote/
├── election/
│   ├── models.py       # 6 normalized database models
│   ├── views.py        # All view logic
│   ├── urls.py         # URL routing
│   ├── forms.py        # Form validation
│   ├── admin.py        # Django admin registration
│   ├── backends.py     # Custom admission number auth
│   ├── middleware.py   # Force password change + auto-close
│   └── utils.py        # Active users + notifications helpers
├── templates/
│   ├── admin/          # PC admin dashboard templates
│   └── student/        # Mobile student templates
├── static/
│   ├── css/kuravote.css
│   └── js/kuravote.js
├── .env.example
├── requirements.txt
└── manage.py
```

---

## Acknowledgements

- Built with [Django](https://djangoproject.com)
- Charts by [Chart.js](https://chartjs.org)
- Icons by [Font Awesome](https://fontawesome.com)
- UI components by [Bootstrap](https://getbootstrap.com)

---

## License

MIT License — feel free to use, modify, and distribute.

---

<div align="center">
Made by Jeff Muturi.
<br>
<strong>KuraVote</strong> — Your voice, your choice.
</div>
