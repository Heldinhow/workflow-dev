export function RetryBadge({
  label,
  count,
  max,
  color = "blue",
}: {
  label: string;
  count: number;
  max: number;
  color?: "blue" | "amber";
}) {
  const filled = color === "blue" ? "bg-blue-400" : "bg-amber-400";
  const empty  = "bg-zinc-800";
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-zinc-500 w-28">{label}</span>
      <div className="flex gap-1">
        {Array.from({ length: max }).map((_, i) => (
          <div
            key={i}
            className={`w-2 h-2 rounded-sm ${i < count ? filled : empty}`}
          />
        ))}
      </div>
      <span className="text-xs font-mono text-zinc-500">
        {count}/{max}
      </span>
    </div>
  );
}
