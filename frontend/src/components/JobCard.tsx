import { useState } from "react";
import { Job, setJobStatus } from "../api";
import ScoreBar from "./ScoreBar";

const SOURCE_LABELS: Record<string, string> = {
  linkedin: "LinkedIn",
  nerdin: "Nerdin",
  geekhunter: "GeekhHunter",
};

const SOURCE_COLORS: Record<string, string> = {
  linkedin: "bg-blue-100 text-blue-700",
  nerdin: "bg-purple-100 text-purple-700",
  geekhunter: "bg-green-100 text-green-700",
};

function salaryLabel(min: number | null, max: number | null): string {
  if (!min && !max) return "";
  const fmt = (n: number) => `R$ ${n.toLocaleString("pt-BR")}`;
  if (min && max) return `${fmt(min)} – ${fmt(max)}`;
  if (max) return `até ${fmt(max)}`;
  return `a partir de ${fmt(min!)}`;
}

export default function JobCard({ job }: { job: Job }) {
  const [status, setStatus] = useState(job.application_status);

  async function changeStatus(next: "" | "applied" | "rejected") {
    const result = await setJobStatus(job.id, next);
    setStatus(result.application_status as typeof status);
  }

  const borderClass = status === "applied" ? "border-green-300 bg-green-50"
    : status === "rejected" ? "border-red-200 bg-red-50"
    : "border-gray-200";

  return (
    <div className={`bg-white border rounded-xl p-5 flex flex-col gap-3 hover:shadow-md transition-shadow ${borderClass}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <a href={job.url} target="_blank" rel="noopener noreferrer" className="font-semibold text-gray-900 hover:text-blue-600 line-clamp-2">
            {job.title}
          </a>
          {job.company && <p className="text-sm text-gray-500 mt-0.5">{job.company}</p>}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {status === "" && (
            <button onClick={() => changeStatus("applied")} className="text-xs font-medium px-2.5 py-0.5 rounded-full border border-gray-200 text-gray-400 hover:border-green-300 hover:text-green-600 transition-colors">
              Mark applied
            </button>
          )}
          {status === "applied" && (
            <>
              <button onClick={() => changeStatus("rejected")} className="text-xs font-medium px-2.5 py-0.5 rounded-full border border-red-200 text-red-400 hover:bg-red-50 transition-colors">
                Didn't get it
              </button>
              <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-green-100 text-green-700 border border-green-300">Applied</span>
            </>
          )}
          {status === "rejected" && (
            <button onClick={() => changeStatus("")} className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-red-100 text-red-500 border border-red-200 hover:bg-red-200 transition-colors">
              Not selected
            </button>
          )}
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${SOURCE_COLORS[job.source]}`}>
            {SOURCE_LABELS[job.source]}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
        <div className="flex items-center gap-1.5 text-gray-500">
          <span className="text-gray-400 w-16 shrink-0">Salary</span>
          <span className="text-gray-700 font-medium">{salaryLabel(job.salary_min, job.salary_max) || "—"}</span>
        </div>
        <div className="flex items-center gap-1.5 text-gray-500">
          <span className="text-gray-400 w-16 shrink-0">Contract</span>
          <span className="text-gray-700 font-medium uppercase">{job.contract_type !== "unknown" ? job.contract_type : "—"}</span>
        </div>
        <div className="flex items-center gap-1.5 text-gray-500">
          <span className="text-gray-400 w-16 shrink-0">Work mode</span>
          <span className="text-gray-700 font-medium capitalize">{job.work_mode !== "unknown" ? job.work_mode : "—"}</span>
        </div>
        <div className="flex items-center gap-1.5 text-gray-500">
          <span className="text-gray-400 w-16 shrink-0">Level</span>
          <span className="text-gray-700 font-medium capitalize">{job.experience_level !== "unknown" ? job.experience_level : "—"}</span>
        </div>
        {job.location && (
          <div className="flex items-center gap-1.5 text-gray-500 col-span-2">
            <span className="text-gray-400 w-16 shrink-0">Location</span>
            <span className="text-gray-700">{job.location}</span>
          </div>
        )}
      </div>

      {job.tech_stack.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {job.tech_stack.slice(0, 8).map((tag) => (
            <span key={tag} className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">{tag}</span>
          ))}
          {job.tech_stack.length > 8 && <span className="text-xs text-gray-400">+{job.tech_stack.length - 8}</span>}
        </div>
      )}

      {job.description && (
        <p className="text-xs text-gray-500 leading-relaxed line-clamp-3">{job.description}</p>
      )}

      <ScoreBar score={job.score} breakdown={job.score_breakdown} />
    </div>
  );
}
