import { useState } from "react";
import { UserProfile, saveProfile, rescoreJobs } from "../api";
import TagInput from "./TagInput";

interface Props {
  profile: UserProfile;
  onSaved: (p: UserProfile) => void;
  showToast: (message: string, type: "success" | "error") => void;
}

export default function ProfileEditor({ profile, onSaved, showToast }: Props) {
  const [form, setForm] = useState(profile);
  const [saving, setSaving] = useState(false);
  const [rescoring, setRescoring] = useState(false);

  const set = <K extends keyof UserProfile>(key: K, value: UserProfile[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

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
    try {
      const result = await rescoreJobs();
      showToast(`Re-scored ${result.updated} jobs`, "success");
    } catch {
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

      <div className="grid grid-cols-2 gap-6">
        <div className="flex flex-col">
          <label className="block text-xs font-medium text-gray-600 mb-1">Competencies</label>
          <textarea
            value={form.competencies}
            onChange={(e) => set("competencies", e.target.value)}
            placeholder="Describe your skills, experience, technologies you know, years of experience, etc."
            className="flex-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
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
              <select
                value={form.preferred_contract_type}
                onChange={(e) => set("preferred_contract_type", e.target.value as UserProfile["preferred_contract_type"])}
                className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="both">PJ + CLT</option>
                <option value="pj">PJ only</option>
                <option value="clt">CLT only</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Work mode</label>
              <select
                value={form.preferred_work_mode}
                onChange={(e) => set("preferred_work_mode", e.target.value as UserProfile["preferred_work_mode"])}
                className="w-full text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="any">Any</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">On-site</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
