from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from chat.models import Message
from trip.models import Booking, Trip


def is_trip_participant(*, trip: Trip, user) -> bool:
    """Motorista e passageiros confirmados participam do chat da viagem."""
    if trip.driver and trip.driver.user_id == user.id:
        return True

    return Booking.objects.filter(
        trip=trip,
        passenger=user,
        status=Booking.Status.CONFIRMED,
    ).exists()


def is_booking_participant(*, booking: Booking, user) -> bool:
    """Motorista da viagem e passageiro da reserva participam do chat 1:1."""
    if booking.passenger_id == user.id:
        return True

    return bool(booking.trip.driver and booking.trip.driver.user_id == user.id)


def get_trip_for_chat(*, trip_id: int, user) -> Trip:
    trip = get_object_or_404(
        Trip.objects.select_related("driver"),
        id=trip_id,
    )
    if not is_trip_participant(trip=trip, user=user):
        raise PermissionDenied("Apenas participantes da viagem podem acessar o chat.")
    return trip


def get_booking_for_chat(*, booking_id: int, user) -> Booking:
    booking = get_object_or_404(
        Booking.objects.select_related("trip__driver", "passenger"),
        id=booking_id,
    )
    if not is_booking_participant(booking=booking, user=user):
        raise PermissionDenied("Apenas participantes da reserva podem acessar o chat.")
    return booking


def message_list(*, trip_id: int, user, after_id: int | None = None):
    trip = get_trip_for_chat(trip_id=trip_id, user=user)
    qs = Message.objects.filter(trip=trip, booking__isnull=True).select_related("sender")
    if after_id is not None:
        qs = qs.filter(id__gt=after_id)
    return qs.order_by("sent_at", "id")


def reservation_message_list(*, booking_id: int, user, after_id: int | None = None):
    booking = get_booking_for_chat(booking_id=booking_id, user=user)
    qs = Message.objects.filter(booking=booking).select_related("sender")
    if after_id is not None:
        qs = qs.filter(id__gt=after_id)
    return qs.order_by("sent_at", "id")
