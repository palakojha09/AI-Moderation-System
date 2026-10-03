import { useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

const API_URL = "http://127.0.0.1:5000/api";

/* =========================================================
   Helper: normalize student API response
========================================================= */

function normalizeStudentResponse(data) {
  let records = [];

  if (Array.isArray(data)) {
    records = data;
  } else if (Array.isArray(data?.records)) {
    records = data.records;
  } else if (Array.isArray(data?.data)) {
    records = data.data;
  } else if (Array.isArray(data?.subjects)) {
    records = data.subjects;
  }

  return {
    ...data,
    student_id:
      data?.student_id ||
      data?.Student_ID ||
      data?.student ||
      "Unknown",
    records,
  };
}

/* =========================================================
   Main App
========================================================= */

function App() {
  /* =======================================================
     Main dashboard state
  ======================================================= */

  const [summary, setSummary] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  /* =======================================================
     Filter state
  ======================================================= */

  const [studentSearch, setStudentSearch] = useState("");
  const [subjectFilter, setSubjectFilter] = useState("All");
  const [facultyFilter, setFacultyFilter] = useState("All");
  const [directionFilter, setDirectionFilter] = useState("All");
  const [recommendationFilter, setRecommendationFilter] =
    useState("All");

  /* =======================================================
     Student analysis state
  ======================================================= */

  const [studentId, setStudentId] = useState("");
  const [studentData, setStudentData] = useState(null);
  const [studentLoading, setStudentLoading] = useState(false);
  const [studentError, setStudentError] = useState("");

  /* =======================================================
     Faculty analysis state
  ======================================================= */

  const [facultyId, setFacultyId] = useState("");
  const [facultyData, setFacultyData] = useState(null);
  const [facultyLoading, setFacultyLoading] = useState(false);
  const [facultyError, setFacultyError] = useState("");

  /* =======================================================
     Load dashboard data
  ======================================================= */

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [summaryResponse, reviewsResponse] =
          await Promise.all([
            fetch(`${API_URL}/summary`),
            fetch(`${API_URL}/reviews`),
          ]);

        if (!summaryResponse.ok) {
          throw new Error("Could not load summary");
        }

        if (!reviewsResponse.ok) {
          throw new Error("Could not load reviews");
        }

        const summaryData = await summaryResponse.json();
        const reviewsData = await reviewsResponse.json();

        setSummary(summaryData);

        /*
          Backend may return either:
          [
            {...},
            {...}
          ]

          or:

          {
            "reviews": [...]
          }

          Handle both.
        */

        let reviewRecords = [];

        if (Array.isArray(reviewsData)) {
          reviewRecords = reviewsData;
        } else if (Array.isArray(reviewsData?.reviews)) {
          reviewRecords = reviewsData.reviews;
        } else if (Array.isArray(reviewsData?.data)) {
          reviewRecords = reviewsData.data;
        } else if (Array.isArray(reviewsData?.records)) {
          reviewRecords = reviewsData.records;
        }

        setReviews(reviewRecords);
      } catch (err) {
        console.error("Dashboard error:", err);

        setError(
          "Could not connect to the backend. Make sure the Flask API is running."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  /* =======================================================
     Filter options
  ======================================================= */

  const subjects = useMemo(() => {
    return [
      ...new Set(
        reviews
          .map((review) => review.Subject)
          .filter(Boolean)
      ),
    ].sort();
  }, [reviews]);

  const faculties = useMemo(() => {
    return [
      ...new Set(
        reviews
          .map((review) => review.Faculty_ID)
          .filter(Boolean)
      ),
    ].sort();
  }, [reviews]);

  const directions = useMemo(() => {
    return [
      ...new Set(
        reviews
          .map((review) => review.Deviation_Direction)
          .filter(Boolean)
      ),
    ].sort();
  }, [reviews]);

  const recommendations = useMemo(() => {
    return [
      ...new Set(
        reviews
          .map((review) => review.Recommendation)
          .filter(Boolean)
      ),
    ].sort();
  }, [reviews]);

  /* =======================================================
     Filter review cases
  ======================================================= */

  const filteredReviews = useMemo(() => {
    return reviews.filter((review) => {
      const student =
        String(review.Student_ID || "").toLowerCase();

      const matchesStudent = student.includes(
        studentSearch.toLowerCase()
      );

      const matchesSubject =
        subjectFilter === "All" ||
        review.Subject === subjectFilter;

      const matchesFaculty =
        facultyFilter === "All" ||
        review.Faculty_ID === facultyFilter;

      const matchesDirection =
        directionFilter === "All" ||
        review.Deviation_Direction === directionFilter;

      const matchesRecommendation =
        recommendationFilter === "All" ||
        review.Recommendation === recommendationFilter;

      return (
        matchesStudent &&
        matchesSubject &&
        matchesFaculty &&
        matchesDirection &&
        matchesRecommendation
      );
    });
  }, [
    reviews,
    studentSearch,
    subjectFilter,
    facultyFilter,
    directionFilter,
    recommendationFilter,
  ]);

  /* =======================================================
     Reset filters
  ======================================================= */

  function resetFilters() {
    setStudentSearch("");
    setSubjectFilter("All");
    setFacultyFilter("All");
    setDirectionFilter("All");
    setRecommendationFilter("All");
  }

  /* =======================================================
     Student API search
  ======================================================= */

  async function searchStudent() {
    const id = studentId.trim().toUpperCase();

    if (!id) {
      setStudentError("Please enter a Student ID.");
      setStudentData(null);
      return;
    }

    setStudentLoading(true);
    setStudentError("");
    setStudentData(null);

    try {
      const response = await fetch(
        `${API_URL}/students/${id}`
      );

      if (!response.ok) {
        throw new Error("Student not found");
      }

      const data = await response.json();

      console.log("Student API response:", data);

      const normalizedData =
        normalizeStudentResponse(data);

      if (normalizedData.records.length === 0) {
        setStudentError(
          "Student was found, but no subject records were returned."
        );
      }

      setStudentData(normalizedData);
    } catch (err) {
      console.error("Student API error:", err);

      setStudentError(
        "Student not found. Try an ID such as S002."
      );

      setStudentData(null);
    } finally {
      setStudentLoading(false);
    }
  }

  /* =======================================================
     Faculty API search
  ======================================================= */

  async function searchFaculty() {
    const id = facultyId.trim().toUpperCase();

    if (!id) {
      setFacultyError("Please enter a Faculty ID.");
      setFacultyData(null);
      return;
    }

    setFacultyLoading(true);
    setFacultyError("");
    setFacultyData(null);

    try {
      const response = await fetch(
        `${API_URL}/faculty/${id}`
      );

      if (!response.ok) {
        throw new Error("Faculty not found");
      }

      const data = await response.json();

      console.log("Faculty API response:", data);

      setFacultyData(data);
    } catch (err) {
      console.error("Faculty API error:", err);

      setFacultyError(
        "Faculty not found. Try an ID such as F07."
      );

      setFacultyData(null);
    } finally {
      setFacultyLoading(false);
    }
  }

  /* =======================================================
     Loading screen
  ======================================================= */

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <h2>AI Moderation System</h2>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  /* =======================================================
     Error screen
  ======================================================= */

  if (error) {
    return (
      <div className="app">
        <div className="error-box">
          <h2>AI Moderation System</h2>

          <p>{error}</p>

          <p className="hint">
            Backend should be running at
            http://127.0.0.1:5000
          </p>
        </div>
      </div>
    );
  }

  /* =======================================================
     Chart data
  ======================================================= */

  const anomalyChartData = summary
    ? [
        {
          name: "Normal",
          value:
            Number(summary.total_records || 0) -
            Number(summary.anomalies || 0),
        },
        {
          name: "Anomalies",
          value: Number(summary.anomalies || 0),
        },
      ]
    : [];

  const directionChartData = summary
    ? [
        {
          name: "Under-marking",
          value: Number(summary.under_marking || 0),
        },
        {
          name: "Over-marking",
          value: Number(summary.over_marking || 0),
        },
      ]
    : [];

  const recommendationChartData = [
    {
      name: "Strong Review",
      value: reviews.filter(
        (review) =>
          review.Recommendation ===
          "Strong Review Recommended"
      ).length,
    },
    {
      name: "Review",
      value: reviews.filter(
        (review) =>
          review.Recommendation ===
          "Review Recommended"
      ).length,
    },
  ];

  /* =======================================================
     Main UI
  ======================================================= */

  return (
    <div className="app">

      {/* =================================================
          Header
      ================================================= */}

      <header className="header">

        <div>
          <h1>AI Moderation System</h1>

          <p>
            AI-assisted detection of abnormal marks deviation
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          System Connected
        </div>

      </header>

      {/* =================================================
          Dashboard
      ================================================= */}

      <main className="dashboard">

        {/* Welcome */}

        <section className="welcome">

          <h2>Moderation Dashboard</h2>

          <p>
            Identify unusual marks deviations and prioritize
            cases for human review.
          </p>

        </section>

        {/* =================================================
            Summary Cards
        ================================================= */}

        <section className="stats-grid">

          <StatCard
            title="Total Records"
            value={summary.total_records}
            description="Marks records analyzed"
          />

          <StatCard
            title="Detected Anomalies"
            value={summary.anomalies}
            description="Records with injected anomalies"
            type="warning"
          />

          <StatCard
            title="Human Review Cases"
            value={summary.review_cases}
            description="Cases requiring review"
            type="danger"
          />

          <StatCard
            title="Under-marking"
            value={summary.under_marking}
            description="Potential under-marking cases"
            type="info"
          />

          <StatCard
            title="Over-marking"
            value={summary.over_marking}
            description="Potential over-marking cases"
            type="success"
          />

        </section>

        {/* =================================================
            Review Cases
        ================================================= */}

        <section className="panel">

          <div className="panel-header">

            <div>

              <h2>
                Cases Requiring Human Review
              </h2>

              <p>
                AI-generated recommendations for
                faculty/moderation review.
              </p>

            </div>

            <span className="count-badge">
              {filteredReviews.length} Cases
            </span>

          </div>

          {/* Filters */}

          <div className="filters">

            <div className="filter-group search-group">

              <label htmlFor="student-search">
                Search Student
              </label>

              <input
                id="student-search"
                type="text"
                placeholder="e.g. S002"
                value={studentSearch}
                onChange={(event) =>
                  setStudentSearch(event.target.value)
                }
              />

            </div>

            <div className="filter-group">

              <label htmlFor="subject-filter">
                Subject
              </label>

              <select
                id="subject-filter"
                value={subjectFilter}
                onChange={(event) =>
                  setSubjectFilter(event.target.value)
                }
              >

                <option value="All">
                  All Subjects
                </option>

                {subjects.map((subject) => (
                  <option
                    key={subject}
                    value={subject}
                  >
                    {subject}
                  </option>
                ))}

              </select>

            </div>

            <div className="filter-group">

              <label htmlFor="faculty-filter">
                Faculty
              </label>

              <select
                id="faculty-filter"
                value={facultyFilter}
                onChange={(event) =>
                  setFacultyFilter(event.target.value)
                }
              >

                <option value="All">
                  All Faculty
                </option>

                {faculties.map((faculty) => (
                  <option
                    key={faculty}
                    value={faculty}
                  >
                    {faculty}
                  </option>
                ))}

              </select>

            </div>

            <div className="filter-group">

              <label htmlFor="direction-filter">
                Direction
              </label>

              <select
                id="direction-filter"
                value={directionFilter}
                onChange={(event) =>
                  setDirectionFilter(event.target.value)
                }
              >

                <option value="All">
                  All Directions
                </option>

                {directions.map((direction) => (
                  <option
                    key={direction}
                    value={direction}
                  >
                    {direction}
                  </option>
                ))}

              </select>

            </div>

            <div className="filter-group">

              <label htmlFor="recommendation-filter">
                Recommendation
              </label>

              <select
                id="recommendation-filter"
                value={recommendationFilter}
                onChange={(event) =>
                  setRecommendationFilter(
                    event.target.value
                  )
                }
              >

                <option value="All">
                  All Recommendations
                </option>

                {recommendations.map(
                  (recommendation) => (
                    <option
                      key={recommendation}
                      value={recommendation}
                    >
                      {recommendation}
                    </option>
                  )
                )}

              </select>

            </div>

            <button
              type="button"
              className="reset-button"
              onClick={resetFilters}
            >
              Reset Filters
            </button>

          </div>

          {/* Filter information */}

          <div className="filter-info">

            Showing{" "}
            <strong>
              {Math.min(filteredReviews.length, 20)}
            </strong>{" "}
            of{" "}
            <strong>
              {filteredReviews.length}
            </strong>{" "}
            matching cases

          </div>

          {/* Review table */}

          <div className="table-container">

            <table>

              <thead>

                <tr>
                  <th>Student</th>
                  <th>Subject</th>
                  <th>Faculty</th>
                  <th>Given</th>
                  <th>Expected</th>
                  <th>Deviation</th>
                  <th>Direction</th>
                  <th>Recommendation</th>
                </tr>

              </thead>

              <tbody>

                {filteredReviews
                  .slice(0, 20)
                  .map((review) => {

                    const given = Number(
                      review.Given_Marks || 0
                    );

                    const expected = Number(
                      review.Expected_Marks || 0
                    );

                    const deviation = Number(
                      review.Deviation || 0
                    );

                    return (
                      <tr
                        key={`${review.Student_ID}-${review.Subject}`}
                      >

                        <td>
                          {review.Student_ID}
                        </td>

                        <td>
                          {review.Subject}
                        </td>

                        <td>
                          {review.Faculty_ID}
                        </td>

                        <td>
                          {given.toFixed(1)}
                        </td>

                        <td>
                          {expected.toFixed(1)}
                        </td>

                        <td
                          className={
                            deviation < 0
                              ? "negative"
                              : "positive"
                          }
                        >
                          {deviation > 0 ? "+" : ""}
                          {deviation.toFixed(1)}
                        </td>

                        <td>

                          <span
                            className={`direction ${
                              review.Deviation_Direction ===
                              "Potential Under-marking"
                                ? "under"
                                : review.Deviation_Direction ===
                                    "Potential Over-marking"
                                  ? "over"
                                  : "normal"
                            }`}
                          >
                            {review.Deviation_Direction}
                          </span>

                        </td>

                        <td>

                          <span
                            className={`recommendation ${
                              review.Recommendation ===
                              "Strong Review Recommended"
                                ? "strong"
                                : "review"
                            }`}
                          >
                            {review.Recommendation}
                          </span>

                        </td>

                      </tr>
                    );
                  })}

                {filteredReviews.length === 0 && (

                  <tr>

                    <td
                      colSpan="8"
                      className="no-results"
                    >
                      No review cases match the selected
                      filters.
                    </td>

                  </tr>

                )}

              </tbody>

            </table>

          </div>

          {filteredReviews.length > 20 && (

            <p className="table-note">

              Showing the first 20 of{" "}
              {filteredReviews.length} matching cases.

            </p>

          )}

        </section>

        {/* =================================================
            Analytics
        ================================================= */}

        <section className="analytics">

          <div className="analytics-header">

            <h2>
              Analytics Overview
            </h2>

            <p>
              Visual summary of anomaly detection and
              moderation recommendations.
            </p>

          </div>

          <div className="charts-grid">

            {/* Anomaly Overview */}

            <div className="chart-card">

              <h3>
                Anomaly Overview
              </h3>

              <ResponsiveContainer
                width="100%"
                height={280}
              >

                <BarChart
                  data={anomalyChartData}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    dataKey="name"
                  />

                  <YAxis />

                  <Tooltip />

                  <Bar
                    dataKey="value"
                    fill="#3b82f6"
                  />

                </BarChart>

              </ResponsiveContainer>

            </div>

            {/* Marking Direction */}

            <div className="chart-card">

              <h3>
                Marking Direction
              </h3>

              <ResponsiveContainer
                width="100%"
                height={280}
              >

                <PieChart>

                  <Pie
                    data={directionChartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    label
                  >

                    <Cell fill="#8b5cf6" />
                    <Cell fill="#10b981" />

                  </Pie>

                  <Tooltip />

                  <Legend />

                </PieChart>

              </ResponsiveContainer>

            </div>

            {/* Review Recommendations */}

            <div className="chart-card">

              <h3>
                Review Recommendations
              </h3>

              <ResponsiveContainer
                width="100%"
                height={280}
              >

                <BarChart
                  data={recommendationChartData}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    dataKey="name"
                  />

                  <YAxis />

                  <Tooltip />

                  <Bar
                    dataKey="value"
                    fill="#ef4444"
                  />

                </BarChart>

              </ResponsiveContainer>

            </div>

          </div>

        </section>

        {/* =================================================
            Student & Faculty Analysis
        ================================================= */}

        <section className="analysis-section">

          <div className="analysis-header">

            <h2>
              Student & Faculty Analysis
            </h2>

            <p>
              Inspect individual student records and
              faculty-level marking patterns.
            </p>

          </div>

          <div className="analysis-grid">

            {/* =================================================
                Student Analysis
            ================================================= */}

            <div className="analysis-card">

              <h3>
                Student Analysis
              </h3>

              <p className="analysis-description">
                Enter a Student ID to view subject-wise
                marks and deviations.
              </p>

              <div className="analysis-search">

                <input
                  type="text"
                  placeholder="e.g. S002"
                  value={studentId}
                  onChange={(event) =>
                    setStudentId(event.target.value)
                  }
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      searchStudent();
                    }
                  }}
                />

                <button
                  type="button"
                  onClick={searchStudent}
                >
                  Search
                </button>

              </div>

              {studentLoading && (
                <p className="analysis-status">
                  Loading student data...
                </p>
              )}

              {studentError && (
                <p className="analysis-error">
                  {studentError}
                </p>
              )}

              {studentData && (
                <div className="analysis-result">

                  <div className="result-title">

                    <strong>
                      Student{" "}
                      {studentData.student_id}
                    </strong>

                  </div>

                  {studentData.records &&
                  studentData.records.length > 0 ? (
                    <div className="student-table-container">

                      <table className="student-table">

                        <thead>

                          <tr>
                            <th>Subject</th>
                            <th>Given</th>
                            <th>Expected</th>
                            <th>Deviation</th>
                            <th>Review</th>
                          </tr>

                        </thead>

                        <tbody>

                          {(studentData.records || []).map(
                            (record, index) => {

                              const given = Number(
                                record.Given_Marks ??
                                record.given_marks ??
                                0
                              );

                              const expected = Number(
                                record.Expected_Marks ??
                                record.expected_marks ??
                                0
                              );

                              const deviation =
                                Number(
                                  record.Deviation ??
                                  record.deviation ??
                                  0
                                );

                              const requiresReview =
                                Boolean(
                                  record.Requires_Human_Review ??
                                  record.requires_human_review ??
                                  false
                                );

                              return (
                                <tr
                                  key={`${record.Subject || "subject"}-${index}`}
                                >

                                  <td>
                                    {record.Subject ||
                                      record.subject ||
                                      "N/A"}
                                  </td>

                                  <td>
                                    {given.toFixed(1)}
                                  </td>

                                  <td>
                                    {expected.toFixed(1)}
                                  </td>

                                  <td
                                    className={
                                      deviation < 0
                                        ? "negative"
                                        : "positive"
                                    }
                                  >
                                    {deviation > 0
                                      ? "+"
                                      : ""}
                                    {deviation.toFixed(1)}
                                  </td>

                                  <td>

                                    {requiresReview ? (
                                      <span className="review-yes">
                                        Review
                                      </span>
                                    ) : (
                                      <span className="review-no">
                                        Normal
                                      </span>
                                    )}

                                  </td>

                                </tr>
                              );
                            }
                          )}

                        </tbody>

                      </table>

                    </div>
                  ) : (
                    <p className="analysis-status">
                      No subject records available for this
                      student.
                    </p>
                  )}

                </div>
              )}

            </div>

            {/* =================================================
                Faculty Analysis
            ================================================= */}

            <div className="analysis-card">

              <h3>
                Faculty Analysis
              </h3>

              <p className="analysis-description">
                Enter a Faculty ID to examine marking
                statistics and review cases.
              </p>

              <div className="analysis-search">

                <input
                  type="text"
                  placeholder="e.g. F07"
                  value={facultyId}
                  onChange={(event) =>
                    setFacultyId(event.target.value)
                  }
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      searchFaculty();
                    }
                  }}
                />

                <button
                  type="button"
                  onClick={searchFaculty}
                >
                  Search
                </button>

              </div>

              {facultyLoading && (
                <p className="analysis-status">
                  Loading faculty data...
                </p>
              )}

              {facultyError && (
                <p className="analysis-error">
                  {facultyError}
                </p>
              )}

              {facultyData && (
                <div className="faculty-result">

                  <div className="result-title">

                    <strong>
                      Faculty{" "}
                      {facultyData.faculty_id ||
                        facultyData.Faculty_ID ||
                        facultyId.toUpperCase()}
                    </strong>

                  </div>

                  <div className="faculty-stats">

                    <div className="faculty-stat">
                      <span>Total Records</span>
                      <strong>
                        {facultyData.total_records ?? 0}
                      </strong>
                    </div>

                    <div className="faculty-stat">
                      <span>Average Given</span>
                      <strong>
                        {Number(
                          facultyData.average_given_marks ??
                          0
                        ).toFixed(2)}
                      </strong>
                    </div>

                    <div className="faculty-stat">
                      <span>Average Expected</span>
                      <strong>
                        {Number(
                          facultyData.average_expected_marks ??
                          0
                        ).toFixed(2)}
                      </strong>
                    </div>

                    <div className="faculty-stat">
                      <span>Average Deviation</span>
                      <strong>
                        {Number(
                          facultyData.average_deviation ??
                          0
                        ) > 0
                          ? "+"
                          : ""}
                        {Number(
                          facultyData.average_deviation ??
                          0
                        ).toFixed(2)}
                      </strong>
                    </div>

                    <div className="faculty-stat">
                      <span>Review Cases</span>
                      <strong>
                        {facultyData.review_cases ?? 0}
                      </strong>
                    </div>

                    <div className="faculty-stat">
                      <span>Under-marking</span>
                      <strong>
                        {facultyData.under_marking ?? 0}
                      </strong>
                    </div>

                    <div className="faculty-stat">
                      <span>Over-marking</span>
                      <strong>
                        {facultyData.over_marking ?? 0}
                      </strong>
                    </div>

                  </div>

                </div>
              )}

            </div>

          </div>

        </section>

        {/* =================================================
            Detection Methodology
        ================================================= */}

        <section className="methodology">

          <h2>
            Detection Methodology
          </h2>

          <div className="method-grid">

            <MethodCard
              title="Z-Score"
              description="Identifies marks with statistically unusual deviation from the overall distribution."
            />

            <MethodCard
              title="IQR"
              description="Detects observations outside the interquartile range based on deviation."
            />

            <MethodCard
              title="Isolation Forest"
              description="Uses machine learning to identify records that behave differently from normal patterns."
            />

            <MethodCard
              title="Human Review"
              description="The system recommends cases for review. Final moderation decisions remain with human experts."
            />

          </div>

        </section>

      </main>

    </div>
  );
}

/* =========================================================
   Stat Card
========================================================= */

function StatCard({
  title,
  value,
  description,
  type = "",
}) {
  return (
    <div className={`stat-card ${type}`}>

      <p className="stat-title">
        {title}
      </p>

      <h3>
        {value}
      </h3>

      <p className="stat-description">
        {description}
      </p>

    </div>
  );
}

/* =========================================================
   Methodology Card
========================================================= */

function MethodCard({
  title,
  description,
}) {
  return (
    <div className="method-card">

      <h3>
        {title}
      </h3>

      <p>
        {description}
      </p>

    </div>
  );
}

export default App;