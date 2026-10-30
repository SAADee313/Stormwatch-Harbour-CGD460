"""Deterministic, tick-based Stormwatch Harbour environment.

Student ID: 231713 (last digit 3).
Design assumptions not specified by the assignment are documented in README.md.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
import random
from typing import Optional

WIDTH, HEIGHT = 24, 16
TICKS = 600
N_WORKERS = 16
CARGO_PER_SHIP = 9
ARRIVAL_MIN, ARRIVAL_MAX = 5, 9
STORM_COUNT, STORM_DURATION, WARNING_LEAD = 5, 15, 5
BERTHS = {"B1": (3, 0), "B2": (9, 0), "B3": (15, 0), "B4": (21, 0)}
WAREHOUSE = (0, 15)
UNSAFE = {"B1", "B4"}

@dataclass
class Ship:
    id: int
    arrival: int
    berth: Optional[str] = None
    cargo: int = CARGO_PER_SHIP
    dock_tick: Optional[int] = None

@dataclass
class Worker:
    id: int
    pos: tuple[int, int]
    cargo: bool = False
    target: Optional[str] = None
    knockout_until: int = 0
    known_storm_until: int = -1


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

class Harbour:
    def __init__(self, policy: str, seed: int):
        if policy not in {"baseline", "reflex", "model", "utility", "llm"}:
            raise ValueError(f"Unsupported agent: {policy}")
        self.policy = policy
        self.llm_assignments = {}
        self.harbour_closed = False
        self.held_ships = set()
        self.release_authorizations = set()
        self.seed = seed
        self.rng = random.Random(seed)
        self.tick = 0
        self.workers = [Worker(i, (i % 4, 15 - i // 4)) for i in range(N_WORKERS)]
        self.berths: dict[str, Optional[Ship]] = {name: None for name in BERTHS}
        self.queue: deque[Ship] = deque()
        self.all_ships: list[Ship] = []
        self.next_ship_id = 1
        self.next_arrival = self.rng.randint(ARRIVAL_MIN, ARRIVAL_MAX)
        # Nonoverlapping storms, generated once by the single seeded RNG.
        candidates = list(range(25, TICKS - STORM_DURATION, 20))
        self.storm_starts = sorted(self.rng.sample(candidates, STORM_COUNT))
        self.cargo_delivered = 0
        self.crowding_violations = 0
        self.storm_knockouts = 0
        self.waits: list[int] = []
        self.heatmap = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.deliveries_by_tick: list[int] = []
        self.berth_loads = {b: 0 for b in BERTHS}

    def storm_active(self):
        return any(s <= self.tick < s + STORM_DURATION for s in self.storm_starts)

    def storm_soon(self):
        return any(s - WARNING_LEAD <= self.tick < s for s in self.storm_starts)

    def _arrival(self):
        if self.tick == self.next_arrival:
            ship = Ship(self.next_ship_id, self.tick)
            self.next_ship_id += 1
            self.all_ships.append(ship)
            self.queue.append(ship)
            self.next_arrival += self.rng.randint(ARRIVAL_MIN, ARRIVAL_MAX)

    def _dock_waiting(self):
        for name in BERTHS:
            if not self.queue:
                break
            if self.berths[name] is None and not self.harbour_closed and (not self.queue or self.queue[0].id not in self.held_ships):
                ship = self.queue.popleft()
                ship.berth = name
                ship.dock_tick = self.tick
                self.waits.append(self.tick - ship.arrival)
                self.berths[name] = ship

    def _storm_events(self):
        if self.storm_soon():
            # Lookout broadcasts a warning; model-based workers remember it.
            for w in self.workers:
                if self.policy in {"model", "utility", "llm"}:
                    w.known_storm_until = max(w.known_storm_until, self.tick + WARNING_LEAD + STORM_DURATION)
        if self.tick in self.storm_starts:
            for w in self.workers:
                if w.pos in (BERTHS["B1"], BERTHS["B4"]) and w.knockout_until <= self.tick:
                    w.knockout_until = self.tick + 20
                    w.cargo = False
                    self.storm_knockouts += 1

    def _risk(self, w: Worker, berth: str):
        return berth in UNSAFE and (self.storm_active() or w.known_storm_until > self.tick)

    def _choose_target(self, w: Worker):
        options = [b for b, ship in self.berths.items() if ship is not None and ship.cargo > 0]
        if not options:
            return None
        if self.policy == "reflex":
            # Reflex sees only current cargo and distance; no storm memory.
            return min(options, key=lambda b: (distance(w.pos, BERTHS[b]), b))
        safe = [b for b in options if not self._risk(w, b)]
        if not safe:
            return None
        if self.policy == "model":
            # Remembers berth assignment until emptied or unsafe.
            if w.target in safe:
                return w.target
            return min(safe, key=lambda b: (distance(w.pos, BERTHS[b]), b))
        if self.policy == "llm" and w.id in self.llm_assignments and self.llm_assignments[w.id] in safe:
            return self.llm_assignments[w.id]
        # Utility: cargo, distance, congestion and storm risk (four factors).
        # Normalized factors with fixed, interpretable weights.
        def score(b):
            ship = self.berths[b]
            cargo = ship.cargo / CARGO_PER_SHIP
            proximity = 1 - distance(w.pos, BERTHS[b]) / (WIDTH + HEIGHT - 2)
            crowd = sum(other.target == b for other in self.workers if other.id != w.id)
            crowd_score = 1 - min(crowd, N_WORKERS) / N_WORKERS
            storm_safety = 0 if self._risk(w, b) else 1
            return .35 * cargo + .30 * proximity + .20 * crowd_score + .15 * storm_safety
        return max(safe, key=lambda b: (score(b), b))

    def _step_toward(self, w: Worker, dest: tuple[int, int], occupancy):
        x, y = w.pos
        choices = []
        if dest[0] < x: choices.append((x - 1, y))
        if dest[0] > x: choices.append((x + 1, y))
        if dest[1] < y: choices.append((x, y - 1))
        if dest[1] > y: choices.append((x, y + 1))
        # Try a detour if the preferred next cell is full.
        for p in ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)):
            if p not in choices:
                choices.append(p)
        candidates = [p for p in choices if 0 <= p[0] < WIDTH and 0 <= p[1] < HEIGHT and occupancy.get(p, 0) < 3]
        if not candidates:
            return
        # Prefer progress, then lower occupancy; never leave grid.
        candidates.sort(key=lambda p: (distance(p, dest), occupancy.get(p, 0), p[1], p[0]))
        if distance(candidates[0], dest) > distance(w.pos, dest):
            return
        occupancy[w.pos] -= 1
        w.pos = candidates[0]
        occupancy[w.pos] = occupancy.get(w.pos, 0) + 1

    def _worker_action(self, w, occupancy):
        if self.policy == "baseline" or w.knockout_until > self.tick:
            return
        if w.cargo:
            if w.pos == WAREHOUSE:
                w.cargo = False
                self.cargo_delivered += 1
                return
            self._step_toward(w, WAREHOUSE, occupancy)
            return
        w.target = self._choose_target(w)
        if w.target is None:
            return
        berth_pos = BERTHS[w.target]
        ship = self.berths[w.target]
        if ship is None or ship.cargo <= 0:
            return
        if distance(w.pos, berth_pos) <= 1:
            # One pickup action per tick; no pickup at unsafe berths in a storm.
            if self.storm_active() and w.target in UNSAFE:
                return
            ship.cargo -= 1
            w.cargo = True
            self.berth_loads[w.target] += 1
            if ship.cargo == 0:
                self.berths[w.target] = None
            return
        self._step_toward(w, berth_pos, occupancy)

    def step(self, t):
        self.tick = t
        self._arrival()
        self._dock_waiting()
        self._storm_events()
        occupancy = {}
        for w in self.workers:
            occupancy[w.pos] = occupancy.get(w.pos, 0) + 1
        for w in self.workers:
            self._worker_action(w, occupancy)
        self.crowding_violations += sum(n > 3 for n in occupancy.values())
        for w in self.workers:
            self.heatmap[w.pos[1]][w.pos[0]] += 1
        self.deliveries_by_tick.append(self.cargo_delivered)

    def metrics(self):
        waits = self.waits + [TICKS - s.arrival for s in self.queue]
        return {
            "cargo_delivered": self.cargo_delivered,
            "avg_ship_wait": round(sum(waits) / len(waits), 3) if waits else 0.0,
            "crowding_violations": self.crowding_violations,
            "storm_knockouts": self.storm_knockouts,
        }

    def run(self):
        for t in range(TICKS):
            self.step(t)
        return self.metrics()
