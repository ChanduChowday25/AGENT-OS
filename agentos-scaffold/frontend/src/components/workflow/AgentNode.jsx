import { Handle, Position } from "reactflow";

const statusContent = {
  completed: { marker: "✓", label: "Completed" },
  started: { marker: "•", label: "Active" },
  failed: { marker: "!", label: "Failed" },
  inactive: { marker: "", label: "Not active" },
};

export default function AgentNode({ data }) {
  const status = statusContent[data.status] || statusContent.inactive;
  const isSupervisor = data.agent === "supervisor";

  return (
    <div
      className={`relative flex items-center gap-2 border text-white shadow-[0_8px_24px_rgba(0,0,0,0.22)] ${
        isSupervisor
          ? "h-[58px] w-[154px] rounded-lg border-cyan-300/70 bg-[#102b38] px-4"
          : "h-[46px] w-[128px] rounded-md border-white/15 bg-[#101923] px-3"
      } ${
        data.status === "completed" || data.status === "started"
          ? "shadow-[0_0_18px_rgba(45,212,191,0.12)]"
          : ""
      } ${data.status === "failed" ? "border-amber-300/60 bg-[#241d1b]" : ""} ${
        data.status === "inactive" ? "opacity-65" : ""
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!h-1.5 !w-1.5 !border-0 !bg-cyan-300/70"
      />
      <span
        className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[10px] font-semibold ${
          data.status === "failed"
            ? "border-amber-300/50 text-amber-200"
            : data.status === "inactive"
              ? "border-white/15 text-white/35"
              : "border-teal-300/50 text-teal-200"
        }`}
        aria-label={status.label}
      >
        {status.marker}
      </span>
      <span className={isSupervisor ? "text-sm font-semibold tracking-wide" : "text-xs font-medium tracking-wide"}>
        {data.label}
      </span>
      <Handle
        type="source"
        position={Position.Bottom}
        className="!h-1.5 !w-1.5 !border-0 !bg-cyan-300/70"
      />
    </div>
  );
}
