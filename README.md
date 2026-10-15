# Ayurveda Wellness and Guidance (AyurWellness)

## 1 INTRODUCTION
### 1.1 Background of the Study
The integration of traditional healthcare with digital technology is a growing trend. Ayurveda, the ancient Indian 'Science of Life', offers holistic remedies and preventive care. However, modern users often find it difficult to identify their constitution (Dosha) and maintain consistent routines without expert guidance. This study explores the digitization of Ayurvedic principles to make them accessible, personalized, and engaging.

### 1.2 Problem Statement
Traditional Ayurvedic wisdom is often inaccessible to the modern population due to its complexity. There is a lack of a unified platform that combines:
*   Standardized Dosha assessment.
*   Personalized habit tracking based on constitution.
*   AI-powered instant guidance.
*   Secure interaction with certified practitioners.

### 1.3 Objectives
*   Develop an automated **Dosha Assessment** system.
*   Provide **Personalized Wellness Routines** (Dinacharya).
*   Integrate an **AI Chatbot (DocAyu)** for wellness tips.
*   Enable **Practitioner Consultations** and Digital Health Records.

### 1.4 Scope of the Project
The project focuses on a web-based ecosystem containing:
1.  **Patient/User Portal:** Quiz, routine, and appointment booking.
2.  **Practitioner Portal:** Scheduling and health record management.
3.  **Admin Portal:** System oversight and activity monitoring.
4.  **AI Module:** Knowledge-based conversational assistant.

### 1.5 Organization of the Report
The README and associated report are organized into sections covering Literature Review, SRS, System Analysis, Implementation, and Testing results.

---

## 2 LITERATURE REVIEW
### 2.1 Introduction to Existing Systems
Existing systems range from basic Dosha questionnaires to complex AI-integrated apps like AyuRythm and Vedix, which offer personalized products and reviews.

### 2.2 Review of Related Works
1.  **AyuRythm (mHealth App):** Uses smartphone-based pulse diagnosis (Naadi Pariksha) for Dosha profiling.
2.  **Jiva Ayurveda (E-Consultation):** A large-scale digital platform for Ayurvedic consultations and product recommendations.
3.  **Vedix (Personalized Care):** Uses data gathering (Prakriti test) to customize hair and skin care regimens.
4.  **Government Initiatives (Ayush Grid):** Integrated digital platform by the Ministry of AYUSH to standardize and provide digital health services in India.
5.  **Digital India Health Initiatives:** Framework for electronic health records (EHR) that includes alternative medicine.

### 2.3 Comparative Analysis Table
| Feature | AyurWellness (Proposed) | AyuRythm | Jiva Ayurveda | Vedix |
| :--- | :--- | :--- | :--- | :--- |
| **Dosha Assessment** | Interactive Quiz | Pulse Diagnosis | Questionnaire | Prakriti Test |
| **Habit Tracking** | Gamified Routine | Wellness Regimes | Limited | Product Focused |
| **AI Support** | DocAyu Chatbot | Personalized Tips | Human-Led | Static Tips |
| **EHR Integration** | High (Vitals/Docs) | Limited | Internal Only | None |
| **Community Feed** | Blogs/Reviews | None | Articles | Limited |

### 2.4 Limitations of Existing Systems
*   **AyuRythm:** High reliance on hardware/sensors; less focus on long-term routine tracking.
*   **Vedix:** Primarily product-centric rather than a holistic health platform.
*   **Jiva:** Human-led consultations lack 24/7 instant AI guidance.

### 2.5 Research Gap Identification
Most current systems focus either on diagnosis or product sales. There is a gap for a **unified daily engagement platform** that combines active habit tracking (gamification) with AI-led knowledge and professional healthcare records in one seamless interface.

### 2.6 Proposed System Overview
AyurWellness closes this gap by providing an MVT-based web platform that uses constitution-based personalization to drive daily wellness habits, supported by both AI and human experts.

---

