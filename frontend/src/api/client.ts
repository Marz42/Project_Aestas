import axios from "axios";

const apiKey = import.meta.env.VITE_API_KEY || "dev-api-key-change-me";

export const api = axios.create({
  baseURL: "",
  headers: {
    "X-API-Key": apiKey,
  },
});

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export async function unwrap<T>(promise: Promise<{ data: ApiResponse<T> }>): Promise<T> {
  const { data } = await promise;
  if (data.code !== 200) {
    throw new Error(data.message || "API error");
  }
  return data.data;
}
