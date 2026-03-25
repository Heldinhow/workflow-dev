"use client";

import { Select } from "@/components/Select";

interface FilterOption {
  value: string;
  label: string;
}

interface FilterDropdownProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: FilterOption[];
  placeholder?: string;
}

export function FilterDropdown({
  label,
  value,
  onChange,
  options,
  placeholder = "All",
}: FilterDropdownProps) {
  const allOptions = [{ value: "", label: placeholder }, ...options];

  return (
    <Select
      label={label}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      options={allOptions}
    />
  );
}
