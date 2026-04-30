import { useEffect, useState } from "react";
import { Job, UserProfile, JobFilters, fetchJobs, fetchProfile, runScrape } from "./api";
import JobCard from "./components/JobCard";
import FilterDrawer from "./components/FilterDrawer";
import ProfileEditor from "./components/ProfileEditor";
import Toast from "./components/Toast";
import { useToast } from "./hooks/useToast";

type Tab = "jobs" | "profile";

export default function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [filters, setFilters] = useState<JobFilters>({ sort: "score" });
  const [tab, setTab] = useState<Tab>("jobs");
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const { toast, showToast, clearToast } = useToast();

  useEffect(() => {
    fetchProfile().then(setProfile);
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchJobs(filters).then((data) => {
      setJobs(data);
      setLoading(false);
    });
  }, [filters]);

  async function handleScrape() {
    setScraping(true);
    try {
      const result = await runScrape();
      const errors = Object.keys(result).filter((k) => k.includes("error"));
      if (errors.length) {
        showToast("Scrape finished with errors", "error");
      } else {
        const counts = Object.entries(result)
          .filter(([k]) => k !== "scraped_at")
          .map(([k, v]) => `${k}: +${v}`)
          .join(" · ");
        showToast(counts || "No new jobs found", "success");
      }
      fetchJobs(filters).then(setJobs);
    } catch {
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
                onClick={() => setTab("profile")}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${tab === "profile" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"}`}
              >
                Profile
              </button>
            </div>
            <button
              onClick={handleScrape}
              disabled={scraping}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-colors"
            >
              {scraping ? "Scraping…" : "Scrape Now"}
            </button>
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

        {tab === "profile" && profile && (
          <div className="w-full">
            <ProfileEditor profile={profile} onSaved={setProfile} showToast={showToast} />
          </div>
        )}
      </main>

      {toast && <Toast message={toast.message} type={toast.type} onClose={clearToast} />}
    </div>
  );
}
