import os
import json
import random
from matplotlib import patches, pyplot as plt
import matplotlib.cm as cm

# --- Configuration Constants ---
expected_keys = ["Tag", "Permissions", "Executive", "Global", "Object Type", "Bounds", "Address", "Reference"]
fixed_widths = [1, 16, 1, 1, 15, 31]  # used for the first row of each drawn capability

# --- Load JSON Data ---
file_path = "input.json"
if not os.path.exists(file_path):
    print(f"Error: File '{file_path}' not found.")
    exit()
with open(file_path, "r") as file:
    data = json.load(file)

# --- Group Capabilities by Type ---
# (Each capability is expected to have a key "Type" and a numeric "Reference")
type_caps = {}
for cap in data:
    typ = cap["Type"]
    if typ not in type_caps:
        type_caps[typ] = []
    type_caps[typ].append(cap)

# For consistency, sort the capabilities within each type (using the "Reference" value)
for typ in type_caps:
    type_caps[typ] = sorted(type_caps[typ], key=lambda cap: cap["Reference"], reverse=True)

# Get a sorted list of types (alphabetical order here)
types = sorted(type_caps.keys())


# --- Helper Functions ---
def get_reference_range(capabilities):
    """Return (min, max) of the 'Reference' values in a list of capabilities."""
    if not capabilities:
        return 0, 1
    refs = [cap["Reference"] for cap in capabilities]
    return min(refs), max(refs)


def calculate_figure_height(min_ref, max_ref, num_caps, base_height=6, height_per_cap=0.6, range_factor=1.5):
    """Compute a subplot height based on the reference range and number of capabilities."""
    ref_range = max_ref - min_ref
    range_based = ref_range * range_factor
    num_based = num_caps * height_per_cap
    return max(base_height, range_based, num_based)


def draw_capability(ax, capability, y_position):
    """
    Draw a single capability on axis ax at vertical position y_position.
    The capability is split into a top row with colored fields (except the last field)
    and a bottom gray row with the address.
    """
    # Get all fields except "Reference"
    sections = [capability[key] for key in expected_keys if key != "Reference"]
    # The last field is used as the address label
    section_labels = sections[:-1]
    address_label = str(sections[-1])
    reference = capability.get("Reference", None)

    # Compute positions for the colored boxes (first row)
    row_1 = []
    start = -1
    colors = cm.tab20.colors  # use a colormap for colors
    for label, width in zip(section_labels, fixed_widths):
        row_1.append((start, width))
        start += width
    # The entire row (the gray background for the address) spans from 0 to start
    row_2 = [(0, start)]

    # Draw the colored boxes and text
    for (x, w), label, color in zip(row_1, section_labels, colors):
        ax.broken_barh([(x, w)], (y_position + 0.44, 0.4), color=color, edgecolor="black")
        ax.text(x + w / 2, y_position + 0.6, label, ha='center', va='center', fontsize=10)

    # Draw the gray row and the address label
    ax.broken_barh(row_2, (y_position, 0.4), color='lightgrey', edgecolor="black")
    ax.text(start / 2, y_position + 0.18, address_label, ha='center', va='center', fontsize=10)

    # Optionally add the reference value as extra text
    if reference is not None:
        ax.text(start + 1, y_position + 0.05, f"Ref: {reference}",
                fontsize=10, fontweight='bold', color='black')

    # Set x-limits; note that start is –1 + sum(fixed_widths) (typically 64), so xlim becomes (-1, 65)
    ax.set_xlim(-1, start + 1)


# --- Pre-calculate Info for Each Type ---
# For each type, record the minimum and maximum "Reference", a computed subplot height,
# and a mapping of each capability’s "Reference" (used as its y-position).
type_info = {}  # keys: type; values: dict with "min", "max", "height", "caps", "y_positions"
max_subplot_height = 0
for typ in types:
    caps = type_caps[typ]
    min_ref, max_ref = get_reference_range(caps)
    height = calculate_figure_height(min_ref, max_ref, len(caps))
    max_subplot_height = max(max_subplot_height, height)
    # For drawing we simply use each capability’s "Reference" as its y coordinate.
    y_positions = {cap["Reference"]: cap["Reference"] for cap in caps}
    type_info[typ] = {"min": min_ref, "max": max_ref, "height": height, "caps": caps, "y_positions": y_positions}

# --- Decide on a Grid Layout for Subplots ---
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
    nrows, ncols = 1, n_types  # fallback

# Let the overall figure width scale with the number of columns (each subplot roughly 7 inches wide)
fig_width = 7 * ncols
# For height, use the maximum subplot height multiplied by the number of rows
fig_height = max_subplot_height * nrows
fig, axes = plt.subplots(nrows, ncols, figsize=(fig_width, fig_height))
# If we have more than one subplot, flatten the axes array for easy iteration.
if n_types > 1:
    axes = axes.flatten()
