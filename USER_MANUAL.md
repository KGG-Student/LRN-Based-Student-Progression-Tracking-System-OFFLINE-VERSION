# Cover Page

## Integrated LRN-Based Student Progression Tracking System

### User Manual

Prepared for:

```text
Department Head, IT Admin, and School Officials
```

Prepared by:

```text
Group C
```

Document version:

```text
Version 1.0
```

Date:

```text
May 31, 2026
```

System description:

```text
A standalone student progression tracking system for Junior High School learners
from Grade 7 to Grade 10 using the 12-digit Learner Reference Number (LRN).
```

Confidentiality note:

```text
This document is intended for authorized school personnel only. Student records,
system access details, and generated reports should be handled according to
school data privacy and confidentiality policies.
```

\pagebreak

# Integrated LRN-Based Student Progression Tracking System User Manual

## Purpose

The Integrated LRN-Based Student Progression Tracking System helps the department head monitor Junior High School learners from Grade 7 to Grade 10 using the 12-digit Learner Reference Number (LRN). The system imports LIS/SF1 Excel files, stores student records, tracks cohort movement, identifies transfer and incomplete records, computes progression indicators, and generates Excel or print-ready reports.

The system is intended for internal school use only. It does not replace the official LIS system and does not connect directly to the national LIS database.

## Intended Users

### Department Head / Main User

The department head uses the system to upload LIS/SF1 files, manage student records, monitor Grade 7 to Grade 10 progression, review irregular learners, and generate reports.

### IT Admin / Technical Maintainer

The IT admin installs the application, prepares the local environment, assists with backups, manages troubleshooting, and ensures the application is updated properly.

### School Official / Reviewer

The school official reviews reports, verifies cohort results, checks transfer and completion summaries, and uses the generated reports for documentation or decision-making.

## System Scope

The system supports:

- Uploading and processing LIS/SF1 Excel or CSV exports
- Centralized student record management using LRN
- Grade 7 to Grade 10 cohort tracking
- Transfer-in, pending transfer-in, and transfer-out monitoring
- Detection of missing, irregular, repeated, or incomplete learner records
- Automatic computation of progression indicators
- Excel report generation
- Print-friendly reports that can be saved as PDF
- Login, logout, password change, forgot password, and user access control

The system does not support:

- Direct LIS API connection
- Elementary or Senior High School records
- Online enrollment
- Parent or student portals
- Grading or attendance monitoring

## Basic Requirements

For normal client use, install the Windows standalone application using:

```text
app\installer\LRN-Tracking-System-Setup.exe
```

The client does not need to install Python, MySQL, Docker, or Git when using the installer version.

## First-Time Login

1. Open **LRN Tracking System** from the desktop shortcut or Start Menu.
2. Log in using the default account:

```text
Username: admin
Password: admin123
```

3. Go to **Change Password**.
4. Set a new secure password.
5. Keep the new password private.

## Main Navigation

### Dashboard

The Dashboard shows a quick overview of system records, recent changes, and student distribution. Use this page to check whether uploaded data is reflected in the system.

### LIS Upload

The LIS Upload page is used to import student records from LIS/SF1 Excel or CSV files. Only authorized users should upload or delete data.

### Students

The Students page allows users to search, filter, and open individual student records. Users can filter by grade level, status, school year, LRN, or student name. Grade Level and Status dropdown filters apply automatically once selected.

### Student History

The Student History page shows a learner's school-year records, grade movement, status, remarks, and change logs. Admin users can edit status, remarks, add a year record, remove a student, or correct an LRN when necessary.

### Cohort Tracking & Reports

The Cohort Tracking & Reports page tracks a selected entry cohort from the starting grade to Grade 10. It shows completed, incomplete, repeated, transferred, irregular, and for-review students.

### Users

The Users page is available only to admin users. It is used to add, reset, deactivate, activate, or delete user accounts.

### Change Password

The Change Password page lets the current user update their own password.

### Logout

Logout ends the current session. The system asks for confirmation before logging out.

