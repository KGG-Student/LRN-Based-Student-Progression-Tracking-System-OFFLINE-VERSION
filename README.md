# Integrated LRN-Based Student Progression Tracking System

A Dockerized Flask web application for tracking junior high school student progression from Grade 7 to Grade 10 using the 12-digit Learner Reference Number (LRN) as the main identifier.

The system imports LIS/SF1 Excel exports, centralizes student records, tracks cohorts across school years, monitors transfer movement, computes progression indicators, and generates formatted reports for administrative review.

## Project Scope

This system is intended for school-level use by the department head or authorized school personnel. It supports:

- Uploading and processing LIS/SF1 Excel or CSV exports
- Centralized LRN-based student record management
- Grade 7 to Grade 10 progression tracking
- Transfer-in, pending transfer-in, and transfer-out monitoring
- Learners-for-review identification
- Cohort completion, irregular completion, and repeater tracking
- Excel report generation
- Print-friendly reports for PDF saving
- Login, logout, password hashing, access control, user management, password change, and session timeout

## Limitations

The system does not:

- Connect directly to the national LIS database API
- Replace the official LIS system
- Support elementary or senior high school records
- Support online enrollment
- Provide student or parent portals
- Handle grading or attendance monitoring

It only processes uploaded LIS/SF1 files provided by authorized school personnel.

## Tech Stack

- Python 3.11
- Flask
- Gunicorn
- MySQL 8.0
- SQLite for standalone desktop mode
- Nginx
- Pandas
- OpenPyXL
- xlrd
- Bootstrap 5
- Docker Compose

## Main Features

### Authentication

- Login and logout
- Logout confirmation page
- Password hashing using Werkzeug
- Change password page
- Forgot password reset using a local recovery key in standalone mode
- Admin password reset for other users
- Admin and Viewer roles
- User activation, deactivation, and deletion
- 20-minute inactivity timeout
- Session-based route protection
- Admin-only actions for upload, edits, deletion, and user management

Default local test account:

```text
Username: admin
Password: admin123
```

Change this password from the **Change Password** page before actual use.

### LIS Data Upload

The upload module accepts `.xls`, `.xlsx`, and `.csv` exports. During import, the system:

- Detects SF1/LIS columns for LRN, name, sex, and remarks
- Validates 12-digit LRNs
- Rejects duplicate LRNs within the same uploaded file
- Warns users before continuing when rows contain missing LRN, name, sex, or invalid LRN values
- Limits uploads to 50 MB
- Checks school year and grade level metadata against the selected form values
- Stores records by school year and grade level
- Detects duplicate year/grade records
- Detects transfer-related remarks such as `T/I`, `Pending TI`, and `T/O`
- Logs student name, gender, status, and remarks changes

### Student Records

The student module provides:

- Search and filtering
- Student list by LRN, name, grade, school year, and status
- Individual student history pages
- Manual editing of record status and remarks
- Change logs for imported and manually edited values

Manual edits are traceable. The system logs old value, new value, school year, grade level, timestamp, and the admin user who made the change.

### Cohort Tracking

### Cohort Tracking & Reports

The cohort tracking and reports module includes:

- Entry cohort selection by starting school year and grade level
- Grade 7 to Grade 10 full cohort tracking
- Grade 8 to Grade 10 later-entry tracking for transferees
- Cohort status summary and per-student progression table
- Completed, completed-irregular, repeater, transfer-out, and for-review indicators for the selected entry cohort
- Excel export
- Print-friendly report page for browser printing or saving as PDF

## Computed Indicators

The system computes selected-cohort indicators inside Cohort Tracking & Reports:

- **On-Time Completion Rate**: learners who reached Grade 10 on the expected year
- **Overall Completion Rate**: learners who reached Grade 10, including those with irregular progression records
- **For Review / Irregular Count**: learners with transfer, repeater, completed-irregular, missing, or incomplete records

## Project Structure

```text
.
+-- app/
|   +-- app.py                  # Main Flask application
|   +-- backend/                # Backend services, validators, formatters, and DB helpers
|   +-- desktop_launcher.py     # Optional local desktop launcher
|   +-- Dockerfile              # Flask/Gunicorn image
|   +-- requirements.txt        # Python dependencies
|   +-- desktop_requirements.txt # Optional desktop packaging dependencies
|   +-- rsc/                    # Static resources such as school logo
|   +-- templates/              # HTML templates, CSS, and JS assets
+-- db/
|   +-- init.sql                # MySQL schema initialization
+-- web/
|   +-- Dockerfile              # Nginx image
|   +-- default.conf            # Nginx reverse proxy config
+-- docker-compose.yml          # Flask, MySQL, and Nginx services
+-- README.md
```

