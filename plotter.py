#-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 Benjamin Barnes-Lewis
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

# Imports
import matplotlib.pyplot as plt, math

# Gets data needed for calculating the number of boxes
def get_sorted_locations(capabilities):
    lowestLocation = capabilities[0]["Location"]
    highestLocation = capabilities[-1]["Location"]
    return sorted(set(cap["Location"] for cap in capabilities)), lowestLocation, highestLocation

# Calculates the total number of boxes by iterating through sorted locations and adding gaps if they exist
# Input needs to be sorted so that gaps can be identified correctly
def get_Boxes_Number(sorted_locs):
    total_Boxes = 0
    for i in range(len(sorted_locs)):
        total_Boxes += 1
        if i < len(sorted_locs) - 1:
            next_loc = sorted_locs[i + 1]
            gap = next_loc - sorted_locs[i] - 1
            if gap > 0:
                total_Boxes += 1
    return total_Boxes

# Lists all boxes based on sorted locations and includes gaps
def list_Boxes(sorted_locs):
    boxes = []
    for i in range(len(sorted_locs)):
        boxes.append(sorted_locs[i])
        if i < len(sorted_locs) - 1:
            next_loc = sorted_locs[i + 1]
            gap = next_loc - sorted_locs[i] - 1
            if gap > 0:
                boxes.append("gap")
    return boxes

# Find corresponding entries in two datasets based on a specified key
def find_corresponding(data1, data2, key):
    corresponding_list = []
    
    # Iterate through both datasets and find corresponding entries based on the specified key
    for d1 in data1:
        for d2 in data2:
            if d1[key] == d2[key]:
                corresponding_list += [(d1, d2)]
    return corresponding_list

