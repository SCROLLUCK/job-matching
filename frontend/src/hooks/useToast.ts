import { useState, useCallback } from "react";

interface ToastState {
  message: string;
  type: "success" | "error" | "loading";
}

export function useToast() {
  const [toast, setToast] = useState<ToastState | null>(null);

  const showToast = useCallback((message: string, type: "success" | "error" | "loading" = "success") => {
    setToast({ message, type });
  }, []);

  const clearToast = useCallback(() => setToast(null), []);

  return { toast, showToast, clearToast };
}