## 3 SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
### 3.1 Purpose
To define the requirements for a comprehensive wellness portal integrating traditional Indian medicine with modern IT frameworks.

### 3.2 Overall Description
*(Detailed in project_report.md)*
*   **3.2.1 Product Perspective:** Standalone Django-based web application.
*   **3.2.2 Product Functions:** RBAC, Dosha Quiz, Routine Tracker, AI Chatbot, Appointment Booking.
*   **3.2.3 User Classes:** Patient, Practitioner, Admin.
*   **3.2.4 Operating Environment:** Modern Browsers, Python 3.x, SQL Server.

### 3.3 Functional Requirements
*   **FR1:** User Authentication.
*   **FR2:** Dosha Score Calculation.
*   **FR3:** Daily Routine Reset and Status Tracking.
*   **FR4:** AI Chatbot Response Management.
*   **FR5:** Health Vitals Recording (Practitioner only).

### 3.4 Non-Functional Requirements
*   **3.6.1 Performance:** <2s page load.
*   **3.6.2 Scalability:** Modular architecture for future expansions.
*   **3.6.3 Security:** CSRF, XSS protection, and secure document storage.
*   **3.6.4 Reliability:** 99.9% uptime for core services.
*   **3.6.5 Usability:** Mobile-responsive premium UI.
*   **3.6.6 Maintainability:** Well-documented code patterns.

### 3.5 Constraints
*   Requires internet connectivity.
*   Manual approval for practitioners.

### 3.6 Assumptions & Dependencies
*   Users provide accurate inputs for the quiz.
*   Database connectivity to SQL Server for production deployments.

---

## 4 SYSTEM ANALYSIS AND DESIGN
### 4.1 Overall System Architecture
Based on the Django **MVT (Model-View-Template)** pattern.

### 4.2 Module Description
*(Refer to project_report.md for detailed breakdown)*
1. Auth 2. Dosha 3. Chatbot 4. Engagement 5. Consultation 6. Admin.

### 4.3 Data Flow Diagram
*   **Level 0:** System Context.
*   **Level 1:** Module Interactions.

### 4.4 Use Case Diagram
Detailed patient and practitioner interaction flows.

### 4.7 Database Design
Relational schema linking Users, Profiles, Results, Appointments, and Blogs.

---

## 5 IMPLEMENTATION
### 5.1 Development Environment
*   **Backend:** Django 5.x.
*   **Frontend:** HTML5, Vanilla CSS, JS.
*   **Storage:** MS SQL Server + SQLite.

### 5.2 Module-wise Implementation
*(Details on Dashboard, Quiz, Chatbot, and Tracker implementation)*

---

## 6 TESTING
### 6.1 Testing Strategy
Unit, Integration, and System testing flows.

### 6.2 Test Case Table
*(Pass/Fail results for Auth, Quiz, Booking, and Chat tests)*

---

## 7 RESULTS & DISCUSSION
### 7.1 Output Results
Successful deployment of the portal with functional Dosha scoring and routine tracking.

### 7.2 Comparison with Existing Systems
AyurWellness leads in holistic data logging and 24/7 AI-guided engagement.

---

## 8 CONCLUSION & FUTURE WORKS
### 8.1 Conclusion
Digitizing Ayurveda through AyurWellness provides a scalable solution for modern holistic health management.

### 8.2 Future Scope
Machine Learning for pulse analysis, Wearables integration, and Mobile Apps.

---

## REFERENCES
1.  Ministry of AYUSH, "Ayush Grid Project".
2.  AyuRythm: Comprehensive Holistic Wellness App.
3.  "AI and Machine Learning in Ayurveda", ResearchGate.

---

## APPENDIX
*   **Appendix A:** Sample scoring algorithm in `views.py`.
*   **Appendix B:** User dashboard and Dosha quiz screenshots.
*   **Appendix C:** Research documentation on Prakriti analysis.
*   **Appendix D:** Project presentation slide deck.