# Displays the boxes in a matplotlib figure
def display_boxes(capabilities, symbols, boxes, saveName):
    y_positions = []
    
    # Define expected fields and widths for capability display
    expected_keys = ["Tag", "Permissions", "Executive", "Global", "Object Type", "LowerBound", "UpperBound", "Address", "Location"]
    fixed_widths = [1, 16, 1, 1, 15, 15, 15]

    # Create the matplotlib figure and axis
    
    figure_width = 8
    figure_height = len(boxes) * 0.5
    fig, ax = plt.subplots(1, 1, figsize=(figure_width, figure_height))
    
    # Scale the font size to fit inside each box, based on row_height and figure height
    fontScale = (figure_height / len(boxes)) * 1.8 if len(boxes) > 0 else 1
    
    # Switch between using a logarithmic scale for the gaps and constant (0.2)
    use_Log = True
    y_gap = 0.2
    
    # Colors for the boxes
    colors = ['royalblue', 'lightblue', 'darkorange', 'sandybrown', 'green', 'lightgreen', 'springgreen']

    # Map each location to its capability data
    cap_by_location = {cap["Location"]: cap for cap in capabilities}
    row_height = 1
    
    # Loop through each box (capability or gap) and draw it
    prev_loc = None
    y_pos = 0
    for idx, item in enumerate(boxes):
        # Create a gap multiplier based on location
        if use_Log == True and idx < len(capabilities) - 1:
            gap_multiplier = math.log(capabilities[idx + 1]["Location"] - capabilities[idx]["Location"])
            gap_multiplier /= 4
        else:
            # Note: Increase this number to have larger gaps without logarithmic scaling
            gap_multiplier = 1
        
        # Determine y_gap for this box
        if idx == 0:
            y_pos = 0
        else:
            y_pos += row_height + y_gap * gap_multiplier
        
        # Differentiate between gap spaces and capability boxes
        if item == "gap":
            # Write the "..." (represents a gap)
            ax.text(sum(fixed_widths) / 2, y_pos + row_height / 2, "...", ha='center', va='center', fontsize=15*fontScale, fontweight="bold")
        else:
            # Draw a capability box
            cap = cap_by_location.get(item)
            if cap:
                # Get all field values except Location for display
                section_labels = [str(cap[key]) for key in expected_keys if key != "Location" and key in cap]
            else:
                section_labels = []
                
            # Calculate positions for coloured fields
            row_1 = []
            start = -1
            for label, width in zip(section_labels, fixed_widths):
                row_1.append((start, width))
                start += width
                
            # Draw the main capability box
            ax.broken_barh([(0, sum(fixed_widths) - 1)], (y_pos, row_height), color='grey', edgecolor='black')
            
            # Draw the address in the second row
            address = str(cap.get('Address', '')) if cap else ''
            ax.text(sum(fixed_widths) / 2, y_pos - 0.25 + row_height / 2, address, ha='center', va='center', fontsize=10*fontScale)
            
            # Log y position for symbols
            y_positions += [(y_pos, address)]
            
            # Draw coloured fields and their labels
            for (x, w), label, color in zip(row_1, section_labels, colors):
                ax.broken_barh([(x, w)], (y_pos + 0.6, row_height / 2), color=color, edgecolor='black')
                ax.text(x + w / 2, y_pos + 0.8, label, ha='center', va='center', fontsize=10*fontScale)
                
            ax.text(34.5, y_pos + 0.8, "LB:", ha='center', va='center', fontsize=10*fontScale)
            ax.text(49.5, y_pos + 0.8, "UB:", ha='center', va='center', fontsize=10*fontScale)
                
            # Display location to the right of the box
            ax.text(sum(fixed_widths), y_pos + row_height / 2 + 0.35, f"Loc: {item}", ha='left', va='center', fontsize=10*fontScale, color='black')
            prev_loc = item if isinstance(item, int) else prev_loc
    
    # Set axis limits and show the plot
    ax.set_xlim(-1, sum(fixed_widths) + 4)
    ax.set_ylim(-2, len(boxes) * (row_height + y_gap))
    
    # Iterate through symbols and place them at the correct y positions
    for idx, sym in enumerate(symbols):
        symbol_x = 68
        symbol_y = 100
        
        # Iterate through y_positions to find the correct y position for the symbol
        for i in range(len(y_positions)):
            if y_positions[i][1] == sym["addr"]:
                symbol_x, symbol_y = 68, y_positions[i][0] + 0.25
                
    symbol_offsets = {}

    for idx, sym in enumerate(symbols):
        symbol_x = 66
        symbol_y = None

        # Find the matching y-position for the address
        for y_pos_val, addr in y_positions:
            if addr == sym["addr"]:
                symbol_y = y_pos_val + 0.25
                break

        if symbol_y is None:
            continue  # Skip if no matching y was found

        # Get how many symbols already occupy this y_position
        offset = symbol_offsets.get(symbol_y, 0)

        # Calculate y offset
        y_offset = offset * 0.3 - 0.15

        # If the length of the symbol name is over 30 characters, it is split into 2 halves to make it not go off the screen
        if len(sym["symbol"]) > 30:
            # Draw the symbol labels (offset if needed)
            ax.text(symbol_x - 1.1, symbol_y - y_offset + 0.1, sym["symbol"][:int(len(sym["symbol"])/2)], ha='left', va='center', fontsize=4*fontScale, color='black')
            ax.text(symbol_x - 1.1, symbol_y - y_offset - 0.04, sym["symbol"][int(len(sym["symbol"])/2):], ha='left', va='center', fontsize=4*fontScale, color='black')
        else:
            # Draw the symbol label (offset if needed)
            ax.text(symbol_x - 1.1, symbol_y - y_offset + 0.1, sym["symbol"], ha='left', va='center', fontsize=4*fontScale, color='black')
            
        # Draw the arrow (also offset to match)
        ax.arrow(63, symbol_y - y_offset + 0.03, 1, 0, head_width=0.3, head_length=0.5, fc='white', ec='black')

        # Update the offset count for this y
        symbol_offsets[symbol_y] = offset + 1
    
    # Hide the axes
    ax.axis('off')
    
    # Set save type to change between png and svg for varying quality
    save_type = "svg"
    if save_type == "svg":
        plt.savefig(f"saves/{saveName}.svg", format="svg", dpi=1200)
    else:
        plt.savefig(f"saves/{saveName}.png")
        
    # Show plot. Note that for larger data sets (even as low as ~40) it will not be very legible, so you may not want to have it enabled
    # plt.show()