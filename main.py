# Student ID: 012370590
# WGUPS Package Routing Program
# This program uses a nearest neighbor algorithm to efficiently deliver packages
# for the Western Governors University Parcel Service (WGUPS).

"""
WGUPS Package Routing Program
=============================

This program implements a delivery routing solution for WGUPS that:
1. Loads package data into a custom hash table
2. Assigns packages to trucks based on constraints
3. Uses a nearest neighbor algorithm to optimize delivery routes
4. Provides an interface to view package status at any time

Algorithm: Nearest Neighbor
- Time Complexity: O(n^2) where n is the number of packages per truck
- Space Complexity: O(n) for storing package data

The program ensures:
- All packages delivered by their deadlines
- Total mileage under 140 miles
- All package constraints are satisfied
"""

import csv
import os
from datetime import datetime
from typing import Optional

from hash_table import HashTable
from package import Package
from truck import Truck


# Global constants
# Get the directory where this script is located
SCRIPT_DIR = (
    os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
)
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
PACKAGES_FILE = os.path.join(DATA_DIR, "packages.csv")

# Delivery time constraints
START_OF_DAY = datetime(2024, 1, 1, 8, 0, 0)  # 8:00 AM
DELAYED_ARRIVAL = datetime(2024, 1, 1, 9, 5, 0)  # 9:05 AM - delayed packages arrive
ADDRESS_CORRECTION_TIME = datetime(
    2024, 1, 1, 10, 20, 0
)  # 10:20 AM - Package 9 address fixed


