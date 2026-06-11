from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from trip.selectors import trip_get, trip_list
from trip.serializers import (
    FareEstimateSerializer,
    TripCreateSerializer,
    TripDetailSerializer,
    TripListFilterSerializer,
    TripListSerializer,
)
from trip.services import fare_breakdown, trip_cancel, trip_create


class TripPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class TripListCreateApi(APIView):
    def get(self, request):
        filters = TripListFilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        trips = trip_list(**filters.validated_data)
        paginator = TripPagination()
        page = paginator.paginate_queryset(trips, request)
        serializer = TripListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = TripCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trip = trip_create(driver=request.user, **serializer.validated_data)
        return Response(TripDetailSerializer(trip).data, status=status.HTTP_201_CREATED)


class TripDetailApi(APIView):
    def get(self, request, trip_id):
        trip = trip_get(trip_id=trip_id)
        return Response(TripDetailSerializer(trip).data)


class TripCancelApi(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, trip_id):
        trip = trip_cancel(trip_id=trip_id, user=request.user)
        return Response(TripDetailSerializer(trip).data)


class FareEstimateApi(APIView):
    def get(self, request):
        filters = FareEstimateSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        data = fare_breakdown(**filters.validated_data)
        return Response({
            "distance_km": data["distance_km"],
            "cost_per_km": str(data["cost_per_km"]),
            "total_cost": str(data["total_cost"]),
            "occupants": data["occupants"],
            "per_person": str(data["per_person"]),
        })