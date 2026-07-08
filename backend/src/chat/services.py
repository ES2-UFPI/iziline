from rest_framework.exceptions import ValidationError

from chat.models import Message
from chat.selectors import get_booking_for_chat, get_trip_for_chat
from trip.models import Trip


def _clean_content(content: str) -> str:
    content = (content or "").strip()
    if not content:
        raise ValidationError({"content": "A mensagem não pode ser vazia."})
    return content


def message_send(*, trip_id: int, sender, content: str) -> Message:
    trip = get_trip_for_chat(trip_id=trip_id, user=sender)
    if trip.status == Trip.Status.CANCELLED:
        raise ValidationError({"trip": "Não é possível enviar mensagens em uma viagem cancelada."})

    return Message.objects.create(
        trip=trip,
        sender=sender,
        content=_clean_content(content),
    )


def reservation_message_send(*, booking_id: int, sender, content: str) -> Message:
    booking = get_booking_for_chat(booking_id=booking_id, user=sender)
    if booking.status == booking.Status.CANCELLED:
        raise ValidationError({"booking": "Não é possível enviar mensagens em uma reserva cancelada."})

    return Message.objects.create(
        trip=booking.trip,
        booking=booking,
        sender=sender,
        content=_clean_content(content),
    )
