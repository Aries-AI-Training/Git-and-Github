# Student Learning Intelligence Report - Task 01

## 1. What problem are we solving?
We are analyzing student learning behavior data for an online AI foundations course. The goal is to identify high-performing students, pinpoint students at risk of dropping out or failing, understand the behaviors linked to poor performance, and prepare data features for future predictive AI models.

## 2. What data do we have?
We analyzed data from 6 students. The dataset tracks demographic information (Age) and key engagement metrics:
* Study hours & Lesson completion percentage.
* Attendance rate & Quiz scores.
* Days of inactivity, projects submitted, and support messages sent.

## 3. What calculations did we perform?
Using Python, we calculated:
* **Individual Metrics:** Average quiz score and lesson completion percentage per student.
* **Academy Averages:** The overall academy attendance rate (**73.33%**) and the average quiz score across all students (**71.44**).
* **Risk Classification:** Grouping students into High, Medium, or Low Risk using structured business logic based on their grades, attendance, and inactivity.
* **AI Readiness:** Converting all raw data into a clean, numerical feature matrix using NumPy for future Machine Learning modeling.

## 4. Which students are at risk?
Based on our business rules, the students are classified as follows:
* **High Risk (2 Students):** * **Maya:** Low quiz average (58.33) and low course completion (40%).
  * **Noor:** Very low attendance (45%), weak quiz average (46.67), and 10 days of inactivity.
* **Medium Risk (1 Student):** * **Rama:** Inactive for 4 days, with borderline attendance (70%).
* **Low Risk / High Performing (3 Students):** * **Huda:** The top performer with a **92.67** quiz average and 93.33% completion.
  * **Sara** and **Lina** are also performing safely and consistently.

## 5. What patterns did we notice?
* **Inactivity and Attendance Drive Risk:** Students who are inactive for more than 4 days (like Noor and Maya) show a drastic drop in attendance, which directly correlates with failing quiz scores (below 60).
* **Support Messages Misconception:** High-risk students send more support messages (Noor sent 5, Maya sent 3), indicating they are struggling but reaching out too late, rather than being disengaged.

## 6. What data might be useful for a future AI model?
To build a machine learning model that predicts student risk, the numeric feature matrix we created is perfect. The most critical features (columns) are:
1. `attendance_rate` (Strongest early indicator).
2. `days_inactive` (Tracks drop in engagement).
3. `average_quiz_score` (Measures actual academic comprehension).
4. `study_hours` (Measures effort).

## 7. What extra data should the academy collect in the future?
To improve our future AI model's accuracy, the academy should start collecting:
* **Platform Interaction Logs:** Number of clicks per day or time spent on the platform.
* **Assignment Submission Delays:** Tracking if homework is submitted on time or late.
* **Forum Engagement:** Number of questions asked or answered in student community groups.
* **Student Feedback/Sentiment:** Periodic short pulse surveys rating their confidence level in the course.
