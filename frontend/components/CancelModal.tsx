"use client";

import { Button } from "@/components/Button";

interface CancelModalProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  executionId: string;
}

export function CancelModal({ isOpen, onConfirm, onCancel, executionId }: CancelModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onCancel} />
      <div className="relative bg-zinc-900 border border-zinc-700 rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
        <h3 className="text-lg font-semibold text-zinc-100 mb-2">Cancel Execution</h3>
        <p className="text-sm text-zinc-400 mb-6">
          Are you sure you want to cancel execution <span className="font-mono text-zinc-300">{executionId}</span>?
          This action cannot be undone.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="ghost" onClick={onCancel}>
            Keep Running
          </Button>
          <Button variant="danger" onClick={onConfirm}>
            Cancel Execution
          </Button>
        </div>
      </div>
    </div>
  );
}
