"""Optional visualization. Requires matplotlib."""
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from src.simulation import Harbour, BERTHS, WAREHOUSE

parser = argparse.ArgumentParser()
parser.add_argument("--agent", choices=["baseline", "reflex", "model", "utility"], default="utility")
parser.add_argument("--seed", type=int, default=1)
args = parser.parse_args()
h = Harbour(args.agent, args.seed)
result = h.run()
Path("results").mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(11, 6))
im = ax.imshow(h.heatmap, origin="upper", cmap="YlOrRd")
for name, (x, y) in BERTHS.items():
    ax.text(x, y, name, ha="center", va="center", color="blue", fontweight="bold")
ax.text(*WAREHOUSE, "W", ha="center", va="center", color="blue", fontweight="bold")
ax.set_title(f"Worker position heatmap | {args.agent} | seed {args.seed}")
ax.set_xticks(range(24)); ax.set_yticks(range(16)); ax.grid(alpha=.15)
fig.colorbar(im, ax=ax, label="Worker-ticks")
fig.tight_layout()
path = f"results/heatmap_{args.agent}_seed{args.seed}.png"
fig.savefig(path, dpi=150)
print(f"Saved {path} | {result}")
