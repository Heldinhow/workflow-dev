import { forwardRef } from "react";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "info" | "outline";
  size?: "sm" | "md";
}

const variantClasses = {
  default: "bg-zinc-800/50 text-zinc-400",
  success: "bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20",
  warning: "bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/20",
  danger: "bg-red-500/10 text-red-400 ring-1 ring-red-500/20",
  info: "bg-blue-500/10 text-blue-400 ring-1 ring-blue-500/20",
  outline: "bg-transparent text-zinc-400 ring-1 ring-zinc-700",
};

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className = "", variant = "default", size = "sm", children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={`
          inline-flex items-center gap-1.5 rounded-full font-medium
          ${variantClasses[variant]}
          ${size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm"}
          ${className}
        `}
        {...props}
      >
        {children}
      </span>
    );
  }
);

Badge.displayName = "Badge";
