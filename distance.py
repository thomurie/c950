# distance.py
# Distance data and utility functions for WGUPS Package Routing Program
from __future__ import annotations

import csv
import os
from typing import Optional

# Index of the hub location in the distance matrix
HUB_INDEX = 0

# Get the directory where this script is located
SCRIPT_DIR = (
    os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
)
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
DISTANCES_FILE = os.path.join(DATA_DIR, "distances.csv")


def load_distance_data(
    path: str,
) -> tuple[list[str], list[str], list[list[float]]]:
    """
    Load location names, addresses, and distance matrix from CSV.
    """
    location_names: list[str] = []
    addresses: list[str] = []
    distance_matrix: list[list[float]] = []

    with open(path, "r", newline="") as file:
        reader = csv.reader(file)
        header = next(reader, None)
        if not header or len(header) < 3:
            raise ValueError("header is missing")

        for row in reader:
            if not row or len(row) < 3:
                continue
            location_names.append(row[0].strip())
            addresses.append(row[1].strip())

            distances: list[float] = []
            for value in row[2:]:
                value = value.strip()
                distances.append(float(value) if value else 0.0)
            distance_matrix.append(distances)

    expected = len(addresses)
    for i, row in enumerate(distance_matrix):
        if len(row) != expected:
            raise ValueError(
                f"file row {i} has {len(row)} distances, expected {expected}"
            )

    return location_names, addresses, distance_matrix


# Load distance data at import
LOCATION_NAMES, ADDRESSES, DISTANCE_MATRIX = load_distance_data(DISTANCES_FILE)


def get_address_index(address: str) -> int:
    """
    Get the index of an address in the ADDRESSES list.
    """
    # Normalize the address for comparison
    normalized = address.lower().strip()

    for i, addr in enumerate(ADDRESSES):
        if addr.lower() == normalized:
            return i

        # Check if the normalized address contains the key parts of the stored address
        addr_lower = addr.lower()

        # Check for partial match - extract the main address components
        if normalized in addr_lower or addr_lower in normalized:
            return i

        # Additional data cleaning
        norm_clean = normalized.replace(",", "").replace(".", "").replace("  ", " ")
        addr_clean = addr_lower.replace(",", "").replace(".", "").replace("  ", " ")

        if norm_clean == addr_clean:
            return i

        # Check if the street number and name match
        norm_parts = norm_clean.split()
        addr_parts = addr_clean.split()

        if len(norm_parts) >= 2 and len(addr_parts) >= 2:
            # Compare first few parts (number and street name)
            if norm_parts[0] == addr_parts[0] and norm_parts[1] == addr_parts[1]:
                return i

    # If no match found, return -1
    return -1


def get_distance(from_index: int, to_index: int) -> float:
    """
    Get the distance between two locations using their indices.
    """
    if from_index < 0 or from_index >= len(DISTANCE_MATRIX):
        return float("inf")
    if to_index < 0 or to_index >= len(DISTANCE_MATRIX):
        return float("inf")

    return DISTANCE_MATRIX[from_index][to_index]


def find_nearest(current_index: int, package_indices: list[int]) -> tuple[
    Optional[int],
    Optional[int],
    float,
]:
    """
    Find the nearest undelivered package from the current location.

    This implements the core of the nearest neighbor algorithm.
    """
    if not package_indices:
        return None, None, float("inf")

    min_distance = float("inf")
    nearest_package_id = None
    nearest_index = None

    for package_id, address_index in package_indices:
        distance = get_distance(current_index, address_index)

        if distance < min_distance:
            min_distance = distance
            nearest_package_id = package_id
            nearest_index = address_index

    return nearest_package_id, nearest_index, min_distance
