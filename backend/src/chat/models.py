from django.conf import settings
from django.db import models


class Message(models.Model):
    trip = models.ForeignKey(
        'trip.Trip',
        on_delete=models.CASCADE,
        related_name='messages',
    )
    booking = models.ForeignKey(
        'trip.Booking',
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,
        blank=True,
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages',
    )
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']  # cronológico — mais antigas primeiro

    def __str__(self) -> str:
        target = f"booking {self.booking_id}" if self.booking_id else f"trip {self.trip_id}"
        return f"Message {self.id} — {self.sender_id} → {target} @ {self.sent_at.isoformat()}"
