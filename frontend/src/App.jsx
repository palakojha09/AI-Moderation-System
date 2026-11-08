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
const COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b"];

function unwrapList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.value)) return data.value;
  if (Array.isArray(data?.records)) return data.records;
  if (Array.isArray(data?.reviews)) return data.reviews;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function StatCard({ title, value, description, type = "" }) {
  return (
    <div className={`stat-card ${type}`}>
      <p className="stat-title">{title}</p>
      <h3>{Number(value ?? 0).toLocaleString("en-IN")}</h3>
      <p className="stat-description">{description}</p>
    </div>
  );
}

function App() {
  const [summary, setSummary] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [analytics, setAnalytics] = useState({
    assessment_analysis: [],
    module_analysis: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [studentSearch, setStudentSearch] = useState("");
  const [moduleFilter, setModuleFilter] = useState("All");
  const [typeFilter, setTypeFilter] = useState("All");
  const [priorityFilter, setPriorityFilter] = useState("All");

  const [studentId, setStudentId] = useState("");
  const [studentData, setStudentData] = useState(null);
  const [studentLoading, setStudentLoading] = useState(false);
  const [studentError, setStudentError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [summaryResponse, reviewsResponse, analyticsResponse] =
          await Promise.all([
            fetch(`${API_URL}/summary`),
            fetch(`${API_URL}/reviews`),
            fetch(`${API_URL}/analytics`),
          ]);

        if (!summaryResponse.ok || !reviewsResponse.ok || !analyticsResponse.ok) {
          throw new Error("One or more dashboard API requests failed.");
        }

        const [summaryData, reviewsData, analyticsData] = await Promise.all([
          summaryResponse.json(),
          reviewsResponse.json(),
          analyticsResponse.json(),
        ]);

        if (!active) return;

        setSummary(summaryData);
        setReviews(unwrapList(reviewsData));
        setAnalytics({
          assessment_analysis: analyticsData?.assessment_analysis ?? [],
          module_analysis: analyticsData?.module_analysis ?? [],
        });
      } catch (err) {
        console.error("Dashboard loading error:", err);
        if (active) {
          setError(
            "Could not load OULAD dashboard data. Check that the Flask backend is running at http://127.0.0.1:5000."
          );
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    loadDashboard();
    return () => {
      active = false;
    };
  }, []);

  const modules = useMemo(
    () => [...new Set(reviews.map((r) => r.code_module).filter(Boolean))].sort(),
    [reviews]
  );

  const assessmentTypes = useMemo(
    () =>
      [...new Set(reviews.map((r) => r.assessment_type).filter(Boolean))].sort(),
    [reviews]
  );

  const priorities = useMemo(
    () => [...new Set(reviews.map((r) => r.Review_Priority).filter(Boolean))].sort(),
    [reviews]
  );

  const filteredReviews = useMemo(() => {
    const query = studentSearch.trim().toLowerCase();

    return reviews.filter((record) => {
      const matchesStudent =
        !query || String(record.id_student ?? "").toLowerCase().includes(query);
      const matchesModule =
        moduleFilter === "All" || record.code_module === moduleFilter;
      const matchesType =
        typeFilter === "All" || record.assessment_type === typeFilter;
      const matchesPriority =
        priorityFilter === "All" || record.Review_Priority === priorityFilter;

      return matchesStudent && matchesModule && matchesType && matchesPriority;
    });
  }, [reviews, studentSearch, moduleFilter, typeFilter, priorityFilter]);

  function resetFilters() {
    setStudentSearch("");
    setModuleFilter("All");
    setTypeFilter("All");
    setPriorityFilter("All");
  }

  async function searchStudent() {
    const id = studentId.trim();

    if (!/^\d+$/.test(id)) {
      setStudentError("Enter a valid numeric OULAD student ID.");
      setStudentData(null);
      return;
    }

    setStudentLoading(true);
    setStudentError("");
    setStudentData(null);

    try {
      const response = await fetch(`${API_URL}/students/${encodeURIComponent(id)}`);
      if (!response.ok) throw new Error("Student not found");

      const data = await response.json();
      const records = unwrapList(data);

      if (records.length === 0) {
        setStudentError("No assessment records were returned for this student.");
      } else {
        setStudentData({ student_id: id, records });
      }
    } catch (err) {
      console.error("Student lookup error:", err);
      setStudentError("Student not found or the API request failed. Check the ID and try again.");
    } finally {
      setStudentLoading(false);
    }
  }

  const detectionChartData = summary
    ? [
        { name: "Statistical", value: Number(summary.statistical_anomalies ?? 0) },
        { name: "Isolation Forest", value: Number(summary.isolation_forest_anomalies ?? 0) },
      ]
    : [];

  const recommendationChartData = summary
    ? [
        { name: "Review Recommended", value: Number(summary.medium_reviews ?? 0) },
        { name: "Strong Review", value: Number(summary.strong_reviews ?? 0) },
      ]
    : [];

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <h2>AI Moderation Recommendation System</h2>
          <p>Loading OULAD assessment data...</p>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="app">
        <div className="error-box">
          <h2>AI Moderation Recommendation System</h2>
          <p>{error || "Dashboard data is unavailable."}</p>
          <p className="hint">Backend URL: {API_URL}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>AI Moderation Recommendation System</h1>
          <p>OULAD-based detection of unusual assessment-score patterns</p>
        </div>
        <div className="status">
          <span className="status-dot" />
          OULAD Dataset Connected
        </div>
      </header>

      <main className="dashboard">
        <section className="welcome">
          <h2>Moderation Dashboard</h2>
          <p>
            Explore statistical and machine-learning flags, inspect assessment
            records, and prioritize cases for human review.
          </p>
          <p className="oulad-disclaimer">
            These are anomaly-based review recommendations, not confirmed cases
            of unfair marking.
          </p>
        </section>

        <section className="stats-grid">
          <StatCard
            title="Assessment Records"
            value={summary.total_records}
            description="Valid OULAD assessment scores"
          />
          <StatCard
            title="Statistical Flags"
            value={summary.statistical_anomalies}
            description="Flagged by statistical detection"
            type="warning"
          />
          <StatCard
            title="Isolation Forest Flags"
            value={summary.isolation_forest_anomalies}
            description="Flagged by the ML model"
            type="info"
          />
          <StatCard
            title="Human Review Cases"
            value={summary.review_cases}
            description={`${summary.review_rate}% of analyzed records`}
            type="danger"
          />
          <StatCard
            title="Strong Review"
            value={summary.strong_reviews}
            description="Flagged by both detection methods"
            type="success"
          />
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Cases Requiring Human Review</h2>
              <p>Filter flagged OULAD student-assessment records.</p>
            </div>
            <span className="count-badge">{filteredReviews.length.toLocaleString("en-IN")} Cases</span>
          </div>

          <div className="filters">
            <div className="filter-group search-group">
              <label htmlFor="student-filter">Student ID</label>
              <input
                id="student-filter"
                type="text"
                inputMode="numeric"
                placeholder="Search numeric student ID"
                value={studentSearch}
                onChange={(e) => setStudentSearch(e.target.value)}
              />
            </div>

            <div className="filter-group">
              <label htmlFor="module-filter">Module</label>
              <select id="module-filter" value={moduleFilter} onChange={(e) => setModuleFilter(e.target.value)}>
                <option value="All">All Modules</option>
                {modules.map((module) => <option key={module} value={module}>{module}</option>)}
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="type-filter">Assessment Type</label>
              <select id="type-filter" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
                <option value="All">All Types</option>
                {assessmentTypes.map((type) => <option key={type} value={type}>{type}</option>)}
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="priority-filter">Review Priority</label>
              <select id="priority-filter" value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
                <option value="All">All Priorities</option>
                {priorities.map((priority) => <option key={priority} value={priority}>{priority}</option>)}
              </select>
            </div>

            <button type="button" className="reset-button" onClick={resetFilters}>
              Reset Filters
            </button>
          </div>

          <div className="filter-info">
            Showing <strong>{Math.min(filteredReviews.length, 50)}</strong> of{" "}
            <strong>{filteredReviews.length.toLocaleString("en-IN")}</strong> matching cases
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Student ID</th>
                  <th>Assessment</th>
                  <th>Module</th>
                  <th>Type</th>
                  <th>Score</th>
                  <th>Median</th>
                  <th>Deviation</th>
                  <th>Priority</th>
                  <th>Detection</th>
                </tr>
              </thead>
              <tbody>
                {filteredReviews.slice(0, 50).map((record, index) => {
                  const deviation = Number(record.Score_Deviation ?? 0);
                  return (
                    <tr key={`${record.id_student}-${record.id_assessment}-${index}`}>
                      <td>{record.id_student}</td>
                      <td>{record.id_assessment}</td>
                      <td>{record.code_module}</td>
                      <td>{record.assessment_type}</td>
                      <td>{Number(record.score ?? 0).toFixed(1)}</td>
                      <td>{Number(record.Assessment_Median ?? 0).toFixed(1)}</td>
                      <td className={deviation < 0 ? "negative" : "positive"}>
                        {deviation > 0 ? "+" : ""}{deviation.toFixed(1)}
                      </td>
                      <td>
                        <span className={`recommendation ${record.Review_Priority === "High" ? "strong" : "review"}`}>
                          {record.Review_Priority ?? "N/A"}
                        </span>
                      </td>
                      <td className="oulad-source">{record.Detection_Source ?? "N/A"}</td>
                    </tr>
                  );
                })}
                {filteredReviews.length === 0 && (
                  <tr><td colSpan="9" className="no-results">No cases match the selected filters.</td></tr>
                )}
              </tbody>
            </table>
          </div>
          {filteredReviews.length > 50 && (
            <p className="table-note">Showing the first 50 cases. Use filters to narrow the results.</p>
          )}
        </section>

        <section className="analytics">
          <div className="analytics-header">
            <h2>Analytics Overview</h2>
            <p>Distribution of detection flags and human-review recommendations.</p>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <h3>Detection Method Comparison</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={detectionChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Review Recommendation Split</h3>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie data={recommendationChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                    {recommendationChartData.map((entry, index) => (
                      <Cell key={entry.name} fill={COLORS[index]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Review Cases by Assessment Type</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={analytics.assessment_analysis}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="assessment_type" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="review_cases" name="Review cases" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Review Cases by Module</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={analytics.module_analysis}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="code_module" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="review_cases" name="Review cases" fill="#10b981" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="analysis-section">
          <div className="analysis-header">
            <h2>Student Assessment Analysis</h2>
            <p>Look up a student to inspect their assessment-level scores and review flags.</p>
          </div>

          <div className="analysis-grid oulad-analysis-grid">
            <div className="analysis-card">
              <h3>Student Lookup</h3>
              <p className="analysis-description">
                Enter a numeric student ID from the Open University Learning Analytics Dataset.
              </p>
              <div className="analysis-search">
                <input
                  type="text"
                  inputMode="numeric"
                  placeholder="e.g. 334333"
                  value={studentId}
                  onChange={(e) => setStudentId(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") searchStudent(); }}
                />
                <button type="button" onClick={searchStudent} disabled={studentLoading}>
                  {studentLoading ? "Searching..." : "Search"}
                </button>
              </div>

              {studentError && <p className="analysis-error">{studentError}</p>}
              {studentLoading && <p className="analysis-status">Loading student assessment records...</p>}

              {studentData && (
                <div className="analysis-result">
                  <div className="result-title">
                    <strong>Student {studentData.student_id}</strong>
                    <span>{studentData.records.length} assessment record(s)</span>
                  </div>
                  <div className="student-table-container">
                    <table className="student-table">
                      <thead>
                        <tr>
                          <th>Assessment</th>
                          <th>Module</th>
                          <th>Type</th>
                          <th>Score</th>
                          <th>Deviation</th>
                          <th>Priority</th>
                        </tr>
                      </thead>
                      <tbody>
                        {studentData.records.map((record, index) => {
                          const deviation = Number(record.Score_Deviation ?? 0);
                          const needsReview = Boolean(record.Requires_Human_Review) ||
                            record.Review_Priority === "High" ||
                            record.Review_Priority === "Medium";
                          return (
                            <tr key={`${record.id_assessment}-${index}`}>
                              <td>{record.id_assessment}</td>
                              <td>{record.code_module}</td>
                              <td>{record.assessment_type}</td>
                              <td>{Number(record.score ?? 0).toFixed(1)}</td>
                              <td className={deviation < 0 ? "negative" : "positive"}>
                                {deviation > 0 ? "+" : ""}{deviation.toFixed(1)}
                              </td>
                              <td>
                                <span className={needsReview ? "review-yes" : "review-no"}>
                                  {record.Review_Priority ?? (needsReview ? "Review" : "Normal")}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>

            <div className="analysis-card">
              <h3>Assessment Type Summary</h3>
              <p className="analysis-description">
                Review frequency across the three assessment categories in OULAD.
              </p>
              <div className="oulad-summary-list">
                {analytics.assessment_analysis.map((item) => (
                  <div className="oulad-summary-row" key={item.assessment_type}>
                    <div>
                      <strong>{item.assessment_type}</strong>
                      <span>{Number(item.review_cases).toLocaleString("en-IN")} review cases / {Number(item.total_records).toLocaleString("en-IN")} records</span>
                    </div>
                    <strong>{Number(item.review_rate).toFixed(2)}%</strong>
                  </div>
                ))}
              </div>
              <p className="oulad-note">
                Review rates describe model-flagged records, not confirmed marking errors.
              </p>
            </div>
          </div>
        </section>

        <section className="methodology">
          <h2>Detection Methodology</h2>
          <div className="method-grid">
            <div className="method-card">
              <h3>Statistical Detection</h3>
              <p>Combines IQR, robust Z-score, and percentile-based indicators to flag unusual scores within assessment groups.</p>
            </div>
            <div className="method-card">
              <h3>Isolation Forest</h3>
              <p>Uses a separate unsupervised anomaly-detection model for each assessment type to account for differences between CMA, Exam, and TMA score patterns.</p>
            </div>
            <div className="method-card">
              <h3>Moderation Engine</h3>
              <p>Combines the two detection outputs and assigns a review priority based on the number of methods that flag a record.</p>
            </div>
            <div className="method-card">
              <h3>Human Review</h3>
              <p>The system highlights records for further investigation. A human moderator must examine context before making any moderation decision.</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
