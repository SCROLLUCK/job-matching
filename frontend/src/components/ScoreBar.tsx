interface Props {
  score: number | null;
  breakdown: {
    stack_match?: number;
    salary_match?: number;
    role_match?: number;
    work_mode_match?: number;
    contract_match?: number;
  };
  weights?: Record<string, number>;
}

const WEIGHT_LABELS: Record<number, { label: string; cls: string }> = {
  1: { label: "Low",  cls: "text-gray-400" },
  2: { label: "Med",  cls: "text-blue-400" },
  3: { label: "High", cls: "text-indigo-500" },
};

function Bar({ label, value, weight }: { label: string; value?: number; weight?: number }) {
  if (value === undefined) return null;
  const pct = Math.round((value / 10) * 100);
  const barColor =
    value >= 7 ? "bg-green-500" : value >= 4 ? "bg-yellow-400" : "bg-red-400";
  const w = weight ?? 2;
  const { label: wLabel, cls: wCls } = WEIGHT_LABELS[w] ?? WEIGHT_LABELS[2];
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-24 text-gray-500 shrink-0">{label}</span>
      <span className={`w-7 shrink-0 font-medium ${wCls}`}>{wLabel}</span>
      <div className="flex-1 h-1.5 bg-gray-100 rounded">
        <div className={`h-full rounded ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-6 text-right text-gray-600">{value.toFixed(1)}</span>
    </div>
  );
}

export default function ScoreBar({ score, breakdown, weights = {} }: Props) {
  if (score === null)
    return <span className="text-xs text-gray-400">Not scored</span>;

  const color =
    score >= 7 ? "text-green-600" : score >= 4 ? "text-yellow-600" : "text-red-500";

  return (
    <div className="space-y-1">
      <div className={`text-2xl font-bold ${color}`}>
        {score.toFixed(1)}
        <span className="text-sm font-normal text-gray-400">/10</span>
      </div>
      <Bar label="Stack"     value={breakdown.stack_match}     weight={weights.stack} />
      <Bar label="Salary"    value={breakdown.salary_match}    weight={weights.salary} />
      <Bar label="Role"      value={breakdown.role_match}      weight={weights.role} />
      <Bar label="Work mode" value={breakdown.work_mode_match} weight={weights.work_mode} />
      <Bar label="Contract"  value={breakdown.contract_match}  weight={weights.contract} />
    </div>
  );
}
