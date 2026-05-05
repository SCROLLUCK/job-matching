import { useEffect, useState } from "react";
import { Job, UserProfile, JobFilters, fetchJobs, fetchProfile, runScrape } from "./api";
import JobCard from "./components/JobCard";
import FilterDrawer from "./components/FilterDrawer";
import ProfileEditor from "./components/ProfileEditor";
import StatsView from "./components/StatsView";
import Toast from "./components/Toast";
import { useProgressToast } from "./hooks/useProgressToast";

type Tab = "jobs" | "applied" | "stats" | "profile";

export default function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [appliedJobs, setAppliedJobs] = useState<Job[]>([]);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [filters, setFilters] = useState<JobFilters>({ sort: "score" });
  const [tab, setTab] = useState<Tab>("jobs");
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const { toast, showToast, clearToast, startProgress, stopProgress } = useProgressToast();

  const profileFilled = profile !== null && (profile.competencies.trim().length > 0 || profile.tech_stack.length > 0);

  const refreshApplied = () => fetchJobs({ application_status: "applied" }).then(setAppliedJobs);

  useEffect(() => {
    fetchProfile().then(setProfile);
    refreshApplied();
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchJobs(filters).then((data) => {
      setJobs(data);
      setLoading(false);
    });
  }, [filters]);

  useEffect(() => {
    if (tab === "applied") refreshApplied();
  }, [tab]);

  async function handleScrape() {
    setScraping(true);
    startProgress("Scraping");
    const counts: Record<string, number> = {};
    try {
      await runScrape((event) => {
        if (event.type === "source_done") {
          counts[event.source as string] = event.count as number;
          const detail = Object.entries(counts).map(([s, n]) => `${s} +${n}`).join(" · ");
          updateProgress(detail);
        } else if (event.type === "source_start") {
          const pending = [
            ...Object.entries(counts).map(([s, n]) => `${s} +${n}`),
            `${event.source}…`,
          ].join(" · ");
          updateProgress(pending);
        } else if (event.type === "complete") {
          stopProgress();
          const hasErrors = Object.keys(event).some((k) => k.includes("error"));
          const summary = Object.entries(counts).map(([s, n]) => `${s}: +${n}`).join(" · ");
          showToast(
            hasErrors ? "Scrape finished with errors" : summary || "No new jobs found",
            hasErrors ? "error" : "success",
          );
          fetchJobs(filters).then(setJobs);
        }
      });
    } catch {
      stopProgress();
      showToast("Scrape failed", "error");
    } finally {
      setScraping(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 py-4">
        <div className="w-[80%] mx-auto flex items-center justify-between">
          <h1 className="text-lg font-bold text-gray-900">Job Matching</h1>
          <div className="flex items-center gap-3">
            <div className="flex bg-gray-100 rounded-lg p-0.5">
              <button
                onClick={() => setTab("jobs")}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${tab === "jobs" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"}`}
              >
                Jobs {jobs.length > 0 && <span className="ml-1 text-xs text-gray-400">({jobs.length})</span>}
              </button>
              <button
                onClick={() => setTab("applied")}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${tab === "applied" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"}`}
              >
                Applied {appliedJobs.length > 0 && <span className="ml-1 text-xs text-gray-400">({appliedJobs.length})</span>}
              </button>
              <button
                onClick={() => setTab("stats")}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${tab === "stats" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"}`}
              >
                Stats
              </button>
              <button
                onClick={() => setTab("profile")}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${tab === "profile" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"}`}
              >
                Profile
              </button>
            </div>
            <div className="relative group">
              <button
                onClick={handleScrape}
                disabled={scraping || !profileFilled}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-colors"
              >
                {scraping ? "Scraping…" : "Scrape Now"}
              </button>
              {!profileFilled && (
                <div className="absolute bottom-full mb-1.5 right-0 hidden group-hover:block whitespace-nowrap bg-gray-800 text-white text-xs rounded px-2 py-1">
                  Fill in your profile before scraping
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="w-[80%] mx-auto py-6">
        {tab === "jobs" && (
          <div className="flex gap-6">
            <FilterDrawer filters={filters} onChange={setFilters} />
            <div className="flex-1 min-w-0">
              {loading ? (
                <p className="text-sm text-gray-400 py-10 text-center">Loading…</p>
              ) : jobs.length === 0 ? (
                <div className="text-center py-16 text-gray-400">
                  <p className="text-lg font-medium">No jobs found</p>
                  <p className="text-sm mt-1">Try adjusting filters or click Scrape Now</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                  {jobs.map((job) => <JobCard key={job.id} job={job} />)}
                </div>
              )}
            </div>
          </div>
        )}

        {tab === "applied" && (
          <div className="flex-1 min-w-0">
            {appliedJobs.length === 0 ? (
              <div className="text-center py-16 text-gray-400">
                <p className="text-lg font-medium">No applications yet</p>
                <p className="text-sm mt-1">Mark jobs as applied from the Jobs tab</p>
              </div>
            ) : (
              <>
                <p className="text-sm text-gray-500 mb-4">{appliedJobs.length} application{appliedJobs.length !== 1 ? "s" : ""}</p>
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                  {appliedJobs.map((job) => <JobCard key={job.id} job={job} />)}
                </div>
              </>
            )}
          </div>
        )}

        {tab === "stats" && <StatsView />}

        {tab === "profile" && profile && (
          <div className="w-full">
            <ProfileEditor
              profile={profile}
              onSaved={setProfile}
              showToast={showToast}
              startProgress={startProgress}
              updateProgress={updateProgress}
              stopProgress={stopProgress}
            />
          </div>
        )}
      </main>

      {toast && <Toast message={toast.message} type={toast.type} onClose={clearToast} />}
    </div>
  );
}
