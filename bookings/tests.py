from django.test import TestCase

# Create your tests here.



from datetime import time, timedelta
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from bookings.models import Booking
from services.models import (
    AutoService,
    MechanicProfile,
    ServiceCategory,
    ServiceCentre,
)
from vehicles.models import Vehicles


User = get_user_model()


class BookingStatusAndPermissionTest(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client",
            password="StrongPassword123!",
        )
        self.service_owner = User.objects.create_user(
            username="service_owner",
            password="StrongPassword123!",
        )
        self.mechanic_user = User.objects.create_user(
            username="mechanic",
            password="StrongPassword123!",
        )
        self.other_user = User.objects.create_user(
            username="other_user",
            password="StrongPassword123!",
        )

        self.vehicle = Vehicles.objects.create(
            owner=self.client_user,
            brand="Chevrolet",
            model="Cobalt",
            year=2024,
            plate_number="01A777AA",
            color="White",
        )

        self.service_centre = ServiceCentre.objects.create(
            owner=self.service_owner,
            name="Test Auto Service",
            description="Test service centre",
            address="Tashkent",
            phone_number="+998901234567",
            opening_time=time(9, 0),
            closing_time=time(18, 0),
        )

        self.category = ServiceCategory.objects.create(
            name="Engine repair",
            description="Engine maintenance",
        )

        self.auto_service = AutoService.objects.create(
            service_centre=self.service_centre,
            category=self.category,
            name="Oil change",
            description="Engine oil replacement",
            price="150000.00",
            duration_minutes=30,
        )

        self.mechanic = MechanicProfile.objects.create(
            user=self.mechanic_user,
            service_centre=self.service_centre,
            specialization="Engine specialist",
            experience_years=3,
        )

        current_time = timezone.now()

        self.booking = Booking.objects.create(
            client=self.client_user,
            vehicle=self.vehicle,
            auto_service=self.auto_service,
            booking_date=timezone.localdate() + timedelta(days=1),
            booking_time=time(12, 0),
            status=Booking.Status.PENDING,
            created_at=current_time,
            updated_at=current_time,
        )

        self.change_status_url = (
            f"/api/bookings/{self.booking.id}/change-status/"
        )

    @patch("bookings.views.async_to_sync")
    @patch("bookings.views.get_channel_layer")
    def test_service_owner_can_accept_booking(
        self,
        mock_channel_layer,
        mock_async_to_sync,
    ):
        mock_async_to_sync.return_value = Mock()

        self.client.force_authenticate(user=self.service_owner)

        response = self.client.patch(
            self.change_status_url,
            {
                "status": Booking.Status.ACCEPTED,
                "mechanic": self.mechanic.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            Booking.Status.ACCEPTED,
        )
        self.assertEqual(
            self.booking.mechanic,
            self.mechanic,
        )

    def test_other_user_cannot_change_booking_status(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            self.change_status_url,
            {
                "status": Booking.Status.ACCEPTED,
                "mechanic": self.mechanic.id,
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            (
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND,
            ),
        )

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            Booking.Status.PENDING,
        )

    def test_booking_cannot_be_accepted_without_mechanic(self):
        self.client.force_authenticate(user=self.service_owner)

        response = self.client.patch(
            self.change_status_url,
            {
                "status": Booking.Status.ACCEPTED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("mechanic", response.data)

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            Booking.Status.PENDING,
        )

    @patch("bookings.views.async_to_sync")
    @patch("bookings.views.get_channel_layer")
    def test_booking_cannot_be_accepted_without_mechanic(
            self,
            mock_channel_layer,
            mock_async_to_sync,
    ):
        mock_async_to_sync.return_value = Mock()

        self.client.force_authenticate(user=self.service_owner)

        response = self.client.patch(
            self.change_status_url,
            {
                "status": Booking.Status.ACCEPTED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("mechanic", response.data)

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            Booking.Status.PENDING,
        )