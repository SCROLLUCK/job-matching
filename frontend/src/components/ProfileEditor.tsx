import { useState, useEffect, useRef } from "react";
import { UserProfile, saveProfile, rescoreJobs, autofillProfile } from "../api";
import TagInput from "./TagInput";
import MultiSelect from "./MultiSelect";

const WORK_MODE_OPTIONS = [
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "onsite", label: "On-site" },
];

const CONTRACT_OPTIONS = [
  { value: "pj", label: "PJ" },
  { value: "clt", label: "CLT" },
];

const WEIGHT_CRITERIA: { key: string; label: string }[] = [
  { key: "stack", label: "Tech stack" },
  { key: "salary", label: "Salary" },
  { key: "role", label: "Role" },
  { key: "work_mode", label: "Work mode" },
  { key: "contract", label: "Contract" },
];

const WEIGHT_LEVELS = [
  { value: 1, label: "Low" },
  { value: 2, label: "Medium" },
  { value: 3, label: "High" },
];

function WeightToggle({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  return (
    <div className="flex rounded-md border border-gray-200 overflow-hidden text-xs font-medium">
      {WEIGHT_LEVELS.map((level) => (
        <button
          key={level.value}
          type="button"
          onClick={() => onChange(level.value)}
          className={`flex-1 px-3 py-1.5 transition-colors ${
            value === level.value
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-500 hover:bg-gray-50"
          }`}
        >
          {level.label}
        </button>
      ))}
    </div>
  );
}

interface Props {
  profile: UserProfile;
  onSaved: (p: UserProfile) => void;
  showToast: (message: string, type: "success" | "error") => void;
  startProgress: (label: string) => void;
  updateProgress: (detail: string) => void;
  stopProgress: () => void;
}

export default function ProfileEditor({ profile, onSaved, showToast, startProgress, updateProgress, stopProgress }: Props) {
  const [form, setForm] = useState(profile);
  const [saving, setSaving] = useState(false);
  const [rescoring, setRescoring] = useState(false);
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [autofilling, setAutofilling] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, [form.competencies]);

  const set = <K extends keyof UserProfile>(key: K, value: UserProfile[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const defaultWeights: Record<string, number> = { stack: 2, salary: 2, role: 2, work_mode: 2, contract: 2 };
  const weights: Record<string, number> = { ...defaultWeights, ...(form.score_weights || {}) };
  const setWeight = (key: string, value: number) =>
    setForm((f) => ({ ...f, score_weights: { ...weights, [key]: value } }));

  async function handleAutofill() {
    setAutofilling(true);
    try {
      const data = await autofillProfile(linkedinUrl);
      setForm((f) => ({
        ...f,
        competencies: data.competencies || f.competencies,
        tech_stack: data.tech_stack.length ? data.tech_stack : f.tech_stack,
        preferred_roles: data.preferred_roles.length ? data.preferred_roles : f.preferred_roles,
      }));
      showToast("Profile filled — review and save", "success");
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Autofill failed", "error");
    } finally {
      setAutofilling(false);
    }
  }

  async function handleSave() {
    setSaving(true);
    try {
      const updated = await saveProfile(form);
      onSaved(updated);
      showToast("Profile saved", "success");
    } catch {
      showToast("Failed to save profile", "error");
    } finally {
      setSaving(false);
    }
  }

  async function handleRescore() {
    setRescoring(true);
    startProgress("Re-scoring");
    try {
      await rescoreJobs((event) => {
        if (event.type === "complete") {
          stopProgress();
          showToast(`Re-scored ${event.updated} jobs`, "success");
        } else if (event.processed !== undefined) {
          updateProgress(`${event.processed} / ${event.total} jobs`);
        }
      });
    } catch {
      stopProgress();
      showToast("Failed to re-score jobs", "error");
    } finally {
      setRescoring(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-gray-800">Your Profile</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRescore}
            disabled={rescoring}
            className="bg-gray-100 hover:bg-gray-200 disabled:opacity-50 text-gray-700 text-sm font-medium px-4 py-1.5 rounded-lg transition-colors"
          >
            {rescoring ? "Re-scoring…" : "Re-score Jobs"}
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-colors"
          >
            {saving ? "Saving…" : "Save Profile"}
          </button>
        </div>
      </div>

      <div className="flex gap-2">
        <input
          type="url"
          value={linkedinUrl}
          onChange={(e) => setLinkedinUrl(e.target.value)}
          placeholder="https://linkedin.com/in/your-profile"
          className="flex-1 text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleAutofill}
          disabled={autofilling || !linkedinUrl.includes("linkedin.com/in/")}
          className="shrink-0 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 text-sm font-medium px-4 py-1.5 rounded-lg transition-colors"
        >
          {autofilling ? "Filling…" : "Auto-fill from LinkedIn"}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Competencies</label>
          <textarea
            ref={textareaRef}
            value={form.competencies}
            onChange={(e) => set("competencies", e.target.value)}
            placeholder="Describe your skills, experience, technologies you know, years of experience, etc."
            rows={4}
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none overflow-hidden"
          />
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Tech stack</label>
            <TagInput
              value={form.tech_stack}
              onChange={(tags) => set("tech_stack", tags)}
              placeholder="Python, Django… (Enter)"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Preferred roles</label>
            <TagInput
              value={form.preferred_roles}
              onChange={(tags) => set("preferred_roles", tags)}
              placeholder="Backend Developer… (Enter)"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Salary min (R$)</label>
              <input
                type="number"
                value={form.desired_salary_min ?? ""}
                onChange={(e) => set("desired_salary_min", e.target.value ? parseInt(e.target.value) : null)}
                placeholder="5000"
                className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Salary max (R$)</label>
              <input
                type="number"
                value={form.desired_salary_max ?? ""}
                onChange={(e) => set("desired_salary_max", e.target.value ? parseInt(e.target.value) : null)}
                placeholder="15000"
                className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Contract</label>
              <MultiSelect
                options={CONTRACT_OPTIONS}
                value={form.preferred_contract_type}
                onChange={(v) => set("preferred_contract_type", v)}
                placeholder="Any"
                allLabel="Any"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Work mode</label>
              <MultiSelect
                options={WORK_MODE_OPTIONS}
                value={form.preferred_work_mode}
                onChange={(v) => set("preferred_work_mode", v)}
                placeholder="Any"
                allLabel="Any"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-3">Scoring weights</label>
            <div className="space-y-3">
              {WEIGHT_CRITERIA.map(({ key, label }) => (
                <div key={key} className="flex items-center gap-4">
                  <span className="text-xs text-gray-500 w-20 shrink-0">{label}</span>
                  <WeightToggle value={weights[key] ?? 2} onChange={(v) => setWeight(key, v)} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
