# CampyTeq — Unified Multi-College Digital Ecosystem
## Comprehensive System Architecture, Workflows & 12 Institutional Roles Specification
**Document Version:** 1.0.0 Production Spec | **Status:** Active & Implemented

---

## Table of Contents
1. [Executive Summary & Engineering Principles](#1-executive-summary--engineering-principles)
2. [High-Level Architecture & Multi-Tenancy Invariants](#2-high-level-architecture--multi-tenancy-invariants)
3. [End-to-End Core Institutional Workflows](#3-end-to-end-core-institutional-workflows)
   - [Workflow 1: Academic Hierarchy & Timetable Engine](#workflow-1-academic-hierarchy--timetable-engine)
   - [Workflow 2: Attendance & Faculty Timesheets](#workflow-2-dual-attendance--statutory-defaulters-radar)
   - [Workflow 3: Examination Governance & Assignments](#workflow-3-examination-governance--assignments)
   - [Workflow 4: Fees, Invoicing & Payroll Batches](#workflow-4-financial-governance-invoicing--payroll)
   - [Workflow 5: Audience-Scoped Circulars & Leave Management](#workflow-5-audience-scoped-circulars--leave-management)
   - [Workflow 6: Campus Fast-Print Kiosk Queue](#workflow-6-campus-fast-print-kiosk-queue)
   - [Workflow 7: Digital Library Catalog & Circulation](#workflow-7-digital-library-catalog--circulation)
   - [Workflow 8: Edge Computer Vision Campus Tracking](#workflow-8-edge-computer-vision-campus-tracking)
   - [Workflow 9: AI Academic Early Warning Radar](#workflow-9-ai-academic-early-warning-radar)
   - [Workflow 10: Student Mobile Companion](#workflow-10-student-mobile-companion-react-native--expo)
4. [Detailed Feature Breakdown Inside All 12 Logins](#4-detailed-feature-breakdown-inside-all-12-logins)
   - [1. Super Admin](#1-super-admin-superadmincampyteqio)
   - [2. Principal](#2-principal-principalapexedu)
   - [3. Management / Trustee](#3-management--trustee-managementapexedu)
   - [4. Head of Department (HOD)](#4-head-of-department-hod-hodcsapexedu)
   - [5. Faculty Mentor](#5-faculty-mentor-mentoranilapexedu)
   - [6. Faculty Instructor](#6-faculty-instructor-facultypriyaapexedu)
   - [7. Accountant / Bursar](#7-accountant--bursar-accountantramanapexedu)
   - [8. Enrolled Student](#8-enrolled-student-studentrahulapexedu)
   - [9. Parent / Guardian](#9-parent--guardian-parentapexedu)
   - [10. Campus Security Officer](#10-campus-security-officer-securitychiefapexedu)
   - [11. Print Shop Staff](#11-print-shop-staff-printstaffdevapexedu)
   - [12. Library Staff](#12-library-staff-librarystaffanitaapexedu)
   - [Cross-Tenant Isolation Persona: Metro Student](#cross-tenant-isolation-persona-studentothermetroedu)
5. [Production Runbook, Hardware Peripherals & Privacy Compliance](#5-production-runbook-hardware-peripherals--privacy-compliance)

---

## 1. Executive Summary & Engineering Principles

**CampyTeq** is an enterprise-grade higher education SaaS digital ecosystem designed to eradicate siloed departmental tools across college campuses. It unifies administrative governance, curriculum scheduling, examinations, dual lecture and biometric attendance, fee billing, payroll, audience-scoped announcements, campus fast-print kiosks, digital library circulation, edge CCTV safety tracking, and explainable AI student risk analytics under strict row-level multi-tenant isolation and responsive web and mobile interfaces.

### Core Architectural Invariants
- **Multi-Tenant Row-Level Isolation:** Every database model inherits from `TenantModel` (`common.models.TenantModel`), enforcing a mandatory foreign key to `College` (`college_id`).
- **Zero Client-Side College Overrides:** Under no circumstances can client-supplied POST/PUT body parameters override the tenant identifier. The college context is strictly resolved from the authenticated JWT session (`request.user.college`).
- **Cross-Tenant Administrative Context Switching:** Only users with the `SUPER_ADMIN` role may pass a verified `X-College-ID` HTTP header to inspect live tenant states without modifying base database credentials.
- **Stateless API:** Built on Django 5.1 REST Framework with `SimpleJWT` token rotation, OpenAPI 3.0 auto-generation via `drf-spectacular`, and uniform response envelopes:
  ```json
  // Success
  { "success": true, "message": "...", "data": { ... } }
  // Error
  { "success": false, "message": "...", "code": "...", "errors": { ... } }
  ```

---

## 2. High-Level Architecture & Multi-Tenancy Invariants

```text
                                 [ Internet Traffic ]
                                          │
                                          ▼
                           [ Port 80 / 443 — Nginx Proxy ]
                             (SSL / TLS & Rate Limiting)
                                          │
                     ┌────────────────────┴────────────────────┐
                     ▼                                         ▼
          [ Next.js 14 Frontend ]                  [ Gunicorn WSGI Backend ]
           (Node 20 Cluster :3000)                   (Django 5 DRF :8000)
                     │                                         │
       ┌─────────────┴─────────────┐                           │
       ▼                           ▼                           │
[ Web Browser ]             [ Mobile App ]                     │
(Next.js App Router)       (Expo 51 / React Native)            │
                                                               │
                          ┌────────────────────────────────────┴──────────────┐
                          ▼                                                   ▼
              [ PostgreSQL 16 Alpine ]                             [ Redis 7 Alpine ]
               (Multi-Tenant Schema)                                (Cache, Queues & JWT)
                          ▲
                          │ (Edge Sighting Ingestion)
               [ cv-service Gateway ]
                (OpenCV / RTSP Streams)
```

---

## 3. End-to-End Core Institutional Workflows

### Workflow 1: Academic Hierarchy & Timetable Engine
- **Structural Tree:** College → Academic Department (headed by HOD) → Degree Course (B.Tech, BCA, MCA) → Batch (e.g. 2023-2027) → Semester → Subject (Theory / Lab).
- **Faculty Allocation:** Teachers are mapped to specific subjects within their department. Cross-department elective assignments are supported.
- **Weekly Timetable Engine:** Configures recurring class schedules with designated lecture slots, lab durations, room allocations, and collision detection against faculty double-booking.

### Workflow 2: Dual Attendance & Statutory Defaulters Radar
- **Classroom Lecture Attendance:** Faculty open their active lecture slot, view the enrolled student roster, and execute 1-click "Mark All Present" with individual toggle switches for "Absent" or "Late".
- **Statutory 75% Defaulter Radar:** Background analytics calculate attendance percentage in real-time. Students falling below 75% are automatically flagged with warning alerts across Principal, HOD, Mentor, and Student portals.
- **Faculty Biometric Timesheets:** Daily check-in/out records log faculty instructional hours and on-campus presence.

### Workflow 3: Examination Governance & Assignments
- **Exam Series Lifecycle:** Examination coordinators create mid-terms and finals, define schedules, and open grade entry windows.
- **Confidential Publishing:** Scores entered by faculty remain confidential until formally approved and published by the Principal.
- **Coursework & Grading:** Instructors create assignments with attachments and deadlines; students submit online; instructors grade submissions with feedback.

### Workflow 4: Financial Governance, Invoicing & Payroll
- **Course Fee Structures:** Annual and semester fee structures configured per course and batch (tuition, laboratory, library, developmental).
- **Student Invoicing & Receipts:** Itemized invoices generated automatically. Integrated payment simulator records transactions and generates instant digital PDF receipts.
- **Confidential Faculty Payroll:** Monthly salary batches calculate base pay, HRA/DA allowances, and deductions, generating private payslips.

### Workflow 5: Audience-Scoped Circulars & Leave Management
- **Targeted Broadcasts:** Circulars scoped to `ALL`, `STUDENTS`, `FACULTY`, `HOD`, or specific departments with file attachments.
- **Multi-Tier Leave Hierarchy:** Students submit leave requests to Mentors; Faculty submit to HOD; HOD submits to Principal. Balances, medical certificates, and approval audit trails are recorded.

### Workflow 6: Campus Fast-Print Kiosk Queue
- **Job Submission:** Students upload documents, configure copies, color vs. B/W, duplex, and paper size with real-time cost calculation.
- **Pickup PIN Generation:** System debits student balance and issues an encrypted 4-digit PIN.
- **Kiosk Dispatch:** Print kiosk staff enter the 4-digit PIN at the terminal to trigger physical network printing.

### Workflow 7: Digital Library Catalog & Circulation
- **Resource Management:** Books tracked with ISBN, title, author, category, rack location, and available copies.
- **Circulation & Fines:** Barcode/ID checkout and return tracking. System automatically applies a ₹5/day overdue fine beyond the statutory loan period.

### Workflow 8: Edge Computer Vision Campus Tracking
- **CCTV Zone Registry:** IP cameras mapped across gates, library, academic blocks, cafeteria, and perimeters.
- **Sighting Ingestion:** Edge vision gateway detects student presence and streams detection events to `/api/v1/tracking/sightings/`.
- **Journey Stepper:** Visual chronological breadcrumb timeline tracking student campus movements.
- **Regulatory Privacy Audit:** Security queries require mandatory justification logs to prevent unmonitored surveillance.

### Workflow 9: AI Academic Early Warning Radar
- **Multi-Factor Risk Model:** Computes composite failure risk based on attendance (< 75%), internal test marks (< 40%), assignment timeliness, and overdue fees.
- **Proactive Counseling Interventions:** Mentors receive automated alerts to schedule counseling interventions before semester disqualification.

### Workflow 10: Student Mobile Companion (React Native / Expo)
- Cross-platform smartphone companion offering live schedules, attendance radar, pending tasks, fee receipts, and print kiosk PINs.

---

## 4. Detailed Feature Breakdown Inside All 12 Logins

| Role | Demo Account | Default Password | Primary Scope |
|---|---|---|---|
| **Super Admin** | `superadmin@campyteq.io` | `Password123!` | Global SaaS Governance & Cross-Tenant Switcher |
| **Principal** | `principal@apex.edu` | `Password123!` | Executive Institutional Command & Grade Approval |
| **Management** | `management@apex.edu` | `Password123!` | Financial Velocity & Strategic Operations |
| **HOD (CS)** | `hod.cs@apex.edu` | `Password123!` | Department Roster, Curriculum & Faculty Mapping |
| **Mentor** | `mentor.anil@apex.edu` | `Password123!` | Cohort Early Warning Radar & Mentee Counseling |
| **Faculty** | `faculty.priya@apex.edu` | `Password123!` | Attendance Marking, Assignments & Exam Grading |
| **Accountant** | `accountant.raman@apex.edu` | `Password123!` | Fee Invoices, Collections & Faculty Payroll |
| **Student** | `student.rahul@apex.edu` | `Password123!` | Academics, Attendance Radar, Fees & Print Shop |
| **Parent** | `parent@apex.edu` | `Password123!` | Ward Attendance, Grades & Fee Settlement |
| **Security** | `security.chief@apex.edu` | `Password123!` | CCTV Status, Student Sighting Ingestion & Audit Logs |
| **Print Staff** | `printstaff.dev@apex.edu` | `Password123!` | Print Queue Fulfillment & 4-Digit PIN Validation |
| **Library Staff** | `librarystaff.anita@apex.edu` | `Password123!` | Cataloging, Book Issues & Overdue Fines |
| **Metro Student** | `student.other@metro.edu` | `Password123!` | Multi-Tenant Data Isolation Test Persona |

---

## 5. Production Runbook, Hardware Peripherals & Privacy Compliance

### 1. Hardware Integration
- **RTSP IP Cameras:** Configure network cameras in `cv-service/stream_simulator.py` by replacing test loops with RTSP URLs (`rtsp://admin:pass@192.168.1.X:554/live`).
- **Biometric Scanners:** Connect ZKTeco/eSSL biometric scanners via push SDK targeting `/api/v1/attendance/faculty-checkin/`.
- **Kiosk Printers:** Connect fast-print kiosk terminals via CUPS / IPP network printers.

### 2. Privacy & Compliance
- **Zero GPS Tracking:** CampyTeq mobile companion records biometric presence exclusively through authorized physical campus CCTV checkpoints.
- **30-Day Auto-Purge:** Raw CCTV student sightings and facial embeddings are automatically purged after 30 days in compliance with DPDP, FERPA, and GDPR.
- **Ethical AI Advisory:** AI Early Warning Radar is strictly decision-support for human mentors; automated disciplinary penalties are prohibited.
