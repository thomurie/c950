# WGUPS Package Routing Program

This project simulates the Western Governors University Parcel Service (WGUPS) delivery day using a nearest-neighbor routing approach. It loads package data from `data/packages.csv`, assigns packages to three trucks based on constraints (deadlines, delays, truck requirements, linked packages), and then delivers them while tracking mileage and delivery status over time.

## How it works

- Loads 40 packages into a custom hash table (`HashTable`).
- Builds three trucks with different departure constraints:
  - Truck 1: early deadlines + linked packages.
  - Truck 2: delayed and truck-2-only packages, then filled to capacity.
  - Truck 3: remaining packages, leaving after Truck 1 returns and the address correction time.
- Runs deliveries using a nearest-neighbor distance lookup from `data/distances.csv`.
- Provides a console menu to view package status at a specific time and the total mileage.

## Run

```bash
python main.py
```

## Data

- `data/packages.csv`: package list with deadlines, notes, and constraints.
- `data/distances.csv`: addresses and the distance matrix used by the routing algorithm.