else:
    axes = [axes]

# --- Map Each Type to an Axis ---
type_to_axis = {}
for i, typ in enumerate(types):
    ax = axes[i]
    type_to_axis[typ] = ax
    ax.set_title(f"{typ} Capabilities", fontsize=14, fontweight="bold")
    ax.axis('off')
# Hide any extra (unused) subplots.
for j in range(len(types), len(axes)):
    axes[j].axis('off')

# --- Draw Capabilities and Empty Memory Regions ---
for typ in types:
    ax = type_to_axis[typ]
    info = type_info[typ]
    caps = info["caps"]
    y_positions = info["y_positions"]
    # Draw each capability (the row with colored boxes, etc.)
    for cap in caps:
        y_pos = y_positions[cap["Reference"]]
        draw_capability(ax, cap, y_pos)
    # Draw empty memory blocks where no capability exists.
    occupied = set(y_positions.values())
    all_addresses = set(range(info["min"], info["max"] + 1))
    empty_addresses = sorted(all_addresses - occupied)
    for empty in empty_addresses:
        ax.broken_barh([(0, 64)], (empty, 0.8), color='rosybrown', edgecolor='black')

# --- Prepare Data for Arrow Connections ---
# For each type, we store its axis, its reference range, and its axis’s x-center (in figure coords)
type_axes_info = {}
for typ in types:
    ax = type_to_axis[typ]
    pos = ax.get_position()  # in figure coordinates
    center_x = (pos.x0 + pos.x1) / 2
    type_axes_info[typ] = {"axis": ax, "min": type_info[typ]["min"], "max": type_info[typ]["max"],
                           "center_x": center_x}

# --- Draw Arrows ---
# For each capability we try to find a target subplot whose reference range contains the capability's "Address".
# If the source and target are the same type, we draw an intra-axis (arc) arrow.
# Otherwise, we compare the axes’ center_x positions to decide whether to use the left or right edge.
for typ in types:
    source_ax = type_axes_info[typ]["axis"]
    source_caps = type_info[typ]["caps"]
    for cap in source_caps:
        source_y = type_info[typ]["y_positions"][cap["Reference"]]
        address_str = str(cap["Address"])
        try:
            address_val = int(address_str)
        except ValueError:
            continue  # skip if not an integer
        # Identify the target type: the type whose reference range covers address_val.
        target_type = None
        for t in types:
            tmin = type_axes_info[t]["min"]
            tmax = type_axes_info[t]["max"]
            if tmin <= address_val <= tmax:
                target_type = t
                break
        if target_type is None:
            continue  # no target found
        target_ax = type_axes_info[target_type]["axis"]
        # Compute target y coordinate (using a small random offset for variation)
        target_y = address_val + random.uniform(0.1, 0.6)
        # The x-limits (from draw_capability) are fixed: (-1, 65)
        x_min, x_max = -1, 65

        if typ == target_type:
            # Intra-axis arrow: decide which side to use.
            # (For example, if the target address is below the source's reference,
            # draw an arrow along the left edge; otherwise, along the right edge.)
            if address_val < cap["Reference"]:
                source_x = -2
                target_x = -2
                connection_style = "arc3, rad=0.3"
            else:
                source_x = x_max + 1  # e.g. 66
                target_x = x_max + 1
                connection_style = "arc3, rad=-0.3"
            arrow = patches.ConnectionPatch((source_x, source_y + 0.5),
                                            (target_x, target_y),
                                            coordsA=source_ax.transData,
                                            coordsB=target_ax.transData,
                                            arrowstyle="-|>",
                                            mutation_scale=12,
                                            linewidth=3,
                                            connectionstyle=connection_style,
                                            color="black")
            fig.patches.append(arrow)
        else:
            # Inter-axis arrow: decide which side to use based on the axes' centers.
            source_center = type_axes_info[typ]["center_x"]
            target_center = type_axes_info[target_type]["center_x"]
            if source_center < target_center:
                # Draw arrow from the right edge of the source to the left edge of the target.
                source_x = x_max
                target_x = x_min
            else:
                source_x = x_min
                target_x = x_max
            arrow = patches.ConnectionPatch((source_x, source_y + 0.5),
                                            (target_x, target_y),
                                            coordsA=source_ax.transData,
                                            coordsB=target_ax.transData,
                                            arrowstyle="-|>",
                                            mutation_scale=12,
                                            linewidth=3,
                                            color="black")
            fig.patches.append(arrow)

# --- Final Adjustments and Show the Figure ---
#plt.tight_layout()
plt.show()
