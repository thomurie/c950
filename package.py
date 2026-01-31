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
