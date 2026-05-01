interface Props {
  score: number | null;
  breakdown: {
    stack_match?: number;
    salary_match?: number;
    role_match?: number;
    work_mode_match?: number;
    contract_match?: number;
    summary?: string;
  };
}

function Bar({ label, value }: { label: string; value?: number }) {
  if (value === undefined) return null;
  const pct = Math.round((value / 10) * 100);
  const color = value >= 7 ? "bg-green-500" : value >= 4 ? "bg-yellow-400" : "bg-red-400";
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-28 text-gray-500 shrink-0">{label}</span>
      <div className="flex-1 h-1.5 bg-gray-100 rounded">
        <div className={`h-full rounded ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-6 text-right text-gray-600">{value.toFixed(1)}</span>
    </div>
  );
}

export default function ScoreBar({ score, breakdown }: Props) {
  if (score === null) return <span className="text-xs text-gray-400">Not scored</span>;

  const color = score >= 7 ? "text-green-600" : score >= 4 ? "text-yellow-600" : "text-red-500";

  return (
    <div className="space-y-1">
      <div className={`text-2xl font-bold ${color}`}>{score.toFixed(1)}<span className="text-sm font-normal text-gray-400">/10</span></div>
      <Bar label="Stack" value={breakdown.stack_match} />
      <Bar label="Salary" value={breakdown.salary_match} />
      <Bar label="Role" value={breakdown.role_match} />
      <Bar label="Work mode" value={breakdown.work_mode_match} />
      <Bar label="Contract" value={breakdown.contract_match} />
    </div>
  );
}
