"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/Card";
import type { TokenUsage } from "@/lib/types";

interface TokenUsageCardProps {
  tokenUsage: TokenUsage;
}

function formatNumber(n: number | undefined): string {
  if (!n && n !== 0) return "—";
  return n.toLocaleString();
}

function formatCost(cost: number | undefined): string {
  if (!cost && cost !== 0) return "—";
  return `$${cost.toFixed(6)}`;
}

export function TokenUsageCard({ tokenUsage }: TokenUsageCardProps) {
  const hasTokens = tokenUsage && (tokenUsage.total_tokens || tokenUsage.prompt_tokens || tokenUsage.completion_tokens);

  return (
    <Card>
      <CardHeader className="p-5 pb-0">
        <CardTitle as="h3">Token Usage</CardTitle>
      </CardHeader>
      <CardContent className="p-5">
        {hasTokens ? (
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-zinc-400">Total Tokens</span>
              <span className="text-sm font-mono text-zinc-200">
                {formatNumber(tokenUsage.total_tokens)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-zinc-400">Prompt Tokens</span>
              <span className="text-sm font-mono text-zinc-200">
                {formatNumber(tokenUsage.prompt_tokens)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-zinc-400">Completion Tokens</span>
              <span className="text-sm font-mono text-zinc-200">
                {formatNumber(tokenUsage.completion_tokens)}
              </span>
            </div>
            <div className="flex justify-between items-center pt-2 border-t border-zinc-800">
              <span className="text-sm text-zinc-400">Est. Cost</span>
              <span className="text-sm font-mono text-emerald-400">
                {formatCost(tokenUsage.estimated_cost_usd)}
              </span>
            </div>
          </div>
        ) : (
          <p className="text-sm text-zinc-500">No token data available yet</p>
        )}
      </CardContent>
    </Card>
  );
}
