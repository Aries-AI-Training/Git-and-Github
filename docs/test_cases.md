# 🧪 Test Cases Documentation: Academy Intelligence Platform

## Overview
This document outlines the execution results for the functional and system validation test cases performed on the Academy Intelligence Platform (Task 04). Testing covers end-to-end REST API behavior, React state management, persistence integrity, and edge-case handling.

---

## 📊 Summary
* **Total Executed:** 9
* **Passed:** 9
* **Failed:** 0
* **Test Coverage:** REST API Endpoints, Pydantic Validation, Dynamic UI Rendering, Error Code Responses.

---

## 📋 Test Cases Matrix

| Test ID | Category | Feature / Scenario | Input Data | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC01** | **Fetch Data** | Load all students on dashboard startup | `GET /students` | Returns `200 OK` with full list of students. UI populates tables & cards instantly. | Data fetched & rendered correctly | **PASS** |
| **TC02** | **Student Creation** | Add a valid new student profile | `POST /students`<br>`{ "name": "Layan Alkhawaldeh", "study_hours": 15, "attendance_rate": 95, "quiz1": 90, "quiz2": 88, "quiz3": 92 }` | Status `201 Created`; new record saved to storage and appended to UI roster. | Student created & total count increased | **PASS** |
| **TC03** | **Validation** | Add student with missing required fields | `POST /students`<br>`{ "name": "Incomplete User" }` | Status `422 Unprocessable Entity`; Pydantic validation error returned and surfaced. | App handles error without crashing | **PASS** |
| **TC04** | **Conflict Handling** | Add a student with an existing name | `POST /students`<br>`{ "name": "Sara" }` | Status `409 Conflict`; alert notification notifies user of duplicate name. | Duplicate rejected with clear alert | **PASS** |
| **TC05** | **Student Update** | Update metrics for an existing student | `PUT /students/Maya`<br>`{ "attendance_rate": 85 }` | Status `200 OK`; risk classification updates dynamically (e.g., High to Low). | Profile updated & UI badge re-calculated | **PASS** |
| **TC06** | **Student Deletion** | Delete student profile from roster | `DELETE /students/{name}` | Status `200 OK`; record removed from UI state and deleted from `students.json`. | Student removed successfully | **PASS** |
| **TC07** | **Risk Logic** | Calculate "High Risk" classification | Attendance `< 60` OR Average Quiz `< 50` | System badges student as **High Risk** and generates recommended interventions. | Risk rules & advice computed accurately | **PASS** |
| **TC08** | **Inactivity Alert** | Surface inactive student monitoring alert | Student with `days_inactive >= 7` | Triggers alert badge on Dashboard KPI banner with actionable advice. | Inactivity alert displayed on Dashboard | **PASS** |
| **TC09** | **Error Handling** | Fetch non-existent student profile | `GET /students/UnknownUser` | Status `404 Not Found`; app handles gracefully with standard fallback error page. | Handled gracefully via React state | **PASS** |

---

## 🛠️ Verification Commands

To re-run backend verification manually via curl / HTTP clients:

```bash
# 1. Test Fetch All Students
curl -X GET "http://localhost:8000/students"

# 2. Test Fetch Summary KPI Metrics
curl -X GET "http://localhost:8000/students/summary"

# 3. Test Student Deletion
curl -X DELETE "http://localhost:8000/students/Layan%20Alkhawaldeh"