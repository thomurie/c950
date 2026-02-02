# hash_table.py
# Custom hash table implementation for WGUPS Package Routing Program

from package import Package
from typing import Optional


class HashTable:
    """
    A custom hash table implementation that stores packages using their ID as the key.
    Uses chaining with linked lists to handle hash collisions.
    """

    def __init__(self, capacity: int = 40):
        self.capacity = capacity
        self.table = [[] for _ in range(capacity)]
        self.size = 0

    def _hash(self, key: int):
        return int(key) % self.capacity

    def insert(self, package_id: int, package: Package) -> bool:
        """
        Insert packages into the hash table.
        """
        # Calculate the bucket index
        bucket_index = self._hash(package_id)
        bucket = self.table[bucket_index]

        # Check if package already exists in bucket (update case)
        for i, (key) in enumerate(bucket):
            if key == package_id:
                # Update existing package
                bucket[i] = (package_id, package)
                return True

        # Package doesn't exist, add new entry
        bucket.append((package_id, package))
        self.size += 1
        return True

    def lookup(self, package_id: int) -> Optional[Package]:
        """
        Look up a package by its ID and return the package data.
        """
        # Calculate the bucket index
        bucket_index = self._hash(package_id)
        bucket = self.table[bucket_index]

        # Search for the package in the bucket
        for key, value in bucket:
            if key == package_id:
                return value

        # Package not found
        return None

    def remove(self, package_id: int) -> bool:
        """
        Remove a package from the hash table.
        """
        bucket_index = self._hash(package_id)
        bucket = self.table[bucket_index]

        for i, (key) in enumerate(bucket):
            if key == package_id:
                bucket.pop(i)
                self.size -= 1
                return True

        return False

    def get_all(self) -> list[Package]:
        """
        Retrieve all packages from the hash table.
        """
        packages = []
        for bucket in self.table:
            for _, value in bucket:
                packages.append(value)
        return packages

    def __len__(self) -> int:
        """
        Return the number of packages in the hash table.
        """
        return self.size

    def __contains__(self, package_id: int) -> bool:
        """
        Check if a package ID exists in the hash table.
        """
        return self.lookup(package_id) is not None
