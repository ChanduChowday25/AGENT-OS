import { useState, useCallback } from "react";
import { sendChatMessage } from "../services/chatService.js";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [error, setError] = useState(null);
  const [workflowTrace, setWorkflowTrace] = useState([]);

  const sendMessage = useCallback(async (query, uploadedFileIds = []) => {
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      return;
    }

    setMessages((prev) => [...prev, { role: "user", content: trimmedQuery }]);
    setError(null);
    setWorkflowTrace([]);
    setLoading(true);

    try {
      const response = await sendChatMessage({
        query: trimmedQuery,
        conversation_id: conversationId,
        uploaded_file_ids: uploadedFileIds,
      });

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.final_response },
      ]);
      setConversationId(response.conversation_id);
      setWorkflowTrace(response.workflow_trace || []);
    } catch (requestError) {
      const detail = requestError?.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : "AgentOS could not process the request. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }, [conversationId]);

  return { messages, loading, conversationId, error, workflowTrace, sendMessage };
}
