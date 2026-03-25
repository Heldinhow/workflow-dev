import { useEffect, useRef, useState, useCallback } from "react";
import type { WorkflowEvent } from "@/lib/types";

export interface UseExecutionEventsOptions {
  onEvent?: (event: WorkflowEvent) => void;
  onStreamEnd?: () => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
}

export interface UseExecutionEventsReturn {
  connected: boolean;
  streamDone: boolean;
}

export function useExecutionEvents(
  executionId: string,
  options: UseExecutionEventsOptions = {}
): UseExecutionEventsReturn {
  const { onEvent, onStreamEnd, onConnected, onDisconnected } = options;
  const [connected, setConnected] = useState(false);
  const [streamDone, setStreamDone] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  const handleStreamEnd = useCallback(() => {
    setStreamDone(true);
    setConnected(false);
    onStreamEnd?.();
  }, [onStreamEnd]);

  useEffect(() => {
    const es = new EventSource(`/api/executions/${executionId}/events`);
    esRef.current = es;

    es.onopen = () => {
      setConnected(true);
      onConnected?.();
    };

    es.onmessage = (e) => {
      const event: WorkflowEvent = JSON.parse(e.data);

      if (event.type === "stream_end") {
        setStreamDone(true);
        setConnected(false);
        es.close();
        onStreamEnd?.();
        return;
      }

      onEvent?.(event);
    };

    es.onerror = () => {
      setConnected(false);
      onDisconnected?.();
      if (!streamDone) {
        es.close();
      }
    };

    return () => es.close();
  }, [executionId, onEvent, onConnected, onDisconnected, handleStreamEnd, streamDone]);

  return { connected, streamDone };
}