## Requirements

For the standalone desktop app, the client does not need to install Python, MySQL, Docker, or Git. They only need the generated application folder.

For Docker development, install:

- Docker
- Docker Compose

No local Python or MySQL installation is required when running through Docker.

## How to Install the App

Use this section for testers and client users.

### Installer Version

The recommended way to install the application is to use the Windows installer:

```text
app\installer\LRN-Tracking-System-Setup.exe
```

Installation steps:

1. Double-click `LRN-Tracking-System-Setup.exe`.
2. If Windows asks for permission, choose **Yes**.
3. Follow the setup wizard.
4. Choose whether to create a desktop shortcut.
5. Click **Install**.
6. After installation, open **LRN Tracking System** from the Start Menu or desktop shortcut.

Default login:

```text
Username: admin
Password: admin123
```

Change the password after the first login.

### Portable Folder Version

If the installer is not used, testers can run the portable standalone folder instead:

```text
app\dist\LRN Tracking System
```

Open:

```text
LRN Tracking System.exe
```

Important: copy or send the whole `LRN Tracking System` folder. Do not send only the `.exe`, because the `_internal` folder is required for the app to run.

### Where App Data Is Saved

The installed and portable versions save local data in:

```text
%LOCALAPPDATA%\LRNTrackingSystem
```

This location changes depending on the Windows user. For example, on another computer it may become:

```text
C:\Users\ClientName\AppData\Local\LRNTrackingSystem
```

The local database and password recovery key are stored there. Uninstalling the app does not automatically delete this data.

### Option 1: Standalone Desktop App

Use this option for client/demo use.

1. Open File Explorer.

2. Go to the standalone build folder:

```text
C:\Users\KGG70\my-docker-stack\app\dist\LRN Tracking System
```

3. Double-click:

```text
LRN Tracking System.exe
```

4. Log in using the default account:

```text
Username: admin
Password: admin123
```

5. Change the password after the first login.

If the password is forgotten in standalone mode, open **Forgot password?** on the login page. The app will show the local recovery-key file path. Open that file, copy the recovery key, then use it to set a new password.

If the admin account password is lost, use the same recovery flow:

1. Click **Forgot password?** on the login page.
2. Open the recovery-key file shown on the page.
3. Copy the recovery key.
4. Enter `admin` as the username.
5. Enter the recovery key and a new password.
6. Log in again using the new admin password.

Important: when copying the program to another computer, copy the whole folder:

```text
LRN Tracking System
```

Do not copy only `LRN Tracking System.exe`. The `_internal` folder beside it is required for the app to run.

### Option 2: Docker Web App

Use this option for development or web-style testing.

1. Open the project folder.

```bash
cd my-docker-stack
```

2. Build and start the containers.

```bash
docker compose up -d --build
```

3. Open the app.

```text
http://localhost
```

4. Log in:

```text
admin / admin123
```

5. Change the default password from **Account > Change Password**.

## Standalone Desktop Build Notes

The app can also run as a local standalone-style desktop application. This mode keeps the same Flask pages, templates, CSS, upload workflow, reports, and login system, but stores data in a local SQLite database instead of MySQL.

Standalone mode is enabled with:

```text
APP_DB_ENGINE=sqlite
```

By default, the SQLite file is stored in:

```text
%LOCALAPPDATA%\LRNTrackingSystem\lrn_tracking.db
```

For development, install the optional desktop dependencies and run the launcher from the `app` directory:

```bash
pip install -r desktop_requirements.txt
python desktop_launcher.py
```

The launcher starts the app on `127.0.0.1` and opens it in a desktop window when `pywebview` is available. If the desktop window cannot start, it falls back to the default browser.

To create a Windows standalone build, run this from the `app` directory:

```powershell
.\build_standalone.ps1
```

The generated executable is placed in:

```text
app\dist\LRN Tracking System\LRN Tracking System.exe
```

Distribute the whole `LRN Tracking System` folder inside `dist`, not only the `.exe`, because the packaged runtime stores supporting files beside the executable.

The default standalone account is also:

```text
admin / admin123
```

Change the password after the first login.

Standalone password recovery uses a local recovery key file stored beside the SQLite database:

```text
%LOCALAPPDATA%\LRNTrackingSystem\password_reset_key.txt
```

Keep this file private. Anyone with the recovery key can reset an account password from the **Forgot password?** page.

If the admin password is lost, enter `admin` as the username on the **Forgot password?** page and use the recovery key to set a new admin password. The old password cannot be viewed because passwords are stored as hashes.

## Windows Installer Build

The standalone app can be packaged into a Windows installer after the PyInstaller build is created.

