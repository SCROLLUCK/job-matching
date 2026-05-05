import { useEffect, useRef, useState } from "react";

export interface MultiSelectOption {
  value: string;
  label: string;
}

interface Props {
  options: MultiSelectOption[];
  value: string[];
  onChange: (v: string[]) => void;
  placeholder: string;
  allLabel?: string;
}

export default function MultiSelect({ options, value, onChange, placeholder, allLabel }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  function toggle(v: string) {
    onChange(value.includes(v) ? value.filter((x) => x !== v) : [...value, v]);
  }

  const allSelected = value.length === 0 || value.length === options.length;
  const label = allSelected
    ? allLabel ?? placeholder
    : value.map((v) => options.find((o) => o.value === v)?.label ?? v).join(", ");

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between gap-2 text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white hover:border-gray-300 transition-colors"
      >
        <span className={allSelected ? "text-gray-400" : "text-gray-700 truncate"}>{label}</span>
        <svg className="w-4 h-4 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="absolute left-0 z-10 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg py-1">
          {options.map((opt) => (
            <label
              key={opt.value}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={value.includes(opt.value)}
                onChange={() => toggle(opt.value)}
                className="rounded"
              />
              {opt.label}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
