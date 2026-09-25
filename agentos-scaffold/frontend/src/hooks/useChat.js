import { useState, useCallback } from "react";
import { getConversation, sendChatMessage } from "../services/chatService.js";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [error, setError] = useState(null);
  const [workflowTrace, setWorkflowTrace] = useState([]);

  const loadConversation = useCallback(async (selectedConversationId) => {
    if (!selectedConversationId) {
      return;
    }

    setError(null);
    setWorkflowTrace([]);
    setLoading(true);

    try {
      const response = await getConversation(selectedConversationId);
      setMessages(
        Array.isArray(response?.messages)
          ? response.messages.map(({ role, content }) => ({ role, content }))
          : []
      );
      setConversationId(response?.conversation_id || selectedConversationId);
    } catch (requestError) {
      const detail = requestError?.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : "AgentOS could not load the conversation. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }, []);

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

  return {
    messages,
    loading,
    conversationId,
    error,
    workflowTrace,
    sendMessage,
    loadConversation,
  };
}
