from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError

from chat.models import Message
from trip.models import Booking, Trip


def is_trip_participant(*, trip, user):
    """Retorna True se o user é motorista ou passageiro confirmado da viagem."""
    if trip.driver and trip.driver.user_id == user.id:
        return True
    return Booking.objects.filter(
        trip=trip,
        passenger=user,
        status=Booking.Status.CONFIRMED,
    ).exists()


def is_booking_participant(*, booking, user):
    if booking.passenger_id == user.id:
        return True
    return bool(booking.trip.driver and booking.trip.driver.user_id == user.id)


def reservation_message_list(*, booking_id, user, after_id=None):
    """Retorna as mensagens do chat 1:1 da reserva em ordem cronológica."""
    booking = get_object_or_404(
        Booking.objects.select_related("trip__driver__user", "passenger"),
        id=booking_id,
    )

    if not is_booking_participant(booking=booking, user=user):
        raise PermissionDenied("Apenas motorista e passageiro desta reserva podem ler as mensagens.")

    if booking.status not in {Booking.Status.PENDING, Booking.Status.CONFIRMED}:
        raise ValidationError({"booking": "A conversa da reserva só fica disponível para reservas pendentes ou confirmadas."})

    messages = Message.objects.filter(booking=booking).select_related("sender").order_by("sent_at", "id")
    if after_id is not None:
        messages = messages.filter(id__gt=after_id)
    return messages


def trip_message_list(*, trip_id, user, after_id=None):
    """Retorna as mensagens do chat em grupo da viagem em ordem cronológica."""
    trip = get_object_or_404(Trip.objects.select_related("driver"), id=trip_id)

    if not is_trip_participant(trip=trip, user=user):
        raise PermissionDenied("Apenas participantes da viagem podem ler as mensagens.")

    messages = (
        Message.objects.filter(trip=trip, booking__isnull=True)
        .select_related("sender")
        .order_by("sent_at", "id")
    )
    if after_id is not None:
        messages = messages.filter(id__gt=after_id)
    return messages
