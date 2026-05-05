import { JobFilters } from "../api";
import MultiSelect from "./MultiSelect";
import TagInput from "./TagInput";

interface Props {
  filters: JobFilters;
  onChange: (f: JobFilters) => void;
}

const SOURCE_OPTIONS = [
  { value: "linkedin", label: "LinkedIn" },
  { value: "nerdin", label: "Nerdin" },
  { value: "geekhunter", label: "GeekHunter" },
  { value: "indeed", label: "Indeed" },
];

const CONTRACT_OPTIONS = [
  { value: "pj", label: "PJ" },
  { value: "clt", label: "CLT" },
  { value: "both", label: "PJ + CLT" },
];

const WORK_MODE_OPTIONS = [
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "onsite", label: "On-site" },
];

const LEVEL_OPTIONS = [
  { value: "junior", label: "Junior" },
  { value: "mid", label: "Mid-level" },
  { value: "senior", label: "Senior" },
];

const SORT_OPTIONS = [
  { value: "score", label: "Score" },
  { value: "date", label: "Date posted" },
  { value: "salary", label: "Salary" },
  { value: "scraped", label: "Recently scraped" },
];

function Label({ children }: { children: React.ReactNode }) {
  return <label className="block text-xs font-medium text-gray-600 mb-1">{children}</label>;
}

export default function FilterDrawer({ filters, onChange }: Props) {
  const set = <K extends keyof JobFilters>(key: K) => (value: JobFilters[K]) =>
    onChange({ ...filters, [key]: value });

  return (
    <aside className="w-56 shrink-0 space-y-4">
      <div>
        <Label>Search</Label>
        <input
          type="text"
          value={filters.search ?? ""}
          onChange={(e) => set("search")(e.target.value || undefined)}
          placeholder="Title, company, skill…"
          className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <Label>Sort by</Label>
        <select
          value={filters.sort ?? "score"}
          onChange={(e) => set("sort")(e.target.value as JobFilters["sort"])}
          className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {SORT_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      </div>

      <div>
        <Label>Source</Label>
        <MultiSelect options={SOURCE_OPTIONS} value={filters.source ?? []} onChange={set("source")} placeholder="All sources" />
      </div>

      <div>
        <Label>Contract</Label>
        <MultiSelect options={CONTRACT_OPTIONS} value={filters.contract_type ?? []} onChange={set("contract_type")} placeholder="Any" />
      </div>

      <div>
        <Label>Work mode</Label>
        <MultiSelect options={WORK_MODE_OPTIONS} value={filters.work_mode ?? []} onChange={set("work_mode")} placeholder="Any" />
      </div>

      <div>
        <Label>Level</Label>
        <MultiSelect options={LEVEL_OPTIONS} value={filters.experience_level ?? []} onChange={set("experience_level")} placeholder="Any" />
      </div>

      <div>
        <Label>Stack</Label>
        <TagInput value={filters.stack ?? []} onChange={set("stack")} placeholder="React, Python… (Enter)" />
      </div>

      <div>
        <Label>Min score</Label>
        <input
          type="number"
          min={0} max={10} step={0.5}
          value={filters.min_score ?? ""}
          onChange={(e) => set("min_score")(e.target.value ? parseFloat(e.target.value) : undefined)}
          placeholder="e.g. 7"
          className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <Label>Salary min</Label>
          <input
            type="number"
            value={filters.salary_min ?? ""}
            onChange={(e) => set("salary_min")(e.target.value ? parseInt(e.target.value) : undefined)}
            placeholder="3000"
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <Label>Salary max</Label>
          <input
            type="number"
            value={filters.salary_max ?? ""}
            onChange={(e) => set("salary_max")(e.target.value ? parseInt(e.target.value) : undefined)}
            placeholder="20000"
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </aside>
  );
}