def load_packages(hash_table: HashTable) -> bool:
    """
    Load all packages from the CSV file into the hash table.

    This function reads the package data file and creates Package objects
    for each entry, then inserts them into the hash table using their
    package ID as the key.
    """
    try:
        with open(PACKAGES_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                package = Package(
                    package_id=row["package_id"],
                    address=row["address"],
                    city=row["city"],
                    state=row["state"],
                    zip_code=row["zip"],
                    deadline=row["deadline"],
                    weight=row["weight"],
                    notes=row["notes"],
                )

                hash_table.insert(int(row["package_id"]), package)

        return True
    except FileNotFoundError:
        print(f"Error: Package file not found at {PACKAGES_FILE}")
        return False
    except Exception as e:
        print(f"Error loading packages: {e}")
        return False


def get_all_linked_packages(setA: set[int], hash_table: HashTable) -> set[int]:
    linked_packages: set[int] = set()
    for pkg_id in list(setA):
        pkg = hash_table.lookup(pkg_id)
        if not pkg:
            continue
        for linked_id in pkg.get_linked_packages():
            if linked_id not in linked_packages:
                linked_packages.add(linked_id)

    return linked_packages


def load_all_packages(
    package_ids: set[int], hash_table: HashTable, truck: Truck
) -> bool:
    at_capacity = False
    for pkg_id in package_ids:
        package = hash_table.lookup(pkg_id)
        if package:
            at_capacity = not truck.load_package(pkg_id)

    return at_capacity


def assign_packages_to_trucks(hash_table: HashTable) -> tuple[Truck, Truck, Truck]:
    """
    Assign packages to trucks based on constraints and deadlines.

    Truck Loading Strategy:
    -----------------------
    Truck 1 (departs 8:00 AM):
        - Early deadline packages (9:00 AM, 10:30 AM deadlines)
        - Linked packages that must be delivered together

    Truck 2 (departs 9:05 AM):
        - Packages that can only be on truck 2
        - Delayed packages
        - Fill with other EOD packages

    Truck 3 (departs when first truck returns):
        - Remaining packages
        - Package 9 (needs address correction at 10:20 AM)
    """
    # Create trucks with their departure times
    truck1 = Truck(1, START_OF_DAY)
    truck2 = Truck(2, DELAYED_ARRIVAL)
    truck3 = Truck(3, None)

    # ==========================================
    # TRUCK 1: Early deadlines and linked packages
    # ==========================================
    # Packages with 9:00 AM or 10:30 AM deadlines that aren't delayed
    remaining_packages = set([p.package_id for p in hash_table.get_all()])

    truck1_packages = set(
        [
            p.package_id
            for p in hash_table.get_all()
            if p.has_deadline() and not p.is_delayed() and not p.requires_truck_2()
        ]
    )
    truck1_linked_packages = get_all_linked_packages(truck1_packages, hash_table)
    truck1_packages = truck1_packages.union(truck1_linked_packages)

    load_all_packages(truck1_packages, hash_table, truck1)

    # ==========================================
    # TRUCK 2: Truck 2 only + Delayed packages
    # ==========================================
    remaining_packages = remaining_packages.difference(truck1_packages)

    truck2_packages = [3, 5, 6, 7, 8, 10, 11, 12, 17, 18, 23, 25, 28, 32, 36, 38]
    truck2_packages.sort()
    truck2_packages = set(
        [
            p.package_id
            for p in hash_table.get_all()
            if (p.package_id in remaining_packages)
            and p.is_delayed()
            and p.requires_truck_2()
            and not p.has_wrong_address()
        ]
    )
    truck2_linked_packages = get_all_linked_packages(truck2_packages, hash_table)
    truck2_packages = truck2_packages.union(truck2_linked_packages)

    # fill truck 2 with EOD packages from remaining till at capacity
    remaining_packages = remaining_packages.difference(truck2_packages)
    for pkg_id in remaining_packages:
        if len(truck2_packages) >= truck2.capacity:
            break
        truck2_packages.add(pkg_id)

    load_all_packages(truck2_packages, hash_table, truck2)

    # ==========================================
    # TRUCK 3: Remaining packages
    # ==========================================
    # All packages not assigned to truck 1 or 2
    truck3_packages = remaining_packages.difference(truck2_packages)

    load_all_packages(truck3_packages, hash_table, truck3)

    return truck1, truck2, truck3


def correct_package_address(
    hash_table: HashTable,
    package_id: int,
    address: str,
    city: str,
    state: str,
    zip_code: str,
):
    """
    Correct the address for a package.
    """
    package = hash_table.lookup(package_id)
    if package:
        # Update to correct address
        package.address = address
        package.city = city
        package.state = state
        package.zip_code = zip_code
        # Clear the wrong address note
        package.notes = "Address corrected at 10:20 AM"


def run_deliveries(
    hash_table: HashTable, truck1: Truck, truck2: Truck, truck3: Truck
) -> float:
    """
    Execute the delivery routes for all trucks.

    Delivery Sequence:
    1. Truck 1 departs at 8:00 AM with early deadline packages
    2. Truck 2 departs at 9:05 AM after delayed packages arrive
    3. When Truck 1 returns, the driver takes Truck 3
    4. Package 9 address is corrected at 10:20 AM
    """
    # ==========================================
    # Execute Truck 1 deliveries (8:00 AM start)
    # ==========================================
    print("\nStarting Truck 1 deliveries...")
    truck1_miles = truck1.deliver_packages(hash_table)
    truck1_return = truck1.get_return_time()
    print(f"  Truck 1 returned at {truck1_return.strftime('%-I:%M %p')}")
    print(f"  Truck 1 mileage: {truck1_miles:.1f} miles")

    # ==========================================
    # Execute Truck 2 deliveries (9:05 AM start)
    # ==========================================
    print("\nStarting Truck 2 deliveries...")
    truck2_miles = truck2.deliver_packages(hash_table)
    truck2_return = truck2.get_return_time()
    print(f"  Truck 2 returned at {truck2_return.strftime('%-I:%M %p')}")
    print(f"  Truck 2 mileage: {truck2_miles:.1f} miles")

    # ==========================================
    # Truck 3: Departs when driver returns
    # ==========================================
    # The driver from Truck 1 takes Truck 3
    # Truck 3 cannot leave until:
    # 1. Truck 1 returns (driver available)
    # 2. 10:20 AM (package 9 address corrected)

    # Determine when Truck 3 can depart
    truck3_earliest = max(truck1_return, ADDRESS_CORRECTION_TIME)
    truck3.departure_time = truck3_earliest
    truck3.current_time = truck3_earliest

    # Correct package 9 address before Truck 3 departs
    correct_package_address(
        hash_table, 9, "410 S State St", "Salt Lake City", "UT", "84111"
    )

    print(
        f"\nStarting Truck 3 deliveries at {truck3_earliest.strftime('%-I:%M %p')}..."
    )
    truck3_miles = truck3.deliver_packages(hash_table)
    truck3_return = truck3.get_return_time()
    print(f"  Truck 3 returned at {truck3_return.strftime('%-I:%M %p')}")
    print(f"  Truck 3 mileage: {truck3_miles:.1f} miles")

    # Calculate total mileage
    total_mileage = truck1_miles + truck2_miles + truck3_miles

    return total_mileage


def main():
    """
    Main entry point for the WGUPS Package Routing Program.

    This function orchestrates the entire delivery process:
    1. Creates the hash table and loads package data
    2. Assigns packages to trucks based on constraints
    3. Executes delivery routes
    4. Launches the user interface
    """
    print("=" * 60)
    print("WGUPS PACKAGE ROUTING PROGRAM")
    print("=" * 60)

    # Step 1: Create hash table and load packages
    print("\nLoading package data...")
    hash_table = HashTable(40)

    if not load_packages(hash_table):
        print("Failed to load packages. Exiting.")
        return

    print(f"  Loaded {len(hash_table)} packages into hash table.")

    # Step 2: Assign packages to trucks
    print("\nAssigning packages to trucks...")
    truck1, truck2, truck3 = assign_packages_to_trucks(hash_table)

    print(f"  Truck 1: {truck1.get_package_count()} packages (departs 8:00 AM)")
    print(f"  Truck 2: {truck2.get_package_count()} packages (departs 9:05 AM)")
    print(
        f"  Truck 3: {truck3.get_package_count()} packages (departs after Truck 1 returns)"
    )

    # Step 3: Execute deliveries
    print("\n" + "-" * 60)
    print("EXECUTING DELIVERIES")
    print("-" * 60)

    total_mileage = run_deliveries(hash_table, truck1, truck2, truck3)

    print("\n" + "=" * 60)
    print("DELIVERY COMPLETE")
    print("=" * 60)
    print(f"Total mileage: {total_mileage:.1f} miles")

    if total_mileage < 140:
        print("SUCCESS: All packages delivered under 140 miles!")
    else:
        print("WARNING: Total mileage exceeds 140 mile limit.")


if __name__ == "__main__":
    main()
