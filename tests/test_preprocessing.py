import pandas as pd


RAW_FILE = "data/raw/synthetic_marks.csv"
PROCESSED_FILE = "data/processed/processed_marks.csv"


def test_raw_dataset_exists():
    df = pd.read_csv(RAW_FILE)

    assert len(df) == 2000
    assert df["Student_ID"].nunique() == 500
    assert df["Subject"].nunique() == 4
    assert df["Faculty_ID"].nunique() == 8


def test_raw_dataset_has_no_missing_values():
    df = pd.read_csv(RAW_FILE)

    assert df.isnull().sum().sum() == 0


def test_marks_are_valid():
    df = pd.read_csv(RAW_FILE)

    assert df["Given_Marks"].between(0, 100).all()
    assert df["Internal_Marks"].between(0, 30).all()
    assert df["Previous_Score"].between(0, 100).all()
    assert df["Attendance"].between(0, 100).all()


def test_processed_dataset_exists():
    df = pd.read_csv(PROCESSED_FILE)

    assert len(df) == 2000


def test_expected_marks_are_valid():
    df = pd.read_csv(PROCESSED_FILE)

    assert df["Expected_Marks"].between(0, 100).all()


def test_deviation_is_calculated():
    df = pd.read_csv(PROCESSED_FILE)

    calculated_deviation = (
        df["Given_Marks"] - df["Expected_Marks"]
    )

    assert (
        abs(calculated_deviation - df["Deviation"]) < 0.01
    ).all()