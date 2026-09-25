import { useEffect, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import {
  BarChart3,
  FileText,
  LayoutDashboard,
  LoaderCircle,
  MessageSquare,
  Plus,
  Sparkles,
  Trash2,
} from "lucide-react";

import { deleteConversation, listConversations } from "../../services/chatService.js";

const links = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/workspace", label: "AI Workspace", icon: Sparkles },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/reports", label: "Reports", icon: FileText },
];

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState([]);
  const [conversationsLoading, setConversationsLoading] = useState(true);
  const [conversationsError, setConversationsError] = useState(false);
  const [conversationDeleteError, setConversationDeleteError] = useState(false);
  const [deletingConversationId, setDeletingConversationId] = useState(null);
  const selectedConversationId = new URLSearchParams(location.search).get("conversation_id");

  function handleNewChat() {
    navigate("/workspace");
  }

  async function handleDeleteConversation(event, conversationId) {
    event.stopPropagation();

    if (deletingConversationId || !window.confirm("This conversation and all of its messages will be permanently deleted. Continue?")) {
      return;
    }

    setConversationDeleteError(false);
    setDeletingConversationId(conversationId);

    try {
      await deleteConversation(conversationId);
      setConversations((previous) =>
        previous.filter((conversation) => conversation.conversation_id !== conversationId)
      );

      if (conversationId === selectedConversationId) {
        navigate("/workspace");
      }
    } catch {
      setConversationDeleteError(true);
    } finally {
      setDeletingConversationId(null);
    }
  }

  useEffect(() => {
    async function fetchConversations() {
      try {
        const response = await listConversations();
        setConversations(Array.isArray(response?.conversations) ? response.conversations : []);
      } catch {
        setConversationsError(true);
      } finally {
        setConversationsLoading(false);
      }
    }

    fetchConversations();
  }, []);

  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-white/[0.07] bg-[#080d16] px-4 py-5">
      <div className="mb-10 flex items-center gap-3 px-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-300/20 bg-cyan-300/[0.08] text-cyan-200 shadow-[0_0_18px_rgba(103,232,249,0.08)]">
          <Sparkles size={16} strokeWidth={1.8} />
        </div>
        <span className="text-[15px] font-semibold tracking-[0.18em] text-white/90">
          AgentOS
        </span>
      </div>
      <nav className="flex flex-col gap-1.5" aria-label="Primary navigation">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              [
                "group flex items-center gap-3 rounded-lg border px-3 py-2.5 text-sm transition-all duration-200",
                isActive
                  ? "border-cyan-300/20 bg-white/[0.055] text-white shadow-[0_0_24px_rgba(45,212,191,0.07)]"
                  : "border-transparent text-white/45 hover:border-white/[0.06] hover:bg-white/[0.03] hover:text-white/80",
              ].join(" ")
            }
          >
            {({ isActive }) => (
              <>
                <link.icon
                  size={17}
                  strokeWidth={isActive ? 1.8 : 1.6}
                  className={
                    isActive
                      ? "text-cyan-200"
                      : "text-white/35 transition-colors duration-200 group-hover:text-white/65"
                  }
                />
                <span>{link.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
      <section className="mt-10" aria-labelledby="conversations-heading">
        <div className="mb-3 flex items-center gap-2 px-2">
          <MessageSquare size={14} className="text-cyan-200/55" strokeWidth={1.6} />
          <div className="flex min-w-0 flex-1 items-center justify-between gap-2">
            <h2
              id="conversations-heading"
              className="text-[11px] uppercase tracking-[0.18em] text-white/35"
            >
              Conversations
            </h2>
            <button
              type="button"
              onClick={handleNewChat}
              aria-label="Start a new chat"
              className="text-white/35 transition-colors hover:text-cyan-100/80"
            >
              <Plus size={15} strokeWidth={1.7} />
            </button>
          </div>
        </div>

        {conversationDeleteError && (
          <p className="mb-2 px-2 text-xs leading-5 text-red-100/65">
            Unable to delete conversation.
          </p>
        )}

        {conversationsLoading ? (
          <div className="flex items-center gap-2 px-2 text-xs text-white/30">
            <LoaderCircle size={13} className="animate-spin" strokeWidth={1.6} />
            Loading...
          </div>
        ) : conversationsError ? (
          <p className="px-2 text-xs leading-5 text-white/25">Unable to load conversations.</p>
        ) : conversations.length === 0 ? (
          <p className="px-2 text-xs leading-5 text-white/25">No conversations yet</p>
        ) : (
          <div className="flex flex-col gap-1">
            {conversations.map((conversation) => {
              const isSelected = conversation.conversation_id === selectedConversationId;
              const isDeleting = conversation.conversation_id === deletingConversationId;

              return (
                <div
                  key={conversation.conversation_id}
                  className={`group flex min-w-0 items-center gap-1 rounded-lg border px-2 py-1 text-xs transition-colors ${
                    isSelected
                      ? "border-cyan-300/15 bg-cyan-300/[0.06] text-cyan-100/80"
                      : "border-transparent text-white/50 hover:border-white/[0.06] hover:bg-white/[0.03] hover:text-white/75"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() =>
                      navigate(`/workspace?conversation_id=${encodeURIComponent(conversation.conversation_id)}`)
                    }
                    className="flex min-w-0 flex-1 items-center gap-2 py-1 text-left"
                    title={conversation.title || conversation.conversation_id}
                  >
                    <MessageSquare
                      size={14}
                      className={`shrink-0 ${isSelected ? "text-cyan-200/70" : "text-white/25 group-hover:text-white/55"}`}
                      strokeWidth={1.5}
                    />
                    <span className="truncate">{conversation.title || conversation.conversation_id}</span>
                  </button>
                  <button
                    type="button"
                    aria-label={`Delete ${conversation.title || conversation.conversation_id}`}
                    disabled={Boolean(deletingConversationId)}
                    onClick={(event) => handleDeleteConversation(event, conversation.conversation_id)}
                    className="shrink-0 p-1 text-white/25 transition-colors hover:text-red-200/80 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {isDeleting ? (
                      <LoaderCircle size={13} className="animate-spin" strokeWidth={1.6} />
                    ) : (
                      <Trash2 size={13} strokeWidth={1.6} />
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </aside>
  );
}
