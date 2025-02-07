import os
import json
import random
from matplotlib import patches, pyplot as plt
import matplotlib.cm as cm

# --- Configuration ---
EXPECTED_KEYS = ["Tag", "Permissions", "Executive", "Global", "Object Type", "Bounds", "Address", "Reference"]
FIXED_WIDTHS = [1, 16, 1, 1, 15, 31]  # widths for colored (top) row
MAX_SUBPLOT_HEIGHT = 10

# --- Capability Class ---
class Capability:
    def __init__(self, data):
        self.tag = data.get("Tag", "")
        self.permissions = data.get("Permissions", "")
        self.executive = data.get("Executive", "")
        self.global_flag = data.get("Global", "")  # avoid conflict with keyword
        self.object_type = data.get("Object Type", "")
        self.bounds = data.get("Bounds", "")
        self.address = data.get("Address", "")
        self.reference = self._to_int(data.get("Reference"))
        self.type = data.get("Type", "")

    def _to_int(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def getAddress(self):
        return self._to_int(self.address)

    def draw_sections(self):
        # Returns labels for the top row and the address label
        return [self.tag, self.permissions, self.executive, self.global_flag, self.object_type, self.bounds], str(self.address), self.reference

# --- Load and Parse JSON Data ---
file_path = "input.json"
if not os.path.exists(file_path):
    print(f"Error: File '{file_path}' not found.")
    exit()
with open(file_path, "r") as f:
    data = json.load(f)
capabilities = [Capability(item) for item in data]

# --- Group Capabilities by Type and Sort by Reference ---
type_caps = {}
for cap in capabilities:
    type_caps.setdefault(cap.type, []).append(cap)
for typ in type_caps:
    type_caps[typ] = sorted(type_caps[typ], key=lambda c: c.reference if c.reference is not None else -1, reverse=True)
types = sorted(type_caps.keys())

# --- Helpers ---
def get_ref_range(caps):
    refs = [cap.reference for cap in caps if cap.reference is not None]
    return (min(refs) if refs else 0, max(refs) if refs else 1)

def calc_height(min_ref, max_ref, count, base=6, per_cap=0.6, factor=1.5):
    return max(base, (max_ref - min_ref) * factor, count * per_cap)

def draw_capability(ax, cap, y):
    sections, addr_label, ref = cap.draw_sections()
    start = -1
    colors = cm.tab20.colors
    # Draw colored boxes for each section.
    for label, width, color in zip(sections, FIXED_WIDTHS, colors):
        ax.broken_barh([(start, width)], (y + 0.44, 0.4), color=color, edgecolor="black")
        ax.text(start + width/2, y + 0.6, label, ha='center', va='center', fontsize=10)
        start += width
    # Draw gray box for address.
    ax.broken_barh([(0, start)], (y, 0.4), color='lightgrey', edgecolor="black")
    ax.text(start/2, y + 0.18, addr_label, ha='center', va='center', fontsize=10)
    if ref is not None:
        ax.text(start + 1, y + 0.05, f"Ref: {ref}", fontsize=10, fontweight='bold', color='black')
    ax.set_xlim(-1, start + 1)

# --- Pre-calculate Type Info (height and y-positions) ---
type_info = {}
max_height = 0
for typ in types:
    caps = type_caps[typ]
    min_ref, max_ref = get_ref_range(caps)
    height = min(calc_height(min_ref, max_ref, len(caps)), MAX_SUBPLOT_HEIGHT)
    max_height = max(max_height, height)
    # Use each capability’s reference value as its y-coordinate.
    y_positions = {cap.reference: cap.reference for cap in caps if cap.reference is not None}
    type_info[typ] = {"min": min_ref, "max": max_ref, "height": height, "caps": caps, "y_positions": y_positions}

# --- Determine Grid Layout ---
n_types = len(types)
if n_types == 1:
    nrows, ncols = 1, 1
elif n_types == 2:
    nrows, ncols = 1, 2
elif n_types == 3:
    nrows, ncols = 1, 3
elif n_types == 4:
    nrows, ncols = 2, 2
elif n_types in (5, 6):
    nrows, ncols = 2, 3
else:
    nrows, ncols = 1, n_types

fig_width, fig_height = 7 * ncols, max_height * nrows
fig, axes = plt.subplots(nrows, ncols, figsize=(fig_width, fig_height))
axes = axes.flatten() if n_types > 1 else [axes]

# --- Map Types to Axes ---
type_axes = {}
for i, typ in enumerate(types):
    ax = axes[i]
    ax.set_title(f"{typ} Capabilities", fontsize=14, fontweight="bold")
    ax.axis('off')
    type_axes[typ] = ax
for ax in axes[len(types):]:
    ax.axis('off')

# --- Draw Capabilities and Empty Regions ---
for typ in types:
    ax = type_axes[typ]
    info = type_info[typ]
    for cap in info["caps"]:
        if cap.reference is None:
            continue
        draw_capability(ax, cap, info["y_positions"].get(cap.reference, cap.reference))
    # Draw empty memory blocks.
    occupied = set(info["y_positions"].values())
    for addr in sorted(set(range(info["min"], info["max"] + 1)) - occupied):
        ax.broken_barh([(0, 64)], (addr, 0.8), color='rosybrown', edgecolor='black')

# --- Prepare Axis Info for Arrows ---
type_axes_info = {}
for typ in types:
    ax = type_axes[typ]
    pos = ax.get_position()
    center_x = (pos.x0 + pos.x1) / 2
    type_axes_info[typ] = {"axis": ax, "min": type_info[typ]["min"], "max": type_info[typ]["max"], "center_x": center_x}

# --- Global Overlay Axis for Arrows ---
ax_global = fig.add_axes([0, 0, 1, 1], frameon=False)
ax_global.set_xticks([]); ax_global.set_yticks([])
ax_global.patch.set_alpha(0)

# --- Helper: Transform point from an axis to figure coordinates ---
def to_fig_coords(ax, point):
    disp = ax.transData.transform(point)
    return fig.transFigure.inverted().transform(disp)

# --- Draw Arrows and Print Their Coordinates ---
for typ in types:
    src_ax = type_axes_info[typ]["axis"]
    for cap in type_info[typ]["caps"]:
        if cap.reference is None:
            continue
        src_y = type_info[typ]["y_positions"].get(cap.reference, cap.reference)
        addr_val = cap.getAddress()
        if addr_val is None:
            continue
        # Find target type whose reference range covers the address.
        target_type = next((t for t in types if type_axes_info[t]["min"] <= addr_val <= type_axes_info[t]["max"]), None)
        if not target_type:
            continue
        tgt_ax = type_axes_info[target_type]["axis"]
        tgt_y = addr_val + random.uniform(0.1, 0.6)
        x_min, x_max = -1, 65

        if typ == target_type:
            if addr_val < cap.reference:
                src_x, tgt_x, style = -2, -2, "arc3, rad=0.3"
            else:
                src_x, tgt_x, style = x_max + 1, x_max + 1, "arc3, rad=-0.3"
        else:
            src_center = type_axes_info[typ]["center_x"]
            tgt_center = type_axes_info[target_type]["center_x"]
            style = "arc3"
            src_x, tgt_x = (x_max, x_min) if src_center < tgt_center else (x_min, x_max)

        src_pt = (src_x, src_y + 0.5)
        tgt_pt = (tgt_x, tgt_y)
        src_fig = to_fig_coords(src_ax, src_pt)
        tgt_fig = to_fig_coords(tgt_ax, tgt_pt)

        arrow = patches.FancyArrowPatch(src_fig, tgt_fig, transform=fig.transFigure,
                                         arrowstyle="-|>", mutation_scale=12, linewidth=3,
                                         color="black", connectionstyle=style)
        ax_global.add_patch(arrow)
        print(f"Arrow from ({src_fig[0]:.2f}, {src_fig[1]:.2f}) to ({tgt_fig[0]:.2f}, {tgt_fig[1]:.2f})")


plt.show()
