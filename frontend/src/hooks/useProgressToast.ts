import { useCallback, useRef } from "react";
import { useToast } from "./useToast";

function fmtElapsed(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}m ${s.toString().padStart(2, "0")}s` : `${seconds}s`;
}

export function useProgressToast() {
  const { toast, showToast, clearToast } = useToast();
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startRef = useRef(0);
  const labelRef = useRef("");

  const startProgress = useCallback((label: string) => {
    labelRef.current = label;
    startRef.current = Date.now();
    showToast(`${label} · 0s`, "loading");
    timerRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startRef.current) / 1000);
      showToast(`${labelRef.current} · ${fmtElapsed(elapsed)}`, "loading");
    }, 1000);
  }, [showToast]);

  const stopProgress = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  return { toast, showToast, clearToast, startProgress, stopProgress };
}
