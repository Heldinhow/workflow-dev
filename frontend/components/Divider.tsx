interface DividerProps {
  orientation?: "horizontal" | "vertical";
  className?: string;
}

export function Divider({ orientation = "horizontal", className = "" }: DividerProps) {
  if (orientation === "vertical") {
    return <div className={`w-px h-full bg-zinc-800 ${className}`} />;
  }

  return <div className={`h-px w-full bg-zinc-800 ${className}`} />;
}
