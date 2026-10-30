# Stormwatch Harbour — CGD-460 Assignment 2

Student ID: **231713**, last digit **3**. Individual project starter for learning and extension.

## Run

Python 3.9+ recommended. From this folder:

```bash
python run.py --agent baseline --seed 1
python run.py --agent reflex --seed 1
python run.py --agent model --seed 1
python run.py --agent utility --seed 1
```

Each run prints exactly one JSON line. No dependencies needed for these commands.

Optional heatmap:

```bash
python -m pip install -r requirements.txt
python visualize.py --agent utility --seed 1
```

## Required parameters

- Grid 24 columns × 16 rows, coordinates x=0..23, y=0..15.
- Berths B1=(3,0), B2=(9,0), B3=(15,0), B4=(21,0).
- Warehouse=(0,15).
- 16 dockworkers; arrivals 5–9 ticks; 5 storms/run; 9 cargo/ship.
- 600 ticks/run; 15-tick storms; lookout warning 5 ticks early; knockout 20 ticks.
- One `random.Random(seed)` instance supplies all randomness.

## Implementation assumptions to disclose in the report

The brief leaves some mechanics unspecified. This prototype assumes:

1. Workers begin in a 4×4 block near the warehouse, with one worker per cell.
2. A ship docks at the first available berth (B1 to B4). A ship is considered to have finished waiting once it docks. Undocked ships at tick 600 contribute elapsed waiting time to the mean (censored waiting); report this definition explicitly.
3. The Lookout broadcasts warnings immediately to model/utility workers. Reflex workers do not retain them.
4. Berth cells can be traversed; workers pick up from a berth or an adjacent orthogonal cell. Storm knockout happens only if standing on B1/B4 berth cells at storm onset.
5. Storm start times are sampled from fixed spaced candidate ticks, so storms do not overlap.
6. Each worker can carry one cargo unit. Ship cargo is removed on pickup, so the ship can leave before cargo reaches the warehouse.
7. Collision handling uses sequential movement, checking destination occupancy against a maximum of three. A blocked worker waits.
8. Ship arrivals and storm timings are generated even for baseline, ensuring a comparable environment per seed.
9. No pathfinding through obstacles is required because the map has no blocked terrain.

## Worker policies

- `baseline`: do nothing.
- `reflex`: go to the nearest berth with cargo, without warning memory.
- `model`: remembers storm warnings and current target berth.
- `utility`: scores eligible berths using cargo (0.35), proximity (0.30), congestion (0.20), and storm safety (0.15); unsafe berths are also filtered out when storm warning is known.

These are initial, explainable weights, not yet tuned. Task B requires you to evaluate and justify them using experiments.

## Current phase / remaining work

This is a **Phase 1 prototype**, not a finished assignment. Phase 2 will add the 30-seed paired evaluation, statistical tables, emergent-behaviour tests and figures. Phase 3 will add the actual LLM closed loop, replay and prompt logs. Phase 4 will add injection and human-approval tests. The `llm` command is intentionally not implemented yet.
