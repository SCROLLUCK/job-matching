import { useEffect } from "react";

interface Props {
  message: string;
  type: "success" | "error";
  onClose: () => void;
}

export default function Toast({ message, type, onClose }: Props) {
  useEffect(() => {
    const t = setTimeout(onClose, 3500);
    return () => clearTimeout(t);
  }, [message, onClose]);

  const colors =
    type === "success"
      ? "bg-gray-900 text-white"
      : "bg-red-600 text-white";

  const icon = type === "success" ? "✓" : "✕";

  return (
    <div className={`fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-lg text-sm font-medium animate-fade-in ${colors}`}>
      <span className="text-base leading-none">{icon}</span>
      {message}
      <button onClick={onClose} className="ml-2 opacity-60 hover:opacity-100 leading-none">×</button>
    </div>
  );
}
