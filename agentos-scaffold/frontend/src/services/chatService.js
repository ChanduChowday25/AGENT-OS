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
