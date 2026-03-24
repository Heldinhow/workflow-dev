interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
  return <div className={`skeleton rounded ${className}`} />;
}

export function SkeletonText({ lines = 3, className = "" }: { lines?: number; className?: string }) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} className={`h-4 ${i === lines - 1 ? "w-3/4" : "w-full"}`} />
      ))}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4 space-y-4">
      <div className="flex items-center gap-3">
        <Skeleton className="w-20 h-5 rounded-full" />
        <Skeleton className="w-16 h-4 rounded" />
      </div>
      <Skeleton className="h-4 w-full" />
      <div className="flex items-center gap-4">
        <Skeleton className="w-20 h-3 rounded" />
        <Skeleton className="w-16 h-3 rounded" />
        <Skeleton className="w-24 h-3 rounded" />
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden">
      <div className="border-b border-zinc-800 bg-zinc-900/50 px-4 py-3">
        <div className="flex gap-4">
          <Skeleton className="w-20 h-3 rounded" />
          <Skeleton className="w-32 h-3 rounded" />
          <Skeleton className="w-28 h-3 rounded" />
          <Skeleton className="w-28 h-3 rounded" />
          <Skeleton className="w-20 h-3 rounded" />
          <Skeleton className="w-24 h-3 rounded" />
        </div>
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="px-4 py-3 border-b border-zinc-800/50 last:border-0">
          <div className="flex gap-4 items-center">
            <Skeleton className="w-20 h-3 rounded" />
            <Skeleton className="w-48 h-3 rounded" />
            <Skeleton className="w-20 h-5 rounded-full" />
            <Skeleton className="w-28 h-3 rounded" />
            <Skeleton className="w-20 h-3 rounded" />
            <Skeleton className="w-24 h-3 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}
