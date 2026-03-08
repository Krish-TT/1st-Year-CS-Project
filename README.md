# 1st-Year-CS-Project
# Orb Collector: CS 1201 Project

Orb Collector is a dual-game Python project combining snake-like mechanics with algorithmic pathfinding.

## Game 1: Postfix Snake
* **Core Mechanic**: A snake-like game where a train collects "modifier spheres" ($+/-$).
* **Scoring**: Points are banked in train coaches.Eating a modifier sphere causes the last coach to detach.
* **Logic**: If the detached coach hits the water, the sphere value is added or subtracted from the main score.

## Game 2: Dijkstra’s Navigation
* **Algorithm**: Implements Dijkstra’s algorithm using a Python min-priority heap to calculate the shortest path to target stations.
* **Map Dynamics**: The map layout, connections, and orb placements are automatically regenerated once all orbs are collected.
* **Constraints**: A strict 2-minute time limit dictates the game session length.

## Technical Implementation
This project utilizes several core data structures:
* **Min-Heap (Priority Queue)**: Implements the priority queue for Dijkstra's algorithm.
* **GraphMap (Custom Class)**: Manages stations, connections, and pathfinding logic
* **Sets**: Tracks processed stations during search to prevent cycles and redundant computations.
* **Lists & Tuples**: Stores station connections, sphere sequences, falling coaches, coordinates, and screen dimensions.

# The project utilizes core Python libraries for logic:

* Built-in Logic & heapq, math, random
* Visualization pygame

## Team
* Krish Seksaria (2401MC30)
* Aditya Tanwar (2401ME50) 
* Parth Kataria (2401ME03) 
