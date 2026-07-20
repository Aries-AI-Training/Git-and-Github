# 🧠 Solution Proposal: Academy Intelligence Platform (Task 04)

## 1. Business Problem Understanding
Academy managers and administrative decision-makers often struggle to evaluate student progress, retention risks, and overall performance using raw database logs or terminal CLI outputs. Without a centralized visual interface, identifying at-risk students and acting on low engagement requires complex, manual data assembly.

## 2. Target Users & Stakeholders
* **Academy Managers / Directors:** Need macro-level visibility into institutional KPIs (total students, class attendance averages, overall quiz scores) to evaluate academy health.
* **Academic Advisors & Instructors:** Require student-level insights to pinpoint specific risk reasons (e.g., low attendance vs. inactive days) and execute targeted interventions.

## 3. System Architecture & Page Structure
The platform is constructed as an end-to-end full-stack web application connecting a lightweight React frontend with our FastAPI backend:
1. **Academy Dashboard (`/dashboard`):** Displays real-time aggregate statistics, top performer cards, high-risk flags, and automated activity monitoring alerts.
2. **Students Management (`/students`):** Interactive data grid listing all enrolled students, calculated completion percentages, risk badges, and direct trigger buttons for profile editing and deletion.
3. **At-Risk Students Panel (`/at-risk`):** Action-oriented dashboard isolating High and Medium Risk students, displaying context-aware failure reasons and automated, rule-based intervention steps.
4. **Student Management Form (`/add-student`):** Universal dynamic form for creating new student profiles or pre-filling existing records for updates.

## 4. Business Scope Expansion Features
To extend platform utility beyond original calculations, two high-value business features were introduced:
* **Rule-Based Recommended Interventions:** Generates automated actionable advice for advisors (e.g., recommending follow-up calls for inactivity vs. instructor material support for low quiz scores).
* **Automated Inactive Student Monitoring:** Monitors student activity gaps and triggers real-time alerts on the primary dashboard when a student is inactive for 7+ days.

## 5. API Endpoints Architecture

* **Existing / Upgraded Endpoints:**
  * `GET /students` — Retrieve processed student roster with calculated completion and risk values.
  * `POST /students` — Register a new student with strict Pydantic model validation.
  * `GET /students/summary` — Aggregate academy statistics, highest risk students, and business alerts.
* **New RESTful Endpoints Added:**
  * `GET /students/{student_name}` — Fetch individual profile metrics for form pre-filling.
  * `PUT /students/{student_name}` — Update existing student attributes in file storage.
  * `DELETE /students/{student_name}` — Remove student profile from state and file system.

## 6. Development & Work Division
The workload was executed systematically through structured development phases:

API Expansion Phase: Designed PUT, DELETE, and GET /{name} endpoints with error handling (404, 409).

Frontend Design Phase: Built modern dashboard components using React state and Tailwind CSS styles.

Integration Phase: Connected client axios requests to backend routes with loading states and CORS enablement.

Testing & Verification: Executed manual test cases across form validation, duplicate student handling, and connection resiliency.
## 7. Proposed Project Structure
```text
project-root/
│
├── api/
│   └── routes.py              # FastAPI endpoints & REST logic
├── src/
│   ├── models/student.py      # Pydantic validation schemas
│   ├── metrics.py             # Score & attendance calculations
│   └── risk.py                # Risk evaluation rules
├── frontend/
│   └── index.html             # React App + Tailwind UI + Axios
├── data/
│   └── students.json          # Persistent JSON storage
├── logs/
│   └── application.log        # System execution logs
└── main.py                    # Server initialization & CORS configuration