Installer build requirement:

- Inno Setup 6

Recommended flow from the `app` directory:

```powershell
.\build_standalone.ps1
.\build_installer.ps1
```

If Windows blocks PowerShell scripts, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_installer.ps1
```

The installer output will be created in:

```text
app\installer
```

The installer includes the whole standalone app folder and creates shortcuts for the client. User data is still stored outside the installation folder in:

```text
%LOCALAPPDATA%\LRNTrackingSystem
```

Uninstalling the app does not delete the local database or recovery key automatically, so client records are not accidentally removed.

## Main Pages

| Page | URL | Purpose |
| --- | --- | --- |
| Login | `/login` | Sign in to the system |
| Forgot Password | `/forgot-password` | Reset an account password using the local recovery key |
| Dashboard | `/dashboard` | View totals, uploaded record distribution, latest activities, and quick actions |
| LIS Upload | `/lis-upload` | Upload LIS/SF1 files and manage imported batches |
| Students | `/students` | Browse, filter, and open student records |
| Student History | `/student/<lrn>` | View progression history and edit status/remarks |
| Cohort Tracking & Reports | `/cohort-tracking` | Track cohorts and export/print reports |
| Print Report | `/reports/print` | Print or save the selected cohort report as PDF |
| Change Password | `/change-password` | Update the current user's own password |
| User Management | `/users` | Admin-only user account management |
| Logout | `/logout` | Confirm and end the session |

## Upload Workflow

Recommended import order:

1. Upload Grade 7 records for the starting school year.
2. Upload Grade 8 records for the next school year.
3. Upload Grade 9 records for the next school year.
4. Upload Grade 10 records for the final school year.

Each upload requires:

- School year in `YYYY-YYYY` format
- Grade level from Grade 7 to Grade 10
- LIS/SF1 file

Example:

```text
Grade 7  -> 2022-2023
Grade 8  -> 2023-2024
Grade 9  -> 2024-2025
Grade 10 -> 2025-2026
```

## Data Reset Options

The LIS Upload page includes:

- Delete a selected school year and grade batch
- Delete all records

Use these only when re-importing a corrected dataset or preparing a new test/demo batch.

## Database Tables

The system uses these main tables:

- `students`
- `student_records`
- `student_change_logs`
- `users`

Default Docker database values:

```text
Host: db
Database: mydb
User: root
Password: root
```

For local development outside Docker, update the database connection in `app/app.py`.

## Default Login

The system initializes with a default administrator account:

- **Username:** `admin`
- **Password:** `admin123`

It is strongly recommended to change this password immediately after the first login via the "Change Password" page.

## Useful Docker Commands

Start containers:

```bash
docker compose up -d
```

Rebuild and start:

```bash
docker compose up -d --build
```

View running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Stop containers:

```bash
docker compose down
```

Reset database volume:

```bash
docker compose down -v
docker compose up -d --build
```

## Testing Checklist

Use this section when asking classmates, instructors, or client-side testers to check the application.

### Tester Setup

For normal testing, use the Windows installer:

```text
app\installer\LRN-Tracking-System-Setup.exe
```

Steps:

1. Run `LRN-Tracking-System-Setup.exe`.
2. Finish the installer.
3. Open **LRN Tracking System** from the Start Menu or desktop shortcut.
4. Log in using the default test account:

```text
Username: admin
Password: admin123
```

5. If the app asks for permission or takes a few seconds to open, wait until the login screen appears.

Do not use confidential real student records for general testing. Use sample LIS/SF1 files or dummy data unless the school has approved the test data.

### Tester Notes

- The app is for Junior High School records only: Grade 7 to Grade 10.
- The LRN must be exactly 12 digits.
- School year must use `YYYY-YYYY` format, for example `2025-2026`.
- The app stores data locally on the computer in `%LOCALAPPDATA%\LRNTrackingSystem`.
- Uninstalling the app does not automatically delete the local database.
- If the admin password is forgotten, use **Forgot password?** and the local recovery key file.

### Core Test Cases

#### 1. Login and Logout

Expected result:

- Correct admin login opens the dashboard.
- Wrong password shows an error.
- Logout asks for confirmation before ending the session.

#### 2. Forgot Password

Expected result:

- **Forgot password?** opens the recovery page.
- The page shows the recovery-key file path.
- Entering the correct recovery key allows the tester to set a new password.
- The tester can log in using the new password.

#### 3. User Management

Expected result:

- Admin can open **Users**.
- Admin can add a new user.
- Admin can reset another user's password.
- Admin can deactivate or delete another user.
- The system does not allow removing the last active admin.

#### 4. LIS/SF1 Upload

Expected result:

- Valid `.xls`, `.xlsx`, or `.csv` LIS/SF1 files can be uploaded.
- The system detects LRN, name, sex, and remarks columns.
- Duplicate LRNs inside the same file are rejected.
- Missing or invalid rows show a warning before import.
- Imported students appear in **Student Records**.

#### 5. Student Records

Expected result:

- Student records can be searched and filtered.
- A student's history page opens from the student list.
- Only one record per student per school year is allowed.
- Duplicate manual entries with the same LRN and school year are rejected.

#### 6. Student History and LRN Tracking

Expected result:

- Student history shows school-year movement from Grade 7 to Grade 10.
- Name, sex, status, and remarks changes are logged.
- Admin can edit status and remarks.
- Admin can change a student's LRN only after confirming the warning.
- Changing an LRN updates all school-year records for that student.

#### 7. Cohort Tracking and Reports

Expected result:

- Cohort Tracking accepts valid starting school year and grade level.
- The system identifies completed, irregular, repeater, transfer-out, incomplete, and for-review students.
- Report tables show students who leave or disappear from the expected path.
- Excel export downloads successfully.
- Print report opens and can be saved as PDF.

#### 8. Data Deletion and Re-Import

Expected result:

- Admin can delete a selected uploaded batch when needed.
- Admin can delete all records for a fresh test batch.
- After deletion, old student progression records should no longer appear in reports.
- New uploads can be imported after deletion.

### Quick Smoke Test

Before demo or deployment, verify:

- Login works with the admin account
- Wrong password shows an error
- Inactive or deleted users cannot log in
- Admin can add, activate/deactivate, delete, and reset passwords for other users
- Viewer accounts cannot access admin-only upload, edit, delete, or user-management actions
- Session expires after 20 minutes of inactivity
- Logout confirmation appears
- Change password works, then log in again
- LIS upload accepts the client sample files
- LIS upload rejects duplicate LRNs within the same file
- LIS upload warns before continuing when required row data is missing or invalid
- Student records appear in `/students`
- Student history shows Grade 7 to Grade 10 movement
- Manual status/remarks edits create change-log entries
- Cohort tracking shows expected completed, completed-irregular, transfer, repeater, and incomplete students
- Cohort Tracking & Reports shows entry cohorts, review flags, print output, and Excel export
- Excel export downloads successfully
- Print report opens and can be saved as PDF

### Issue Report Format

When a tester finds a problem, record:

```text
Tester name:
Date tested:
App version or installer file used:
Page or feature:
Steps to reproduce:
Expected result:
Actual result:
Screenshot or error message:
Sample file used, if any:
```

Example:

```text
Page or feature: LIS Upload
Steps to reproduce: Uploaded Grade 7 2025-2026 sample file with duplicate LRN.
Expected result: System rejects duplicate LRN.
Actual result: System imported the file.
Screenshot or error message: Attached screenshot.
Sample file used: Sample data.xls
```

- The active Flask application is `app/app.py`.
- The main templates are `dashboard.html`, `records_page.html`, `student_history.html`, `co_tracking.html`, `login.html`, `change_password.html`, `logout_confirm.html`, and `print_report.html`.
- Root-level legacy files such as `app.py` or `index.html`, if present, are not used by the Docker setup.
- Bootstrap and Bootstrap Icons are loaded from CDNs, so internet access is needed for those assets unless they are vendored locally.
- The authentication system is suitable for internal use but should be reviewed by a security expert before public deployment.

Deploy this as a **web service**, not a static website.

The app requires:

- Flask/Gunicorn runtime
- MySQL database
- Persistent database storage
- File upload handling
- Server-side sessions

For production deployment, configure a strong secret key:

```text
FLASK_SECRET_KEY=<your-secure-secret>
```

Also change the default admin password immediately after first login.

## Development Notes

- The active Flask app is `app/app.py`.
- The active dashboard template is `app/templates/dashboard.html`.
- Root-level legacy files such as `app.py` and `index.html` are not used by the Dockerized app.
- Bootstrap and Bootstrap Icons are loaded from CDNs.
- Avoid editing LRNs directly. LRN correction should be handled as a separate controlled feature if needed.

## Troubleshooting

If the app cannot connect to MySQL:

```bash
docker compose ps
docker compose logs db
docker compose logs app
```

If tables are missing or schema changes do not appear:

```bash
docker compose down -v
docker compose up -d --build
```

If port `80`, `5000`, or `3306` is already in use, edit the port mappings in `docker-compose.yml`.

If login fails after changing the password, reset the database volume during local testing or update the `users` table manually.

## License

Add a license before publishing this repository publicly.
