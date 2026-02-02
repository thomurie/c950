# package.py
# Package class for WGUPS Package Routing Program
# Stores all package data and tracks delivery status
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

        Args:
            package_id (int): Unique package ID number
            address (str): Delivery address
            city (str): Delivery city
            state (str): Delivery state
            zip_code (str): Delivery ZIP code
            deadline (str): Delivery deadline (e.g., "10:30 AM", "EOD")
            weight (int): Package weight in kilogramss
            notes (str): Special note
            status (PackageStatus): Delivery status
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
        if status == "Delivered" and time:
            self.delivery_time = time
        elif status == "En Route" and time:
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
        """
        if "Must be delivered with" not in self.notes:
            return []

        # Parse the package IDs from the notes
        # Format: "Must be delivered with 13 15" or "Must be delivered with 15 19"
        try:
            parts = self.notes.split("Must be delivered with")[1].strip()
            # Split by space and convert to integers
            linked_ids = [int(x) for x in parts.split(",")]

            return linked_ids
        except (ValueError, IndexError):
            return []
