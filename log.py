# log.py
# Log class for WGUPS Package Routing Program
# Logs historical data for all packages
from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from package import Package, PackageStatus


@dataclass(frozen=True)
class LogEntry:
    package_id: int
    event_time: Optional[datetime]
    address: tuple[str, str, str, str]
    notes: str
    status: PackageStatus
    departure_time: Optional[datetime]
    truck_id: Optional[int]
    delivery_time: Optional[datetime]
    metadata: str


class Log:
    """
    Log maintains a historical record of package events and persists to CSV.
    """

    def __init__(self, file_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        self.file_path = file_path or os.path.join(data_dir, "package_log.csv")
        self.entries: list[LogEntry] = []

        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self._initialize_csv()

    def _initialize_csv(self) -> None:
        """
        Initialize a csv file with the appropriate headers.
        """
        with open(self.file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "package_id",
                    "event_time",
                    "address",
                    "city",
                    "state",
                    "zip",
                    "notes",
                    "status",
                    "departure_time",
                    "truck_id",
                    "delivery_time",
                    "metadata",
                ]
            )

    def _format_time(self, time_obj: Optional[datetime]) -> str:
        """
        Format a datetime object to a readable time string.
        """
        if time_obj is None:
            return ""
        return time_obj.strftime("%Y-%m-%d %H:%M:%S")

    def record_event(
        self,
        package: Package,
        event_time: datetime,
        metadata: str,
        truck_id: Optional[int] = None,
        departure_time: Optional[datetime] = None,
        delivery_time: Optional[datetime] = None,
    ) -> None:
        """
        Compose and append event for a single package.
        """
        entry = LogEntry(
            package_id=package.package_id,
            event_time=event_time,
            address=(package.address, package.city, package.state, package.zip_code),
            notes=package.notes,
            status=package.status,
            departure_time=departure_time,
            truck_id=truck_id,
            delivery_time=delivery_time,
            metadata=metadata,
        )

        self.entries.append(entry)

        with open(self.file_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    entry.package_id,
                    self._format_time(entry.event_time),
                    entry.address[0],
                    entry.address[1],
                    entry.address[2],
                    entry.address[3],
                    entry.notes,
                    entry.status.value,
                    self._format_time(entry.departure_time),
                    entry.truck_id if entry.truck_id is not None else "",
                    self._format_time(entry.delivery_time),
                    entry.metadata,
                ]
            )

    def get_history(self, package_id: int) -> list[LogEntry]:
        """
        Get entire history from log for a single package.
        """
        return [entry for entry in self.entries if entry.package_id == package_id]

    def get_entry_at_time(
        self, package_id: int, query_time: datetime
    ) -> Optional[LogEntry]:
        """
        Get log entry for a single package at a given time.
        """
        last_entry = None
        for entry in self.get_history(package_id):
            if entry.event_time and entry.event_time <= query_time:
                last_entry = entry
        return last_entry

    def format_status_line(self, package: Package, query_time: datetime) -> str:
        """
        Format log entry into console friendly format.
        """
        entry = self.get_entry_at_time(package.package_id, query_time)
        if entry is None:
            status = package.status
            updated = "--"
            address = package.address
            truck_display = "-"
            delivery_time = "-"
        else:
            status = entry.status
            address = entry.address[0]
            if (
                entry.status == PackageStatus.DELIVERED
                and entry.delivery_time
                and entry.delivery_time <= query_time
            ):
                delivery_time = entry.delivery_time.strftime("%-I:%M %p")
            else:
                delivery_time = "-"
            if (
                entry.status == PackageStatus.ENROUTE
                and entry.departure_time
                and entry.departure_time <= query_time
            ):
                updated = entry.departure_time.strftime("%-I:%M %p")
            elif entry.event_time and entry.event_time <= query_time:
                updated = entry.event_time.strftime("%-I:%M %p")
            else:
                updated = "--"
            truck_display = str(entry.truck_id) if entry.truck_id else "-"

        return (
            f"{package.package_id:>3} | "
            f"{address:<40} | "
            f"{package.deadline:<10} | "
            f"{delivery_time:<10} | "
            f"{status.value:<10} | "
            f"{updated:<10} | "
            f"Truck {truck_display}"
        )