## Department Head User Guide

### Uploading LIS/SF1 Data

1. Open **LIS Upload**.
2. Enter the school year using `YYYY-YYYY` format, for example:

```text
2025-2026
```

3. Select the grade level from Grade 7 to Grade 10.
4. Choose the LIS/SF1 Excel or CSV file.
5. Click **Upload**.
6. Review any warning message shown by the system.
7. If the file has valid data, continue the import.

Recommended upload order:

```text
Grade 7  -> 2022-2023
Grade 8  -> 2023-2024
Grade 9  -> 2024-2025
Grade 10 -> 2025-2026
```

### Searching and Filtering Students

1. Open **Students**.
2. Use the search box to search by LRN or student name.
3. Select a Grade Level or Status from the dropdown to filter automatically.
4. Enter a School Year if needed.
5. Click **Filter** if using the search box or school year input.
6. Click **View History** to open a learner's full record.

### Viewing Student History

1. Open **Students**.
2. Find the learner.
3. Click **View History**.
4. Review the student's school year records, grade levels, status, remarks, and change logs.

### Editing Student Status or Remarks

1. Open the student's history page.
2. Choose the record that needs correction.
3. Click edit for that record.
4. Update the status or remarks.
5. Save the change.

Use this only for verified corrections. The system records changes in the change log.

### Correcting a Student LRN

1. Open the student's history page.
2. Choose the LRN correction option.
3. Enter the new 12-digit LRN.
4. Read the warning carefully.
5. Type the required confirmation phrase.
6. Confirm the update.

Changing an LRN updates all school-year records connected to that student. This should only be done when the LRN correction is verified.

### Adding a Student Manually

1. Open **Students**.
2. Click **Add New Student**.
3. Enter the LRN, name, sex, grade, school year, status, and remarks.
4. Type the required confirmation phrase.
5. Confirm the add action.

The system rejects duplicate LRNs and duplicate school-year records to protect data integrity.

### Generating Cohort Tracking Reports

1. Open **Cohort Tracking & Reports**.
2. Enter the starting school year, for example:

```text
2022-2023
```

3. Select the entry grade level.
4. Click **Generate Tracking**.
5. Review the summary cards, progression path, retention/repetition breakdown, and student cohort list.
6. Click **Export Excel** to create an Excel report.
7. Click **Print / Save PDF** to open the print-ready report.

### Understanding Remarks

Some records may display remarks such as:

```text
Remarks: CCT
```

This means the learner is still counted based on their actual status, such as **Enrolled**, while `CCT` is stored as an additional remark from the uploaded record or manual entry.

## Computed Indicators

### Gross / Survival Rate

Gross / Survival Rate is computed as:

```text
Grade 10 Enrollment Current SY / Grade 7 Enrollment SY (N-3) x 100
```

### Completion Rate

Completion Rate is computed as:

```text
Grade 10 Completers Current SY / Grade 7 Enrollment SY (N-3) x 100
```

Note: the current system treats a valid Grade 10 record as a Grade 10 completer because there is no separate graduation/completer field yet.

### Retention Rate

Retention Rate is computed as:

```text
Enrollment Current SY / Enrollment Previous SY x 100
```

New learners and transferees are excluded from the retained count.

### Repetition Rate

Repetition Rate is computed as:

```text
Number of Repeaters Current SY / Total Enrollment Current SY x 100
```

## IT Admin Guide

### Installing the Application

1. Locate the installer:

```text
app\installer\LRN-Tracking-System-Setup.exe
```

2. Double-click the installer.
3. Follow the setup wizard.
4. Create a desktop shortcut if needed.
5. Open **LRN Tracking System** after installation.

### Updating the Application

1. Close the running application.
2. Run the updated installer.
3. Install it in the same location.
4. Open the app and verify the updated features.

The user data is stored separately, so reinstalling normally does not delete student records.

### Data Storage Location

The standalone app stores local data in:

```text
%LOCALAPPDATA%\LRNTrackingSystem
```

On a specific computer, this may look like:

