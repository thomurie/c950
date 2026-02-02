# package.py
# Package class for WGUPS Package Routing Program
# Stores all package data and tracks delivery status
from __future__ import annotations

from enum import Enum
from typing import Optional
from datetime import datetime


class PackageStatus(Enum):
    ATHUB = "at the hub"
    ENROUTE = "en route"
    DELIVERED = "delivered"


class Package:
    """
    Represents a package in the WGUPS delivery system.

    Stores all package information including:
        - Identification (ID)
        - Delivery location (address, city, state, zip)
        - Delivery requirements (deadline, weight, special notes)
        - Delivery tracking (status, time, assigned truck)
    """

    def __init__(
        self,
        package_id: int,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        deadline: str,
        weight: int,
        notes="",
        status: PackageStatus = PackageStatus.ATHUB,
    ):
        """
        Initialize a new package with all required attributes.
        """
        # Inserted data
        self.package_id = int(package_id)
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = int(weight)
        self.notes = notes if notes else ""

        # Non inserted data
        self.status: PackageStatus = status
        self.delivery_time: Optional[datetime] = None
        self.departure_time: Optional[datetime] = None
        self.truck_id: Optional[int] = None

    def update_status(self, status: PackageStatus, time: Optional[datetime] = None):
        """
        Update the delivery status of the package.
        """
        self.status = status
        if status == PackageStatus.DELIVERED and time:
            self.delivery_time = time
        elif status == PackageStatus.ENROUTE and time:
            self.departure_time = time

    def has_deadline(self) -> bool:
        """
        Check if the package has a specific deadline (not EOD).
        """
        return self.deadline != "EOD"

    def is_delayed(self) -> bool:
        """
        Check if the package is delayed (arrives to depot late).
        """
        return "Delayed" in self.notes or "will not arrive" in self.notes.lower()

    def requires_truck_2(self) -> bool:
        """
        Check if the package must be on truck 2.
        """
        return "truck 2" in self.notes.lower()

    def has_wrong_address(self) -> bool:
        """
        Check if the package has a wrong address that needs correction.
        """
        return "wrong address" in self.notes.lower()

    def get_linked_packages(self) -> list[int]:
        """
        Get list of package IDs that must be delivered with this package.
        Example format: "Must be delivered with 13, 15"
        """
        if "Must be delivered with" not in self.notes:
            return []

        # Parse the package IDs from the notes
        try:
            parts = self.notes.split("Must be delivered with")[1].strip()
            # Split by space and convert to integers
            linked_ids = [int(x) for x in parts.split(",")]

            return linked_ids
        except (ValueError, IndexError):
            return []

    def get_status_at_time(self, query_time: datetime) -> PackageStatus:
        """
        Get the package status at a specific point in time.
        """
        if self.departure_time is None:
            return PackageStatus.ATHUB

        if query_time < self.departure_time:
            return PackageStatus.ATHUB

        if self.delivery_time and query_time >= self.delivery_time:
            return PackageStatus.DELIVERED

        return PackageStatus.ENROUTE

    def _format_time(self, time_obj: datetime) -> str:
        """
        Format a datetime object to a readable time string.
        """
        if time_obj is None:
            return "--"
        return time_obj.strftime("%-I:%M %p")

    def display_at_time(self, query_time: Optional[datetime] = None) -> str:
        """
        Return package data formatted for table display.
        """
        if query_time:
            status = self.get_status_at_time(query_time)
            # For delivery time, only show if delivered before query time
            if status == PackageStatus.DELIVERED and self.delivery_time:
                delivery_time_str = self._format_time(self.delivery_time)
            else:
                delivery_time_str = "--"
        else:
            status = self.status
            delivery_time_str = (
                self._format_time(self.delivery_time) if self.delivery_time else "--"
            )

        return (
            f"{self.package_id:>3} | "
            f"{self.address:<40} | "
            f"{self.deadline:<10} | "
            f"{status.value:<10} | "
            f"{delivery_time_str:<10} | "
            f"Truck {self.truck_id if self.truck_id else '-'}"
        )
