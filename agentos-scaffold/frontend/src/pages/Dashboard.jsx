import {
  BarChart3,
  FileSearch,
  FileText,
  MessageSquare,
  Network,
  Search,
  Sparkles,
  Workflow,
} from "lucide-react";

const agents = [
  {
    name: "Chat Agent",
    description: "Conversations",
    icon: MessageSquare,
    position: "left-0 top-[10%] lg:left-[7%] lg:top-[18%]",
  },
  {
    name: "Research Agent",
    description: "Deep research",
    icon: Search,
    position: "right-0 top-[10%] lg:right-[7%] lg:top-[18%]",
  },
  {
    name: "RAG Agent",
    description: "Knowledge retrieval",
    icon: FileSearch,
    position: "left-0 bottom-[10%] lg:left-[7%] lg:bottom-[17%]",
  },
  {
    name: "Analytics Agent",
    description: "Data analysis",
    icon: BarChart3,
    position: "right-0 bottom-[10%] lg:right-[7%] lg:bottom-[17%]",
  },
  {
    name: "Document Agent",
    description: "Document intelligence",
    icon: FileText,
    position: "left-1/2 top-[13%] -translate-x-1/2 lg:top-[10%]",
  },
];

const actions = [
  { label: "Ask Anything", icon: MessageSquare },
  { label: "Analyze Data", icon: BarChart3 },
  { label: "Research Topics", icon: Search },
  { label: "Search Documents", icon: FileSearch },
  { label: "Generate Reports", icon: FileText },
];

function AgentNode({ agent }) {
  const Icon = agent.icon;

  return (
    <div
      className={`absolute w-[43%] max-w-52 -translate-y-1/2 lg:w-44 ${agent.position}`}
    >
      <div className="group relative border border-white/[0.1] bg-[#101925]/90 px-3 py-3 shadow-[0_14px_35px_rgba(0,0,0,0.2)] backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:border-cyan-200/30 hover:bg-[#132231] hover:shadow-[0_14px_35px_rgba(45,212,191,0.1)]">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center border border-cyan-200/15 bg-cyan-200/[0.06] text-cyan-200/80">
            <Icon size={15} strokeWidth={1.7} />
          </div>
          <div className="min-w-0">
            <p className="truncate text-xs font-medium text-white/85">{agent.name}</p>
            <p className="mt-1 truncate text-[10px] tracking-wide text-white/35">
              {agent.description}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  return (
    <div className="mx-auto w-full max-w-7xl pb-8">
      <section className="mb-10 pt-2 sm:mb-12 sm:pt-4">
        <p className="mb-4 text-[10px] font-medium uppercase tracking-[0.3em] text-cyan-200/55">
          Command Center
        </p>
        <h1 className="text-3xl font-light tracking-[-0.02em] text-white sm:text-4xl">
          Welcome to <span className="font-medium text-white/90">AgentOS</span>
        </h1>
        <p className="mt-3 text-sm tracking-wide text-white/45">
          Your multi-agent AI operating system.
        </p>
      </section>

      <section className="mb-12 border border-white/[0.09] bg-[#0b121d]/80 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.18)] sm:p-7 lg:p-8">
        <div className="mb-7 flex items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <Network size={17} className="text-cyan-200/75" strokeWidth={1.6} />
              <h2 className="text-sm font-medium tracking-wide text-white/85">
                Agent Network
              </h2>
            </div>
            <p className="mt-2 text-xs text-white/35">
              A unified intelligence layer for your work.
            </p>
          </div>
          <Workflow size={18} className="text-white/20" strokeWidth={1.5} />
        </div>

        <div className="relative h-[20rem] overflow-hidden border border-white/[0.06] bg-[#080e17] sm:h-[22rem]">
          <div className="pointer-events-none absolute inset-0 opacity-60 [background-image:linear-gradient(rgba(255,255,255,0.025)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.025)_1px,transparent_1px)] [background-size:38px_38px]" />

          <div className="pointer-events-none absolute left-[21%] top-[31%] h-px w-[27%] origin-left rotate-[18deg] bg-cyan-200/20 shadow-[0_0_10px_rgba(103,232,249,0.25)] lg:left-[18%] lg:top-[31%] lg:w-[27%] lg:rotate-[17deg]" />
          <div className="pointer-events-none absolute right-[21%] top-[31%] h-px w-[27%] origin-right -rotate-[18deg] bg-cyan-200/20 shadow-[0_0_10px_rgba(103,232,249,0.25)] lg:right-[18%] lg:top-[31%] lg:w-[27%] lg:-rotate-[17deg]" />
          <div className="pointer-events-none absolute bottom-[31%] left-[21%] h-px w-[27%] origin-left -rotate-[18deg] bg-cyan-200/20 shadow-[0_0_10px_rgba(103,232,249,0.25)] lg:bottom-[31%] lg:left-[18%] lg:w-[27%] lg:-rotate-[17deg]" />
          <div className="pointer-events-none absolute right-[21%] bottom-[31%] h-px w-[27%] origin-right rotate-[18deg] bg-cyan-200/20 shadow-[0_0_10px_rgba(103,232,249,0.25)] lg:right-[18%] lg:bottom-[31%] lg:w-[27%] lg:rotate-[17deg]" />
          <div className="pointer-events-none absolute left-1/2 top-[11%] h-[28%] w-px -translate-x-1/2 bg-amber-200/20 shadow-[0_0_10px_rgba(253,230,138,0.2)]" />

          <div className="absolute left-1/2 top-1/2 w-48 -translate-x-1/2 -translate-y-1/2 sm:w-56">
            <div className="border border-cyan-200/35 bg-[#122331] px-5 py-5 text-center shadow-[0_0_45px_rgba(45,212,191,0.13)]">
              <div className="mx-auto mb-3 flex h-11 w-11 items-center justify-center border border-cyan-200/25 bg-cyan-200/[0.08] text-cyan-100 shadow-[0_0_22px_rgba(103,232,249,0.12)]">
                <Sparkles size={20} strokeWidth={1.5} />
              </div>
              <p className="text-sm font-medium text-white">Supervisor Agent</p>
              <p className="mt-1.5 text-[10px] uppercase tracking-[0.18em] text-cyan-100/55">
                Orchestration core
              </p>
            </div>
          </div>

          {agents.map((agent) => (
            <AgentNode key={agent.name} agent={agent} />
          ))}
        </div>
      </section>

      <section>
        <div className="mb-5 flex items-end justify-between gap-4">
          <div>
            <p className="text-[10px] font-medium uppercase tracking-[0.28em] text-white/30">
              Start with intent
            </p>
            <h2 className="mt-2 text-lg font-medium text-white/85">Quick Actions</h2>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {actions.map((action) => {
            const Icon = action.icon;

            return (
              <div
                key={action.label}
                className="group border border-white/[0.09] bg-[#0c141f]/75 px-4 py-5 transition-all duration-300 hover:-translate-y-0.5 hover:border-cyan-200/25 hover:bg-[#101d2a] hover:shadow-[0_12px_30px_rgba(45,212,191,0.07)]"
              >
                <Icon
                  size={18}
                  strokeWidth={1.6}
                  className="mb-5 text-cyan-200/65 transition-colors duration-300 group-hover:text-cyan-100"
                />
                <p className="text-xs font-medium tracking-wide text-white/75">{action.label}</p>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
