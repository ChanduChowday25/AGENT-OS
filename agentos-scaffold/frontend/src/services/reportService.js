import api from "./api.js";

export async function listReports() {
  const { data } = await api.get("/reports");
  return data;
}

export async function downloadReport(reportId) {
  const response = await api.get(
    `/reports/${reportId}/download`,
    {
      responseType: "blob",
    }
  );

  return response.data;
}

export async function deleteReport(reportId) {
  const { data } = await api.delete(
    `/reports/${reportId}`
  );

  return data;
}