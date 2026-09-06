import { useMemo } from "react";
import ReactFlow, { Background } from "reactflow";
import "reactflow/dist/style.css";
import AgentNode from "./AgentNode.jsx";

const agentLabels = {
  chat: "Chat",
  research: "Research",
  rag: "RAG",
  analytics: "Analytics",
  document: "Document",
  supervisor: "Supervisor",
};

const agentPositions = {
  chat: { x: -125, y: 90 },
  research: { x: 125, y: 90 },
  rag: { x: -145, y: 190 },
  analytics: { x: 145, y: 190 },
  document: { x: -64, y: 285 },
};

const statusStyles = {
  completed: "completed",
  started: "started",
  failed: "failed",
};

const nodeTypes = { agent: AgentNode };

export default function WorkflowVisualization({ workflowTrace = [] }) {
  const traceStatuses = useMemo(
    () =>
      workflowTrace.reduce((statuses, event) => {
        statuses[event.agent] = event.status;
        return statuses;
      }, {}),
    [workflowTrace]
  );

  const nodes = useMemo(
    () => {
      const supervisorNode = {
        id: "supervisor",
        position: { x: 0, y: 0 },
        type: "agent",
        data: {
          agent: "supervisor",
          label: "Supervisor",
          status: traceStatuses.supervisor
            ? statusStyles[traceStatuses.supervisor] || statusStyles.started
            : "inactive",
        },
      };

      const specializedAgents = Object.keys(agentLabels).filter((agent) => agent !== "supervisor");

      return [
        supervisorNode,
        ...specializedAgents.map((agent) => {
          return {
            id: agent,
            position: agentPositions[agent],
            type: "agent",
            data: {
              agent,
              label: agentLabels[agent],
              status: traceStatuses[agent]
                ? statusStyles[traceStatuses[agent]] || statusStyles.started
                : "inactive",
            },
          };
        }),
      ];
    },
    [traceStatuses]
  );
  const edges = useMemo(
    () =>
      Object.keys(agentLabels)
        .filter((agent) => agent !== "supervisor")
        .map((agent) => ({
          id: `supervisor-${agent}`,
          source: "supervisor",
          target: agent,
          style: traceStatuses[agent]
            ? {
                stroke: traceStatuses[agent] === "failed" ? "#fbbf24" : "#67e8f9",
                strokeOpacity: 0.65,
                strokeWidth: 1.5,
              }
            : { stroke: "#526272", strokeOpacity: 0.28, strokeWidth: 1 },
        })),
    [traceStatuses]
  );

  return (
    <div className="h-64 overflow-hidden rounded-lg border border-white/10 bg-[#070d14]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.12, minZoom: 0.5, maxZoom: 1.1 }}
        nodesDraggable={false}
        nodesConnectable={false}
        panOnDrag={false}
        zoomOnScroll={false}
        zoomOnPinch={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#19303a" gap={26} size={1} />
      </ReactFlow>
    </div>
  );
}
