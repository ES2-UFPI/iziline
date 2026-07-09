from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError

from chat.models import Message
from chat.selectors import is_booking_participant, is_trip_participant
from trip.models import Booking, Trip


def reservation_message_send(*, booking_id, sender, content):
    """Cria e persiste uma mensagem no chat 1:1 da reserva."""
    booking = get_object_or_404(
        Booking.objects.select_related("trip__driver__user", "passenger"),
        id=booking_id,
    )

    if not is_booking_participant(booking=booking, user=sender):
        raise PermissionDenied("Apenas motorista e passageiro desta reserva podem enviar mensagens.")

    if booking.status not in {Booking.Status.PENDING, Booking.Status.CONFIRMED}:
        raise ValidationError({"booking": "Só é possível conversar em reservas pendentes ou confirmadas."})

    normalized_content = content.strip()
    if not normalized_content:
        raise ValidationError({"content": "A mensagem não pode estar vazia."})

    if booking.trip.status == Trip.Status.CANCELLED:
        raise ValidationError({"trip": "Não é possível enviar mensagens em uma viagem cancelada."})

    return Message.objects.create(
        trip=booking.trip,
        booking=booking,
        sender=sender,
        content=normalized_content,
    )


def trip_message_send(*, trip_id, sender, content):
    """Cria e persiste uma mensagem no chat da viagem.

    Levanta Http404 se a viagem não existir.
    Levanta PermissionDenied se o sender não for participante da viagem.
    Levanta ValidationError se a viagem estiver cancelada.
    """
    trip = get_object_or_404(Trip.objects.select_related("driver"), id=trip_id)

    if not is_trip_participant(trip=trip, user=sender):
        raise PermissionDenied("Apenas participantes da viagem podem enviar mensagens.")

    normalized_content = content.strip()
    if not normalized_content:
        raise ValidationError({"content": "A mensagem não pode estar vazia."})

    if trip.status == Trip.Status.CANCELLED:
        raise ValidationError({"trip": "Não é possível enviar mensagens em uma viagem cancelada."})

    if trip.status == Trip.Status.FINISHED:
        raise ValidationError({"trip": "Não é possível enviar mensagens em uma viagem finalizada."})

    return Message.objects.create(trip=trip, sender=sender, content=normalized_content)
