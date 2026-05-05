import { useEffect } from "react";

interface Props {
  message: string;
  type: "success" | "error" | "loading";
  onClose: () => void;
}

export default function Toast({ message, type, onClose }: Props) {
  useEffect(() => {
    if (type === "loading") return;
    const t = setTimeout(onClose, 3500);
    return () => clearTimeout(t);
  }, [message, type, onClose]);

  const colors =
    type === "error" ? "bg-red-600 text-white"
    : type === "loading" ? "bg-gray-800 text-white"
    : "bg-gray-900 text-white";

  const icon =
    type === "loading" ? (
      <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin shrink-0" />
    ) : (
      <span className="text-base leading-none">{type === "success" ? "✓" : "✕"}</span>
    );

  return (
    <div className={`fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-lg text-sm font-medium animate-fade-in ${colors}`}>
      {icon}
      {message}
      {type !== "loading" && (
        <button onClick={onClose} className="ml-2 opacity-60 hover:opacity-100 leading-none">×</button>
      )}
    </div>
  );
}
