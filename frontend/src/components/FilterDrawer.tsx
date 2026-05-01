import { JobFilters } from "../api";

interface Props {
  filters: JobFilters;
  onChange: (f: JobFilters) => void;
}

function Select({ label, value, onChange, options }: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );
}

export default function FilterDrawer({ filters, onChange }: Props) {
  const set = (key: keyof JobFilters) => (value: string | number) =>
    onChange({ ...filters, [key]: value === "" ? undefined : value });

  return (
    <aside className="w-56 shrink-0 space-y-4">
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Search</label>
        <input
          type="text"
          value={filters.search ?? ""}
          onChange={(e) => set("search")(e.target.value)}
          placeholder="Title, company, skill…"
          className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <Select label="Sort by" value={filters.sort ?? "score"} onChange={set("sort")} options={[
        { value: "score", label: "Score" },
        { value: "date", label: "Date posted" },
        { value: "salary", label: "Salary" },
        { value: "scraped", label: "Recently scraped" },
      ]} />

      <Select label="Source" value={filters.source ?? ""} onChange={set("source")} options={[
        { value: "", label: "All sources" },
        { value: "linkedin", label: "LinkedIn" },
        { value: "nerdin", label: "Nerdin" },
        { value: "geekhunter", label: "GeekhHunter" },
        { value: "indeed", label: "Indeed" },
      ]} />

      <Select label="Contract" value={filters.contract_type ?? ""} onChange={set("contract_type")} options={[
        { value: "", label: "Any" },
        { value: "pj", label: "PJ" },
        { value: "clt", label: "CLT" },
        { value: "both", label: "PJ + CLT" },
      ]} />

      <Select label="Work mode" value={filters.work_mode ?? ""} onChange={set("work_mode")} options={[
        { value: "", label: "Any" },
        { value: "remote", label: "Remote" },
        { value: "hybrid", label: "Hybrid" },
        { value: "onsite", label: "On-site" },
      ]} />

      <Select label="Level" value={filters.experience_level ?? ""} onChange={set("experience_level")} options={[
        { value: "", label: "Any" },
        { value: "junior", label: "Junior" },
        { value: "mid", label: "Mid-level" },
        { value: "senior", label: "Senior" },
      ]} />

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Min score</label>
        <input
          type="number"
          min={0} max={10} step={0.5}
          value={filters.min_score ?? ""}
          onChange={(e) => set("min_score")(e.target.value ? parseFloat(e.target.value) : "")}
          placeholder="e.g. 7"
          className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Salary min (R$)</label>
          <input
            type="number"
            value={filters.salary_min ?? ""}
            onChange={(e) => set("salary_min")(e.target.value ? parseInt(e.target.value) : "")}
            placeholder="3000"
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Salary max (R$)</label>
          <input
            type="number"
            value={filters.salary_max ?? ""}
            onChange={(e) => set("salary_max")(e.target.value ? parseInt(e.target.value) : "")}
            placeholder="20000"
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </aside>
  );
}
