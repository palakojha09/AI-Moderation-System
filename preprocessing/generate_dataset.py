import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42
NUM_STUDENTS = 500

SUBJECTS = [
    "Machine Learning",
    "Computer Networks",
    "Compiler Design",
    "Software Engineering",
]

FACULTIES = [
    "F01",
    "F02",
    "F03",
    "F04",
    "F05",
    "F06",
    "F07",
    "F08",
]

MAX_MARKS = 100

rng = np.random.default_rng(RANDOM_SEED)


# ============================================================
# CREATE STUDENT INFORMATION
# ============================================================

students = []

for i in range(1, NUM_STUDENTS + 1):
    students.append(
        {
            "Student_ID": f"S{i:03d}",
            "Previous_Score": round(
                np.clip(rng.normal(70, 12), 35, 98), 1
            ),
            "Attendance": round(
                np.clip(rng.normal(82, 10), 50, 100), 1
            ),
            "Internal_Marks": round(
                np.clip(rng.normal(22, 4), 10, 30), 1
            ),
        }
    )

student_df = pd.DataFrame(students)


# ============================================================
# GENERATE EVALUATION RECORDS
# ============================================================

records = []

for _, student in student_df.iterrows():

    for subject in SUBJECTS:

        faculty_id = rng.choice(FACULTIES)

        # ----------------------------------------------------
        # Estimate underlying student performance
        # ----------------------------------------------------

        academic_signal = (
            0.45 * student["Previous_Score"]
            + 0.25 * (student["Internal_Marks"] / 30 * 100)
            + 0.20 * student["Attendance"]
            + 0.10 * rng.normal(70, 8)
        )

        expected_marks = np.clip(
            academic_signal,
            20,
            95,
        )

        # ----------------------------------------------------
        # Faculty marking variation
        # ----------------------------------------------------

        faculty_bias = {
            "F01": 0,
            "F02": -2,
            "F03": 1,
            "F04": -1,
            "F05": 2,
            "F06": 0,
            "F07": -3,
            "F08": 1,
        }

        normal_noise = rng.normal(0, 5)

        given_marks = expected_marks + faculty_bias[faculty_id] + normal_noise

        injected_anomaly = False
        anomaly_type = "No_Anomaly"

        # ----------------------------------------------------
        # Inject controlled anomalies
        # Approximately 5% of evaluations
        # ----------------------------------------------------

        if rng.random() < 0.05:

            injected_anomaly = True

            anomaly_type = rng.choice(
                [
                    "Severe_Undermarking",
                    "Severe_Overmarking",
                ]
            )

            if anomaly_type == "Severe_Undermarking":
                given_marks = expected_marks - rng.uniform(20, 35)

            else:
                given_marks = expected_marks + rng.uniform(20, 35)

        # ----------------------------------------------------
        # Keep marks within valid range
        # ----------------------------------------------------

        given_marks = np.clip(
            given_marks,
            0,
            MAX_MARKS,
        )

        records.append(
            {
                "Student_ID": student["Student_ID"],
                "Subject": subject,
                "Faculty_ID": faculty_id,
                "Internal_Marks": student["Internal_Marks"],
                "Previous_Score": student["Previous_Score"],
                "Attendance": student["Attendance"],
                "Given_Marks": round(given_marks, 1),
                "Max_Marks": MAX_MARKS,
                "Injected_Anomaly": injected_anomaly,
                "Anomaly_Type": anomaly_type,
            }
        )


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(records)


# ============================================================
# SAVE DATASET
# ============================================================

output_directory = Path("data/raw")
output_directory.mkdir(parents=True, exist_ok=True)

output_file = output_directory / "synthetic_marks.csv"

df.to_csv(output_file, index=False)


# ============================================================
# DISPLAY SUMMARY
# ============================================================

print("\nDataset created successfully!")
print(f"File: {output_file}")
print(f"Total evaluations: {len(df)}")
print(f"Total students: {df['Student_ID'].nunique()}")
print(f"Total subjects: {df['Subject'].nunique()}")
print(f"Total faculty: {df['Faculty_ID'].nunique()}")

print("\nInjected anomaly count:")
print(df["Injected_Anomaly"].value_counts())

print("\nAnomaly types:")
print(df["Anomaly_Type"].value_counts())

print("\nFirst 10 records:")
print(df.head(10))