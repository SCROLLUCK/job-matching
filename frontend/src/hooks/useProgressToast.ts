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
  const detailRef = useRef("");

  const _show = useCallback(() => {
    const elapsed = Math.floor((Date.now() - startRef.current) / 1000);
    const detail = detailRef.current ? ` · ${detailRef.current}` : "";
    showToast(`${labelRef.current}${detail} · ${fmtElapsed(elapsed)}`, "loading");
  }, [showToast]);

  const startProgress = useCallback((label: string, startTime?: number) => {
    labelRef.current = label;
    detailRef.current = "";
    startRef.current = startTime ?? Date.now();
    showToast(`${label} · 0s`, "loading");
    timerRef.current = setInterval(_show, 1000);
  }, [showToast, _show]);

  const updateProgress = useCallback((detail: string) => {
    detailRef.current = detail;
    _show();
  }, [_show]);

  const stopProgress = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  return { toast, showToast, clearToast, startProgress, updateProgress, stopProgress };
}
