import { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import { fetchStats, JobStats } from "../api";
import TagInput from "./TagInput";
import MultiSelect from "./MultiSelect";

const LEVEL_OPTIONS = [
  { value: "junior", label: "Junior" },
  { value: "mid", label: "Mid" },
  { value: "senior", label: "Senior" },
  { value: "unknown", label: "Unknown" },
];

function fmtSalary(v: number | null) {
  if (!v) return "—";
  return `R$ ${v.toLocaleString("pt-BR")}`;
}

function dualBarOption(
  xData: string[],
  counts: number[],
  salaries: (number | null)[],
  rotateDeg = 0,
) {
  return {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
      formatter: (params: { seriesName: string; value: number | null; marker: string; axisValue: string }[]) => {
        const name = params[0]?.axisValue ?? "";
        const lines = params.map((p) =>
          p.seriesName === "Avg Salary"
            ? `${p.marker} Avg Salary: ${fmtSalary(p.value)}`
            : `${p.marker} Jobs: ${p.value}`,
        );
        return [name, ...lines].join("<br/>");
      },
    },
    legend: { data: ["Jobs", "Avg Salary"] },
    grid: { left: 50, right: 70, bottom: rotateDeg > 0 ? 100 : 40, top: 40 },
    xAxis: {
      type: "category",
      data: xData,
      axisLabel: { rotate: rotateDeg, interval: 0, fontSize: 11 },
    },
    yAxis: [
      { type: "value", name: "Jobs", nameTextStyle: { color: "#6b7280" } },
      {
        type: "value",
        name: "Avg Salary",
        nameTextStyle: { color: "#6b7280" },
        axisLabel: { formatter: (v: number) => `R$${(v / 1000).toFixed(0)}k` },
      },
    ],
    series: [
      { name: "Jobs", type: "bar", data: counts, itemStyle: { color: "#6366f1" }, barMaxWidth: 48 },
      { name: "Avg Salary", type: "bar", yAxisIndex: 1, data: salaries, itemStyle: { color: "#10b981" }, barMaxWidth: 48 },
    ],
  };
}

export default function StatsView() {
  const [stats, setStats] = useState<JobStats | null>(null);
  const [stackFilter, setStackFilter] = useState<string[]>([]);
  const [levelFilter, setLevelFilter] = useState<string[]>([]);
  const [loadingStack, setLoadingStack] = useState(false);
  const [sortBy, setSortBy] = useState<"jobs_desc" | "jobs_asc" | "salary_desc" | "salary_asc">("jobs_desc");

  useEffect(() => {
    setLoadingStack(true);
    fetchStats(levelFilter.length > 0 ? levelFilter : undefined).then((data) => {
      setStats(data);
      setLoadingStack(false);
    });
  }, [levelFilter]);

  if (!stats) return <p className="text-sm text-gray-400 py-10 text-center">Loading…</p>;

  const filtered =
    stackFilter.length > 0
      ? stats.by_stack.filter((d) => stackFilter.includes(d.tech))
      : stats.by_stack;

  const visibleStacks = [...filtered].sort((a, b) => {
    if (sortBy === "jobs_desc") return b.count - a.count;
    if (sortBy === "jobs_asc") return a.count - b.count;
    if (sortBy === "salary_desc") return (b.avg_salary ?? -1) - (a.avg_salary ?? -1);
    return (a.avg_salary ?? -1) - (b.avg_salary ?? -1);
  });

  const stackLabels = visibleStacks.map((d) => d.tech);
  const stackCounts = visibleStacks.map((d) => d.count);
  const stackSalaries = visibleStacks.map((d) => d.avg_salary);

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <div className="flex items-center justify-between gap-4 mb-4">
          <h2 className="text-sm font-semibold text-gray-700">
            Stacks — Occurrences & Average Salary
            <span className="ml-2 text-xs font-normal text-gray-400">
              {visibleStacks.length} of {stats.by_stack.length}
            </span>
          </h2>
          <div className="flex items-center gap-3">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="jobs_desc">Jobs ↓</option>
              <option value="jobs_asc">Jobs ↑</option>
              <option value="salary_desc">Avg Salary ↓</option>
              <option value="salary_asc">Avg Salary ↑</option>
            </select>
            <div className="w-40">
              <MultiSelect
                options={LEVEL_OPTIONS}
                value={levelFilter}
                onChange={setLevelFilter}
                placeholder="All levels"
              />
            </div>
            <div className="w-60">
              <TagInput
                value={stackFilter}
                onChange={setStackFilter}
                placeholder="Filter stacks…"
              />
            </div>
          </div>
        </div>
        <ReactECharts
          option={dualBarOption(stackLabels, stackCounts, stackSalaries, 40)}
          showLoading={loadingStack}
          style={{ height: 580 }}
        />
      </div>
    </div>
  );
}
