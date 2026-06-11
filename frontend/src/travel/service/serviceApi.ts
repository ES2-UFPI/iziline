import type {
  CreateTripInput,
  CreateTripPayload,
  TripResponse
} from '../../types/trip'
import { apiClient } from "./apiClient";

export class ApiError extends Error {
  readonly status: number
  readonly body: unknown

  constructor(message: string, status: number, body?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

export function buildDepartureAt(date: string, time: string): string {
  const departureAt = new Date(`${date}T${time}`)

  if (Number.isNaN(departureAt.getTime())) {
    throw new ApiError('Data ou horario da viagem invalidos.', 0)
  }

  return departureAt.toISOString()
}

export async function createTrip(input: CreateTripInput): Promise<TripResponse> {
  const payload = buildCreateTripPayload(input);
  try {
    const { data } = await apiClient.post<TripResponse>("/api/trips/", payload);
    return data;
  } catch (err) {
    const anyErr = err as { response?: { status?: number; data?: unknown } };
    throw new ApiError(
      "Não foi possível criar a viagem.",
      anyErr?.response?.status ?? 0,
      anyErr?.response?.data,
    );
  }
}

function buildCreateTripPayload(input: CreateTripInput): CreateTripPayload {
  return {
    origin: input.origin.trim(),
    destination: input.destination.trim(),
    departure_at: buildDepartureAt(input.date, input.time),
    seats_available: input.availableSeats
  }
}

