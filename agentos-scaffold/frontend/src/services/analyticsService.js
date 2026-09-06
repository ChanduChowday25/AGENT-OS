import api from "./api.js";

export async function analyzeFile(payload) {
  // payload: { file_id, instructions }
  const { data } = await api.post("/analyze", payload);
  return data;
}