```text
C:\Users\ClientName\AppData\Local\LRNTrackingSystem
```

Important files may include:

```text
lrn_tracking.db
password_reset_key.txt
exports
```

### Backup Recommendation

Before major updates or data reset, copy the full folder:

```text
%LOCALAPPDATA%\LRNTrackingSystem
```

Keep backups in a secure location because the folder may contain student records and password recovery data.

### Password Recovery

If the admin forgets the password:

1. Open the login page.
2. Click **Forgot password?**
3. Open the recovery key file shown on the page.
4. Copy the recovery key.
5. Enter the username, recovery key, and new password.
6. Log in using the new password.

Keep the recovery key private. Anyone with the recovery key may reset an account password.

### Troubleshooting

If the app does not open:

- Wait a few seconds after launching.
- Close duplicate app windows.
- Restart the computer if the local app process is stuck.
- Reinstall using the latest installer.

If reports do not export:

- Check the Downloads folder.
- Check:

```text
%LOCALAPPDATA%\LRNTrackingSystem\exports
```

If data appears missing:

- Confirm the correct Windows user account is being used.
- Check whether the local database exists in `%LOCALAPPDATA%\LRNTrackingSystem`.
- Restore from backup if needed.

## School Official / Reviewer Guide

### Reviewing Student Progression

1. Open **Cohort Tracking & Reports**.
2. Select the correct starting school year and grade level.
3. Review the summary cards.
4. Check the student cohort list for missing, incomplete, repeated, transfer-out, or irregular learners.

### Reviewing At-Risk or For-Review Students

Students may be marked for review when they:

- Disappear from the expected Grade 7 to Grade 10 path
- Have missing school-year records
- Repeat a grade
- Transfer out
- Complete Grade 10 through an irregular path

These records should be validated against official school documents and LIS/SF1 files.

### Using Reports

The system can generate:

- Excel reports
- Print-ready reports
- PDF reports through the print dialog

Use **Export Excel** when further editing or tabulation is needed. Use **Print / Save PDF** when submitting or attaching a clean report copy.

### Report Verification Checklist

Before accepting a report, verify:

- The starting school year is correct
- The selected entry grade level is correct
- Grade 7 to Grade 10 years are aligned properly
- Missing students are reviewed
- Transfer-in and transfer-out records are checked
- Completion, survival, retention, and repetition rates match the selected cohort
- The report date and exported file are the latest version

## Data Privacy and Security Reminders

- Do not share real student records with unauthorized people.
- Do not upload confidential files to public systems.
- Change the default admin password after installation.
- Keep the recovery key private.
- Back up local data securely.
- Use the system only for authorized school-level tracking and reporting.

## Common Issues and Solutions

### The School Year Field Looks Empty

The school year must be typed manually using this format:

```text
YYYY-YYYY
```

Example:

```text
2025-2026
```

### The Placeholder Looks Like Real Input

Fields now use example-style placeholders such as:

```text
e.g. 2025-2026
```

If the field already contains a value, the placeholder will not show.

### A Student Appears as Missing

This means the LRN was expected in the selected school year and grade level but was not found in the uploaded records. Verify the LIS/SF1 file, transfer documents, or manual records.

### A Remark Such as CCT Appears

This means the text was saved as a record remark. The system still uses the actual status badge, such as **Enrolled**, for calculation unless the status itself indicates transfer, repetition, or another tracking condition.

## Recommended Workflow

1. Install the application.
2. Log in using the admin account.
3. Change the default password.
4. Upload Grade 7 to Grade 10 LIS/SF1 records in order.
5. Review the Students page for missing or duplicate data.
6. Open student histories for correction or verification.
7. Generate the cohort tracking report.
8. Export Excel or save the print report as PDF.
9. Back up the local data folder.

## Support Notes

When reporting an issue, include:

```text
User name:
Computer used:
Date tested:
App installer version or timestamp:
Page or feature:
Steps performed:
Expected result:
Actual result:
Screenshot or error message:
Sample file used:
```
