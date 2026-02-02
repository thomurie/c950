# truck.py
# Truck class for WGUPS Package Routing Program
# Handles package loading, delivery routing, and mileage tracking

from datetime import datetime, timedelta
from distance import get_distance, get_address_index, find_nearest, HUB_INDEX
from hash_table import HashTable

from package import PackageStatus


class Truck:
    """
    Represents a delivery truck in the WGUPS system.

    Each truck can carry up to 16 packages and travels at 18 mph.
    The truck uses a nearest neighbor algorithm to determine delivery order.
    """

    def __init__(self, truck_id: int, departure_time: datetime):
        """
        Initialize a new truck.
        """
        self.truck_id: int = truck_id
        self.departure_time: datetime = departure_time
        self.current_time: datetime = departure_time
        self.current_location = HUB_INDEX

        self.packages: list[int] = []  # List of package IDs loaded on the truck
        self.delivered_packages: list[int] = []  # List of delivered package IDs
        self.mileage: float = 0.0
        self.speed_mph = 18
        self.capacity = 16

        self.route_history: list[tuple[int, datetime, float]] = [
            (HUB_INDEX, departure_time, 0.0)
        ]  # (location, time, cumulative_miles)

    def load_package(self, package_id: int) -> bool:
        """
        Load a package onto the truck.
        """
        if len(self.packages) >= self.capacity:
            return False

        self.packages.append(package_id)
        return True

    def get_package_count(self) -> int:
        """
        Get the number of packages currently loaded.
        """
        return len(self.packages)

    def _calculate_travel_time(self, distance: float) -> timedelta:
        """
        Calculate the time to travel a given distance.
        """
        hours = distance / self.speed_mph
        minutes = hours * 60
        return timedelta(minutes=minutes)

    def deliver_packages(self, hash_table: HashTable) -> float:
        """
        Deliver all packages using the nearest neighbor algorithm.

        This method implements the core delivery algorithm:
        1. Find the nearest undelivered package
        2. Travel to that location
        3. Deliver all packages at that location
        4. Repeat until all packages are delivered
        5. Return to the hub
        """
        # Build list of packages with their address indices
        remaining_packages = []
        for package_id in self.packages:
            package = hash_table.lookup(package_id)
            if package:
                # Mark package as en route
                package.update_status(PackageStatus.ENROUTE, self.departure_time)
                package.truck_id = self.truck_id

                # Get address index
                address_index = get_address_index(package.address)
                remaining_packages.append((package_id, address_index))

        # Deliver packages using nearest neighbor algorithm
        while remaining_packages:
            # Find the nearest package
            nearest_id, nearest_index, distance = find_nearest(
                self.current_location, remaining_packages
            )

            if nearest_id is None:
                break

            # Travel to the delivery location
            travel_time = self._calculate_travel_time(distance)
            self.current_time += travel_time
            self.mileage += distance
            self.current_location = nearest_index

            # Deliver all packages at this location
            # (Multiple packages might share the same address)
            packages_at_location = [
                (pid, idx) for pid, idx in remaining_packages if idx == nearest_index
            ]

            for package_id, _ in packages_at_location:
                package = hash_table.lookup(package_id)
                if package:
                    package.update_status(PackageStatus.DELIVERED, self.current_time)
                    self.delivered_packages.append(package_id)

                # Remove from remaining list
                remaining_packages = [
                    (pid, idx) for pid, idx in remaining_packages if pid != package_id
                ]

            # Record route history
            self.route_history.append((nearest_index, self.current_time, self.mileage))

        # Return to hub
        return_distance = get_distance(self.current_location, HUB_INDEX)
        return_time = self._calculate_travel_time(return_distance)
        self.current_time += return_time
        self.mileage += return_distance
        self.current_location = HUB_INDEX

        # Record return to hub
        self.route_history.append((HUB_INDEX, self.current_time, self.mileage))

        return self.mileage

    def get_return_time(self) -> datetime:
        """
        Get the time when the truck returns to the hub.
        """
        return self.current_time
