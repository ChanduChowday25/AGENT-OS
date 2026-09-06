import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const api = axios.create({ baseURL });

export default api;
