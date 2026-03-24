interface AvatarProps {
  src?: string;
  alt?: string;
  fallback?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeClasses = {
  sm: "w-6 h-6 text-xs",
  md: "w-8 h-8 text-sm",
  lg: "w-10 h-10 text-base",
};

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function Avatar({ src, alt, fallback = "?", size = "md", className = "" }: AvatarProps) {
  if (src) {
    return (
      <img
        src={src}
        alt={alt}
        className={`rounded-full object-cover ${sizeClasses[size]} ${className}`}
      />
    );
  }

  return (
    <div
      className={`
        rounded-full bg-gradient-to-br from-indigo-500 to-indigo-600
        flex items-center justify-center font-medium text-white
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {getInitials(fallback)}
    </div>
  );
}

interface AvatarGroupProps {
  avatars: { src?: string; alt?: string; fallback: string }[];
  max?: number;
  size?: "sm" | "md" | "lg";
}

export function AvatarGroup({ avatars, max = 4, size = "md" }: AvatarGroupProps) {
  const visible = avatars.slice(0, max);
  const remaining = avatars.length - max;

  return (
    <div className="flex items-center -space-x-2">
      {visible.map((avatar, i) => (
        <div
          key={i}
          className="ring-2 ring-zinc-950 rounded-full"
          style={{ zIndex: visible.length - i }}
        >
          <Avatar src={avatar.src} alt={avatar.alt} fallback={avatar.fallback} size={size} />
        </div>
      ))}
      {remaining > 0 && (
        <div
          className={`
            rounded-full bg-zinc-800 flex items-center justify-center
            font-medium text-zinc-400 ring-2 ring-zinc-950
            ${sizeClasses[size]}
          `}
        >
          +{remaining}
        </div>
      )}
    </div>
  );
}
