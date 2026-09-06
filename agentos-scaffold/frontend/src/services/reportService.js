import api from "./api.js";

export async function listReports() {
  const { data } = await api.get("/reports");
  return data;
}
