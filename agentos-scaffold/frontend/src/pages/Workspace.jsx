import { useEffect, useRef, useState } from "react";
import {
  Check,
  LoaderCircle,
  Paperclip,
  Send,
  Sparkles,
  X,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { useChat } from "../hooks/useChat.js";
import { uploadFile } from "../services/uploadService.js";
import WorkflowVisualization from "../components/workflow/WorkflowVisualization.jsx";

const supportedFileTypes = ".pdf,.docx,.txt,.csv,.xls,.xlsx";

function formatSourceCitations(content, attachments) {
  const withoutContextCitations = content.replace(/【Context\s+\d+】|\[Context\s+\d+\]/gi, "");

  return withoutContextCitations.replace(/\[([^\]]+)\]/g, (citation, metadata) => {
    const source = metadata.split(",")[0].trim();
    const attachment = attachments.find(
      (item) =>
        item.status === "ready" &&
        item.fileId &&
        (source === item.fileId || source.startsWith(`${item.fileId}.`))
    );
    const generatedFilename = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\.[a-z0-9]+$/i.test(
      source
    );
    const hasRetrievalMetadata = /\b(?:Page\s+\d+|Chunk(?:\s+ID)?\s*:?)\b/i.test(metadata);

    if (!attachment && !(generatedFilename && hasRetrievalMetadata)) {
      return citation;
    }

    return "";
  });
}

const markdownComponents = {
  h1: ({ children }) => (
    <h1 className="mb-4 text-lg font-semibold tracking-tight text-white/95">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="mb-3 mt-6 text-base font-semibold tracking-tight text-cyan-50/90 first:mt-0">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="mb-2 mt-5 text-sm font-semibold text-white/90 first:mt-0">{children}</h3>
  ),
  p: ({ children }) => <p className="mb-4 last:mb-0 leading-7 text-white/70">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold text-white/95">{children}</strong>,
  ul: ({ children }) => <ul className="mb-4 list-disc space-y-2 pl-5 last:mb-0">{children}</ul>,
  ol: ({ children }) => <ol className="mb-4 list-decimal space-y-2 pl-5 last:mb-0">{children}</ol>,
  li: ({ children }) => <li className="pl-1 leading-6 text-white/70">{children}</li>,
  blockquote: ({ children }) => (
    <blockquote className="mb-4 border-l-2 border-cyan-200/30 pl-4 italic text-white/55">
      {children}
    </blockquote>
  ),
  table: ({ children }) => (
    <div className="mb-4 overflow-x-auto last:mb-0">
      <table className="min-w-full border-collapse text-left text-xs">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-white/[0.06] text-white/85">{children}</thead>,
  th: ({ children }) => (
    <th className="border border-white/[0.1] px-3 py-2 font-semibold">{children}</th>
  ),
  td: ({ children }) => (
    <td className="border border-white/[0.08] px-3 py-2 text-white/65">{children}</td>
  ),
  code: ({ inline, className, children, ...props }) =>
    inline ? (
      <code
        className="rounded border border-white/[0.08] bg-[#080e17] px-1.5 py-0.5 text-[0.9em] text-cyan-100/85"
        {...props}
      >
        {children}
      </code>
    ) : (
      <code
        className={`block min-w-max font-mono text-xs leading-6 text-white/75 ${className || ""}`}
        {...props}
      >
        {children}
      </code>
    ),
  pre: ({ children }) => (
    <pre className="mb-4 max-w-full overflow-x-auto border border-white/[0.08] bg-[#080e17] p-4 last:mb-0">
      {children}
    </pre>
  ),
  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="text-cyan-200/85 underline decoration-cyan-200/30 underline-offset-2 transition-colors hover:text-cyan-100"
    >
      {children}
    </a>
  ),
};

