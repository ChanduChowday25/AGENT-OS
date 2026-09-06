import { useEffect, useState } from "react";

/**
 * TODO: connect to the backend's SSE stream (LangGraph stream() -> FastAPI)
 * and translate workflow_trace events into React Flow nodes/edges for
 * WorkflowVisualization.jsx.
 */
export function useWorkflow(conversationId) {
  const [trace, setTrace] = useState([]);

  useEffect(() => {
    if (!conversationId) return;
    // TODO: const source = new EventSource(`${baseURL}/chat/stream?...`)
    // TODO: source.onmessage = (event) => setTrace((prev) => [...prev, JSON.parse(event.data)])
    // TODO: return () => source.close()
  }, [conversationId]);

  return trace;
}
