# AI Moderation Recommendation System

An AI-powered academic assessment analysis system that identifies unusual student score patterns using statistical anomaly detection and machine learning, and recommends records for human moderation.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Scikit-learn](https://img.shields.io/badge/ML-Scikit--learn-orange)](https://scikit-learn.org/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Backend-Flask-black)](https://flask.palletsprojects.com/)

## Repository

**GitHub:** https://github.com/palakojha09/AI-Moderation-System  
**Development branch:** `feature/oulad-integration`

## 1. Project Overview

The AI Moderation Recommendation System analyzes student assessment records to identify unusual score patterns that may require further investigation.

Educational institutions handle large volumes of assessment records. Manually identifying unusual scoring patterns can be time-consuming. This project combines statistical methods and unsupervised machine learning to help moderators prioritize records for human review.

The system does not automatically modify marks or determine whether unfair marking has occurred. It provides data-driven recommendations for human moderators.

## 2. Problem Statement

Manual examination of large academic assessment datasets makes it difficult to consistently identify unusual scoring patterns.

The project aims to:
- Process and analyze student assessment records.
- Identify unusual scores using statistical techniques.
- Detect unusual patterns using an unsupervised machine-learning model.
- Combine detection results into moderation recommendations.
- Visualize results through an interactive dashboard.

## 3. Objectives

- Integrate and preprocess academic assessment data.
- Engineer useful statistical features.
- Implement IQR, robust Z-score and percentile-based anomaly detection.
- Implement Isolation Forest without deviation-based input features.
- Combine detection outputs through a moderation engine.
- Assign review recommendations and priorities.
- Provide searchable records and analytics through a web dashboard.

## 4. Dataset — OULAD

This project uses the **Open University Learning Analytics Dataset (OULAD)**.

OULAD contains anonymized information about students, courses, assessments and interactions with the Virtual Learning Environment.

### Dataset links

- [Official Open University OULAD page](https://analyse.kmi.open.ac.uk/open_dataset)
- [UCI Machine Learning Repository — OULAD](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset)
- [OULAD dataset DOI](https://doi.org/10.24432/C5KK69)

### Dataset files

| File | Description |
|---|---|
| `studentAssessment.csv` | Student assessment scores |
| `assessments.csv` | Assessment metadata |
| `studentInfo.csv` | Student and course information |
| `courses.csv` | Course module information |
| `studentRegistration.csv` | Student registration details |
| `studentVle.csv` | Student interaction records |
| `vle.csv` | Virtual Learning Environment metadata |

The current score-detection pipeline primarily uses assessment records and relevant student/course information. The large `studentVle.csv` interaction log is not used in the current detection pipeline.

### Assessment categories

| Code | Description |
|---|---|
| TMA | Tutor Marked Assessment |
| CMA | Computer Marked Assessment |
| Exam | Formal examination |

Module codes such as AAA, BBB, CCC, DDD, EEE, FFF and GGG are anonymized identifiers.

### Dataset processing results

| Stage | Records |
|---|---:|
| Merged assessment records | 173,912 |
| Missing score records | 173 |
| Valid assessment records | 173,739 |
| Duplicate records after cleaning | 0 |

**Note:** The raw dataset is not included in this repository. Download it from the official source and place the extracted CSV files in `data/raw/OULAD/`.

## 5. Technology Stack

### Data Processing and Machine Learning
- Python
- Pandas
- NumPy
- Scikit-learn

### Statistical Analysis
- IQR
- Robust Z-score
- Percentile-based detection

### Machine Learning
- Isolation Forest
- StandardScaler
- SimpleImputer
- OneHotEncoder
- ColumnTransformer
- Scikit-learn Pipeline

### Backend
- Flask
- Flask-CORS
- REST APIs

### Frontend
- React
- JavaScript
- CSS
- Recharts
- Vite

### Development Tools
- Git
- GitHub
- Visual Studio Code
- PowerShell

## 6. System Architecture

```text
                 OULAD Dataset
                       |
                       v
             Data Merging and Cleaning
                       |
                       v
                Preprocessing
                       |
                       v
               Feature Engineering
                       |
              +--------+--------+
              |                 |
              v                 v
       Statistical          Isolation Forest
        Detection              Detection
              |                 |
              +--------+--------+
                       |
                       v
                Moderation Engine
                       |
                       v
                  Flask API
                       |
                       v
                React Dashboard
                       |
                       v
              Human Review Workflow
```

## 7. Methodology

### 7.1 Data Merging and Preprocessing

The raw OULAD CSV files are merged using student, assessment, module and presentation identifiers.

Preprocessing includes:
- Missing-value checks.
- Duplicate checks.
- Score validation.
- Separation of records with missing scores.
- Preparation of cleaned assessment records.

Output: `data/processed/oulad_cleaned_assessments.csv`

### 7.2 Feature Engineering

Assessment-level statistical features are generated, including:
- Assessment mean and median.
- Standard deviation.
- First and third quartiles.
- Interquartile range.
- Median absolute deviation.
- Score deviation.
- Absolute deviation.
- Robust Z-score.
- Score percentile.

Output: `data/processed/oulad_featured_assessments.csv`

### 7.3 Statistical Anomaly Detection

The statistical detection module uses three indicators:
1. IQR-based detection.
2. Robust Z-score detection.
3. Percentile-based detection.

A record is classified as a statistical anomaly when at least two of the three indicators flag it.

Output: `data/processed/oulad_statistical_results.csv`

**Result:** 2,067 statistical anomalies.

### 7.4 Isolation Forest

Isolation Forest is an unsupervised machine-learning algorithm that identifies observations that can be isolated more easily through random partitioning.

Following faculty feedback, the updated Isolation Forest does not use deviation-based features as model inputs.

**Numerical features:**
- `score`
- `weight`
- `num_of_prev_attempts`
- `studied_credits`

**Categorical feature:**
- `code_module`

Preprocessing:
- Median imputation for numerical features.
- StandardScaler for numerical features.
- Most-frequent imputation for categorical features.
- OneHotEncoder for module codes.

Model configuration:

| Parameter | Value |
|---|---:|
| Number of estimators | 200 |
| Contamination | 0.02 |
| Random state | 42 |
| Jobs | -1 |

Separate models are trained for TMA, CMA and Exam to account for differences in assessment characteristics.

Output: `data/processed/oulad_isolation_forest_results.csv`

**Result:** 3,476 Isolation Forest anomalies.

The 2% contamination setting is a model configuration, not a verified real-world anomaly prevalence.

### 7.5 Moderation Engine

The moderation engine combines statistical and Isolation Forest outputs.

| Statistical Detection | Isolation Forest | Recommendation | Priority |
|---|---|---|---|
| No | No | No Significant Anomaly | Not Required |
| Yes | No | Review Recommended | Medium |
| No | Yes | Review Recommended | Medium |
| Yes | Yes | Strong Review Recommended | High |

Output: `data/processed/oulad_final_moderation_results.csv`

### 7.6 Evaluation

The evaluation module generates:
- Dataset summary.
- Detector counts and agreement.
- Review rates by assessment type.
- Review rates by module.
- Recommendation distribution.
- Review direction.
- Data-quality checks.

Generated files:
- `data/processed/oulad_evaluation_report.txt`
- `data/processed/oulad_evaluation_summary.csv`

## 8. Final Results

The latest generated results are:

| Metric | Result |
|---|---:|
| Total assessment records | 173,739 |
| Statistical anomalies | 2,067 |
| Isolation Forest anomalies | 3,476 |
| Human review recommendations | 5,181 |
| Overall review rate | 2.98% |
| Strong review / High priority | 362 |
| Review recommended / Medium priority | 4,819 |
| No significant anomaly | 168,558 |

### Detector agreement

| Detection source | Records |
|---|---:|
| Both methods | 362 |
| Statistical detection only | 1,705 |
| Isolation Forest only | 3,114 |
| No detection | 168,558 |

### Review rate by assessment type

| Assessment type | Total records | Review cases | Review rate |
|---|---:|---:|---:|
| CMA | 70,527 | 1,920 | 2.72% |
| Exam | 4,959 | 106 | 2.14% |
| TMA | 98,253 | 3,155 | 3.21% |

### Data quality
- Duplicate student-assessment pairs: 0
- Missing student IDs: 0
- Missing assessment IDs: 0

## 9. Dashboard Features

The React dashboard provides:
- Dataset connection status.
- Total assessment record count.
- Statistical anomaly count.
- Isolation Forest anomaly count.
- Human review and high-priority case counts.
- Search by student ID.
- Filters by module, assessment type and review priority.
- Review records table.
- Detection method comparison chart.
- Recommendation distribution chart.
- Review cases by assessment type.
- Review cases by module.
- Methodology and limitations information.

## 10. Project Structure

```text
AI-Moderation-System/
├── backend/
│   ├── app.py
│   └── app_synthetic_backup.py
├── data/
│   ├── raw/
│   │   └── OULAD/
│   └── processed/
├── preprocessing/
│   ├── merge_dataset.py
│   ├── preprocess_data.py
│   └── feature_engineering.py
├── ml_model/
│   ├── statistical_detection.py
│   ├── isolation_forest.py
│   ├── oulad_moderation_engine.py
│   └── oulad_evaluation.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── tests/
├── .gitignore
└── README.md
```

## 11. Installation and Setup

### Prerequisites
- Python 3.11 or later.
- Node.js and npm.
- Git.
- Visual Studio Code (recommended).

### Step 1 — Clone the repository

```bash
git clone https://github.com/palakojha09/AI-Moderation-System.git
cd AI-Moderation-System
```

### Step 2 — Create and activate Python environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3 — Install Python dependencies

```powershell
pip install -r requirements.txt
```

### Step 4 — Download the OULAD dataset

Download the dataset from:

https://analyse.kmi.open.ac.uk/open_dataset

Extract the CSV files into:

```text
data/raw/OULAD/
```

Ensure the required files include:
- `studentAssessment.csv`
- `assessments.csv`
- `studentInfo.csv`
- `courses.csv`
- `studentRegistration.csv`

### Step 5 — Install frontend dependencies

```powershell
cd frontend
npm install
```

## 12. Running the Project

Run the backend and frontend in separate terminals.

### Terminal 1 — Flask backend

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m backend.app
```

Backend URL: http://127.0.0.1:5000

### Terminal 2 — React frontend

```powershell
cd frontend
npm run dev
```

Frontend URL: http://localhost:5173

Keep both terminals running while using the dashboard.

## 13. Regenerating the Data Pipeline

If processed outputs need to be rebuilt, execute the following commands from the project root in order:

```powershell
python -m preprocessing.merge_dataset
python -m preprocessing.preprocess_data
python -m preprocessing.feature_engineering
python -m ml_model.statistical_detection
python -m ml_model.isolation_forest
python -m ml_model.oulad_moderation_engine
python -m ml_model.oulad_evaluation
```

Restart the Flask backend after regenerating moderation results.

## 14. Backend API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Backend health check |
| GET | `/api/summary` | Overall dataset and detection statistics |
| GET | `/api/reviews` | Human-review records, with optional filters |
| GET | `/api/students/<student_id>` | Student-level assessment records |
| GET | `/api/assessments/<assessment_id>` | Assessment-level details |
| GET | `/api/analytics` | Assessment-type and module analytics |

## 15. Evaluation Limitations

OULAD does not contain verified ground-truth labels for unfair marking. Therefore, accuracy, precision, recall and F1-score are not reported as real-world unfair-marking detection metrics.

The system identifies unusual score patterns and recommends records for human review. An anomaly does not necessarily indicate unfair marking, an error or misconduct.

The final moderation decision must be made by an authorized human moderator after examining the relevant context.

## 16. Future Enhancements

- Add more assessment and student-context features.
- Introduce moderator feedback and review outcomes.
- Evaluate models using a verified, appropriately labelled moderation dataset.
- Add explainability for individual anomaly recommendations.
- Improve dashboard filtering and reporting.
- Add exportable moderation reports.
- Explore temporal and course-level performance patterns.

## 17. Dataset Citation

Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2015). Open University Learning Analytics Dataset. UCI Machine Learning Repository.

https://doi.org/10.24432/C5KK69

Dataset license: Creative Commons Attribution 4.0 International (CC BY 4.0).

## 18. Acknowledgements

We acknowledge The Open University and the OULAD dataset creators for making the educational dataset publicly available for research and learning analytics.

---

**AI Moderation Recommendation System**  
A data-driven approach to identifying unusual academic assessment patterns and supporting human moderation.
