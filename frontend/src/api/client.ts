import axios from "axios";
import type { Ticket, TicketDetail, User } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({ baseURL: API_BASE_URL });

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ---------------- Auth ----------------
export async function register(email: string, fullName: string, password: string) {
  const { data } = await apiClient.post<{ access_token: string }>("/auth/register", {
    email,
    full_name: fullName,
    password,
  });
  return data;
}

export async function login(email: string, password: string) {
  const { data } = await apiClient.post<{ access_token: string }>("/auth/login", { email, password });
  return data;
}

export async function fetchCurrentUser() {
  const { data } = await apiClient.get<User>("/auth/me");
  return data;
}

// ---------------- Chat ----------------
export async function sendChatMessage(message: string, ticketId?: number) {
  const { data } = await apiClient.post<{ ticket: TicketDetail }>("/chat/message", {
    message,
    ticket_id: ticketId ?? null,
  });
  return data.ticket;
}

// ---------------- Tickets ----------------
export async function listTickets() {
  const { data } = await apiClient.get<Ticket[]>("/tickets");
  return data;
}

export async function getTicket(ticketId: number) {
  const { data } = await apiClient.get<TicketDetail>(`/tickets/${ticketId}`);
  return data;
}
