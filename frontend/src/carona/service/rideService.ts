import { apiClient } from "../../travel/service/apiClient";
import type { RideSearchFilters, RideSearchResult } from "../../types/ride";

type ApiTrip = {
  id: number;
  driver_name: string;
  origin: string;
  destination: string;
  departure_at: string;
  seats_available: number;
  price: string;
};

function mapTrip(t: ApiTrip): RideSearchResult {
  return {
    id: t.id,
    driverName: t.driver_name,
    origin: t.origin,
    destination: t.destination,
    departureAt: t.departure_at,
    seatsAvailable: t.seats_available,
    price: t.price,
  };
}

export async function searchRides(
  filters: RideSearchFilters
): Promise<RideSearchResult[]> {
  const params: Record<string, string> = {};
  if (filters.origin.trim()) params.origin = filters.origin.trim();
  if (filters.destination.trim()) params.destination = filters.destination.trim();
  if (filters.date) params.date = filters.date;

  const { data } = await apiClient.get<{ results: ApiTrip[] }>("/api/trips/", { params });
  return (data.results ?? []).map(mapTrip);
}
