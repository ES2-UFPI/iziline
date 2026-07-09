import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from trip.services import trip as trip_services


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def pending_booking(passenger_user, open_trip):
    stops = list(open_trip.stops.order_by("order"))
    return trip_services.create_booking_request(
        passenger=passenger_user,
        trip_id=open_trip.id,
        pickup_stop_id=stops[0].id,
        dropoff_stop_id=stops[-1].id,
    )


@pytest.fixture
def driver_user(driver_profile):
    return driver_profile.user


@pytest.fixture
def confirmed_booking(pending_booking, driver_profile):
    return trip_services.accept_booking_request(
        booking_id=pending_booking.id,
        driver_profile_id=driver_profile.id,
    )


class TestBookingMessagesApi:
    def test_participants_can_exchange_messages_on_pending_booking(
        self, api_client, driver_user, passenger_user, pending_booking
    ):
        api_client.force_authenticate(user=passenger_user)
        send_response = api_client.post(
            f"/api/bookings/{pending_booking.id}/messages/",
            {"content": "  Oi motorista  "},
            format="json",
        )

        assert send_response.status_code == 201
        assert send_response.data["content"] == "Oi motorista"
        assert send_response.data["sender_id"] == passenger_user.id
        assert send_response.data["sender_name"] == passenger_user.full_name

        api_client.force_authenticate(user=driver_user)
        list_response = api_client.get(f"/api/bookings/{pending_booking.id}/messages/")

        assert list_response.status_code == 200
        assert [item["content"] for item in list_response.data] == ["Oi motorista"]

    def test_supports_incremental_polling_with_after(
        self, api_client, passenger_user, pending_booking
    ):
        api_client.force_authenticate(user=passenger_user)
        first = api_client.post(
            f"/api/bookings/{pending_booking.id}/messages/",
            {"content": "Primeira"},
            format="json",
        )
        second = api_client.post(
            f"/api/bookings/{pending_booking.id}/messages/",
            {"content": "Segunda"},
            format="json",
        )

        response = api_client.get(
            f"/api/bookings/{pending_booking.id}/messages/",
            {"after": first.data["id"]},
        )

        assert response.status_code == 200
        assert [item["id"] for item in response.data] == [second.data["id"]]

    def test_returns_403_for_non_participant(
        self, api_client, django_user_model, pending_booking
    ):
        outsider = django_user_model.objects.create_user(username="chat-outsider", password="x")
        api_client.force_authenticate(user=outsider)

        response = api_client.get(f"/api/bookings/{pending_booking.id}/messages/")

        assert response.status_code == 403

    def test_blocks_chat_for_cancelled_booking(
        self, api_client, passenger_user, pending_booking
    ):
        trip_services.cancel_booking_request(booking_id=pending_booking.id, passenger=passenger_user)
        api_client.force_authenticate(user=passenger_user)

        response = api_client.post(
            f"/api/bookings/{pending_booking.id}/messages/",
            {"content": "Ainda consigo falar?"},
            format="json",
        )

        assert response.status_code == 400
        assert "reservas pendentes ou confirmadas" in str(response.data)


class TestTripMessagesApi:
    def test_driver_and_confirmed_passenger_can_chat(
        self, api_client, driver_user, passenger_user, open_trip, confirmed_booking
    ):
        api_client.force_authenticate(user=driver_user)
        send_response = api_client.post(
            f"/api/trips/{open_trip.id}/messages/",
            {"content": "Partimos em 10 minutos"},
            format="json",
        )

        assert send_response.status_code == 201
        assert send_response.data["sender_id"] == driver_user.id

        api_client.force_authenticate(user=passenger_user)
        list_response = api_client.get(f"/api/trips/{open_trip.id}/messages/")

        assert list_response.status_code == 200
        assert [item["content"] for item in list_response.data] == ["Partimos em 10 minutos"]

    def test_pending_passenger_cannot_access_trip_chat(
        self, api_client, passenger_user, open_trip, pending_booking
    ):
        api_client.force_authenticate(user=passenger_user)

        response = api_client.get(f"/api/trips/{open_trip.id}/messages/")

        assert response.status_code == 403

    def test_trip_chat_ignores_reservation_messages(
        self, api_client, driver_user, passenger_user, open_trip, confirmed_booking
    ):
        api_client.force_authenticate(user=passenger_user)
        api_client.post(
            f"/api/bookings/{confirmed_booking.id}/messages/",
            {"content": "Mensagem privada"},
            format="json",
        )

        api_client.force_authenticate(user=driver_user)
        api_client.post(
            f"/api/trips/{open_trip.id}/messages/",
            {"content": "Mensagem em grupo"},
            format="json",
        )

        api_client.force_authenticate(user=passenger_user)
        response = api_client.get(f"/api/trips/{open_trip.id}/messages/")

        assert response.status_code == 200
        assert [item["content"] for item in response.data] == ["Mensagem em grupo"]

    def test_blocks_send_when_trip_is_finished(
        self, api_client, driver_user, driver_profile, passenger_user, open_trip, confirmed_booking
    ):
        open_trip.departure_time = timezone.now()
        open_trip.save(update_fields=["departure_time"])
        trip_services.start_trip(trip_id=open_trip.id, driver_profile_id=driver_profile.id)
        trip_services.finish_trip(trip_id=open_trip.id, driver_profile_id=driver_profile.id)
        api_client.force_authenticate(user=driver_user)

        response = api_client.post(
            f"/api/trips/{open_trip.id}/messages/",
            {"content": "Cheguei"},
            format="json",
        )

        assert response.status_code == 400
        assert "viagem finalizada" in str(response.data)
