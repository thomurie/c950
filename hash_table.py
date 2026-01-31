# hash_table.py
# Custom hash table implementation for WGUPS Package Routing Program

from package import Package


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

    def __len__(self) -> int:
        """
        Return the number of packages in the hash table.
        """
        return self.size
