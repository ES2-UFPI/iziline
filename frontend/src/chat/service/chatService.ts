// Camada de serviço do chat. Segue o padrão do projeto: ramo mock
// (VITE_USE_MOCK=true, sem backend) + ramo real que fala com a API.

import { apiClient } from "../../app/services/apiClient";
import { ApiError, buildApiError } from "../../app/services/apiError";
import { mockListMessages, mockSendMessage } from "../mocks/chat.mock";
import type { ChatMessage } from "../../types/chat";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";
const EMPTY_MESSAGE_ERROR = "Digite uma mensagem antes de enviar.";

function mockDelay(ms = 260): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function buildAfterParams(afterId?: number): { after: number } | undefined {
  return afterId == null ? undefined : { after: afterId };
}

function normalizeMessageContent(content: string): string {
  const trimmed = content.trim();
  if (!trimmed) {
    throw new ApiError(EMPTY_MESSAGE_ERROR, 400);
  }
  return trimmed;
}

// --- Chat da reserva (motorista ↔ passageiro) ------------------------------

export async function listReservationMessages(
  bookingId: number,
  afterId?: number
): Promise<ChatMessage[]> {
  if (USE_MOCK) {
    await mockDelay();
    return mockListMessages(`reservation:${bookingId}`, afterId);
  }

  try {
    const { data } = await apiClient.get<ChatMessage[]>(
      `/api/bookings/${bookingId}/messages/`,
      { params: buildAfterParams(afterId) }
    );
    return data;
  } catch (error) {
    throw buildApiError(error, "Não foi possível carregar a conversa.");
  }
}

export async function sendReservationMessage(
  bookingId: number,
  content: string
): Promise<ChatMessage> {
  const messageContent = normalizeMessageContent(content);

  if (USE_MOCK) {
    await mockDelay(160);
    return mockSendMessage(`reservation:${bookingId}`, messageContent);
  }

  try {
    const { data } = await apiClient.post<ChatMessage>(
      `/api/bookings/${bookingId}/messages/`,
      { content: messageContent }
    );
    return data;
  } catch (error) {
    throw buildApiError(error, "Não foi possível enviar a mensagem.");
  }
}

// --- Chat da viagem (motorista + passageiros confirmados) ------------------

export async function listTripMessages(
  tripId: number,
  afterId?: number
): Promise<ChatMessage[]> {
  if (USE_MOCK) {
    await mockDelay();
    return mockListMessages(`trip:${tripId}`, afterId);
  }

  try {
    const { data } = await apiClient.get<ChatMessage[]>(
      `/api/trips/${tripId}/messages/`,
      { params: buildAfterParams(afterId) }
    );
    return data;
  } catch (error) {
    throw buildApiError(error, "Não foi possível carregar a conversa.");
  }
}

export async function sendTripMessage(
  tripId: number,
  content: string
): Promise<ChatMessage> {
  const messageContent = normalizeMessageContent(content);

  if (USE_MOCK) {
    await mockDelay(160);
    return mockSendMessage(`trip:${tripId}`, messageContent);
  }

  try {
    const { data } = await apiClient.post<ChatMessage>(
      `/api/trips/${tripId}/messages/`,
      { content: messageContent }
    );
    return data;
  } catch (error) {
    throw buildApiError(error, "Não foi possível enviar a mensagem.");
  }
}
