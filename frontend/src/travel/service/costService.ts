import { apiClient } from "./apiClient";
import type { CreateTripInput, TripCostEstimate } from "../../types/trip";

type FareEstimateResponse = {
  distance_km: number;
  cost_per_km: string;
  total_cost: string;
  occupants: number;
  per_person: string;
};

export async function calculateTripCosts(
  input: CreateTripInput
): Promise<TripCostEstimate> {
  const { data } = await apiClient.get<FareEstimateResponse>(
    "/api/trips/fare-estimate/",
    {
      params: {
        origin: input.origin.trim(),
        destination: input.destination.trim(),
        seats_available: input.availableSeats,
      },
    }
  );
  return {
    distanceInKm: data.distance_km,
    costPerKm: data.cost_per_km,
    totalCost: data.total_cost,
    occupants: data.occupants,
    perPersonCost: data.per_person,
  };
}