export default function Workspace() {
  const [input, setInput] = useState("");
  const [attachments, setAttachments] = useState([]);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const { messages, loading, error, workflowTrace, sendMessage } = useChat();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, error]);

  function handleSubmit(event) {
    event.preventDefault();
    const trimmedInput = input.trim();

    if (!trimmedInput || loading) {
      return;
    }

    const uploadedFileIds = attachments
      .filter((attachment) => attachment.status === "ready" && attachment.fileId)
      .map((attachment) => attachment.fileId);

    sendMessage(trimmedInput, uploadedFileIds);
    setInput("");
  }

  function handleFileSelection(event) {
    const selectedFiles = Array.from(event.target.files || []);
    event.target.value = "";

    if (selectedFiles.length === 0) {
      return;
    }

    const selectedAttachments = selectedFiles.map((file, index) => ({
      id: `${file.name}-${file.lastModified}-${Date.now()}-${index}`,
      name: file.name,
      fileId: null,
      status: "uploading",
      error: null,
    }));

    setAttachments((prev) => [...prev, ...selectedAttachments]);

    selectedFiles.forEach(async (file, index) => {
      const attachmentId = selectedAttachments[index].id;

      try {
        const response = await uploadFile(file);
        setAttachments((prev) =>
          prev.map((attachment) =>
            attachment.id === attachmentId
              ? { ...attachment, fileId: response.file_id, status: "ready", error: null }
              : attachment
          )
        );
      } catch (uploadError) {
        const detail = uploadError?.response?.data?.detail;
        setAttachments((prev) =>
          prev.map((attachment) =>
            attachment.id === attachmentId
              ? {
                  ...attachment,
                  status: "failed",
                  error:
                    typeof detail === "string" ? detail : "Upload failed. Remove and try again.",
                }
              : attachment
          )
        );
      }
    });
  }

  function removeAttachment(attachmentId) {
    setAttachments((prev) => prev.filter((attachment) => attachment.id !== attachmentId));
  }

  function handleInputKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form.requestSubmit();
    }
  }

  return (
    <div className="flex min-h-full flex-col gap-5 lg:grid lg:min-h-0 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
      <section className="flex min-h-[38rem] flex-col border border-white/[0.08] bg-[#0b121d]/75 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.14)] sm:p-7">
        <div>
          <div className="flex items-center gap-2.5">
            <Sparkles size={17} className="text-cyan-200/75" strokeWidth={1.6} />
            <h1 className="text-sm font-medium tracking-wide text-white/90">
              AI Workspace
            </h1>
          </div>
          <p className="mt-2 text-xs tracking-wide text-white/40">
            Coordinate tasks across your AgentOS intelligence layer.
          </p>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-1 py-8 sm:px-3 sm:py-10">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center px-4 text-center">
              <div className="max-w-md">
                <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center border border-cyan-200/20 bg-cyan-200/[0.06] text-cyan-100/80 shadow-[0_0_24px_rgba(103,232,249,0.08)]">
                  <Sparkles size={21} strokeWidth={1.5} />
                </div>
                <h2 className="text-lg font-medium tracking-wide text-white/85">
                  Start a conversation
                </h2>
                <p className="mt-3 text-sm leading-6 text-white/40">
                  Ask AgentOS to research, analyze data, search documents, or generate a report.
                </p>
              </div>
            </div>
          ) : (
            <div className="mx-auto flex max-w-3xl flex-col gap-4">
              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] border px-4 py-3 text-sm leading-6 ${
                      message.role === "user"
                        ? "border-cyan-200/20 bg-cyan-200/[0.09] text-cyan-50/90"
                        : "border-white/[0.08] bg-[#101925]/90 text-white/70"
                    }`}
                  >
                    {message.role === "assistant" ? (
                      <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                        {formatSourceCitations(message.content, attachments)}
                      </ReactMarkdown>
                    ) : (
                      message.content
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex items-center gap-2 text-xs text-cyan-100/55">
                  <LoaderCircle size={14} className="animate-spin" strokeWidth={1.7} />
                  AgentOS is processing...
                </div>
              )}
              {error && (
                <div className="border border-red-300/15 bg-red-300/[0.05] px-4 py-3 text-xs leading-5 text-red-100/70">
                  {error}
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
          {messages.length === 0 && error && (
            <div className="mx-auto mt-4 max-w-md border border-red-300/15 bg-red-300/[0.05] px-4 py-3 text-center text-xs leading-5 text-red-100/70">
              {error}
            </div>
          )}
          {messages.length === 0 && <div ref={messagesEndRef} />}
        </div>

        <form onSubmit={handleSubmit} className="border border-white/[0.1] bg-[#080e17]/90 p-2 shadow-[0_12px_35px_rgba(0,0,0,0.18)]">
          {attachments.length > 0 && (
            <div className="mb-2 flex flex-wrap gap-1.5 border-b border-white/[0.06] px-1 pb-2">
              {attachments.map((attachment) => (
                <div
                  key={attachment.id}
                  title={attachment.error || attachment.name}
                  className={`flex min-w-0 max-w-full items-center gap-1.5 border px-2 py-1 text-[11px] ${
                    attachment.status === "ready"
                      ? "border-teal-300/20 bg-teal-300/[0.06] text-teal-100/80"
                      : attachment.status === "failed"
                        ? "border-red-300/20 bg-red-300/[0.05] text-red-100/75"
                        : "border-white/[0.1] bg-white/[0.03] text-white/45"
                  }`}
                >
                  {attachment.status === "uploading" && (
                    <LoaderCircle size={12} className="shrink-0 animate-spin" strokeWidth={1.7} />
                  )}
                  {attachment.status === "ready" && (
                    <Check size={12} className="shrink-0 text-teal-200/80" strokeWidth={1.8} />
                  )}
                  {attachment.status === "failed" && (
                    <span className="shrink-0 text-red-200/80">!</span>
                  )}
                  <span className="max-w-[15rem] truncate">{attachment.name}</span>
                  <button
                    type="button"
                    aria-label={`Remove ${attachment.name}`}
                    onClick={() => removeAttachment(attachment.id)}
                    className="shrink-0 text-white/35 transition-colors hover:text-white/80"
                  >
                    <X size={13} strokeWidth={1.7} />
                  </button>
                </div>
              ))}
            </div>
          )}
          <div className="flex items-end gap-2">
            <button
              type="button"
              aria-label="Attach a file"
              onClick={() => fileInputRef.current?.click()}
              className="flex h-10 w-10 shrink-0 items-center justify-center text-white/35 transition-colors duration-200 hover:text-cyan-100/80"
            >
              <Paperclip size={17} strokeWidth={1.6} />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept={supportedFileTypes}
              onChange={handleFileSelection}
              className="hidden"
            />
            <textarea
              rows={1}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleInputKeyDown}
              placeholder="Ask AgentOS anything..."
              aria-label="Ask AgentOS anything"
              className="min-h-10 flex-1 resize-none bg-transparent px-1 py-2.5 text-sm text-white/70 outline-none placeholder:text-white/30"
            />
            <button
              type="submit"
              aria-label="Send message"
              disabled={loading || !input.trim()}
              className="flex h-10 w-10 shrink-0 items-center justify-center bg-cyan-200/[0.1] text-cyan-100/75 transition-colors duration-200 hover:bg-cyan-200/[0.18] hover:text-cyan-50 disabled:cursor-not-allowed disabled:opacity-35"
            >
              <Send size={16} strokeWidth={1.7} />
            </button>
          </div>
        </form>
      </section>

      <aside className="border border-white/[0.08] bg-[#0b121d]/75 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.14)] sm:p-7">
        <div className="mb-6">
          <h2 className="text-sm font-medium tracking-wide text-white/90">Agent Network</h2>
          <p className="mt-2 text-xs leading-5 text-white/40">
            Your specialized agents, coordinated by the Supervisor.
          </p>
        </div>
        <WorkflowVisualization workflowTrace={workflowTrace} />
      </aside>
    </div>
  );
}
