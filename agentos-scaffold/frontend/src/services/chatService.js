import api from "./api.js";

export async function sendChatMessage(payload) {
  // payload: { query, conversation_id, uploaded_file_ids }
  const { data } = await api.post("/chat", payload);
  return data;
}

export async function listConversations() {
  const { data } = await api.get("/conversations");
  return data;
}

export async function getConversation(conversationId) {
  const { data } = await api.get(`/conversations/${conversationId}`);
  return data;
}

export async function deleteConversation(conversationId) {
  const { data } = await api.delete(`/conversations/${conversationId}`);
  return data;
}
