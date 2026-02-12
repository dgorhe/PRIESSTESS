#!/usr/bin/env python3
"""
Visualization script for PRIESSTESS results.
Creates logo plots for all motifs and bar graphs for model weights.
"""

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path

# Color schemes for different alphabets (matching R script colors)
COLOR_SCHEMES = {
    "seq-4": {
        "A": "#00CC00",  # Green
        "C": "#0000CC",  # Blue
        "G": "#FFB302",  # Orange/Yellow
        "U": "#CC0001",  # Red
    },
    "struct-2": {
        "U": "#000000",  # Black
        "P": "#ff006b",  # Pink
    },
    "struct-4": {
        "P": "#ff006b",  # Pink
        "L": "#008060",  # Teal
        "U": "#000000",  # Black
        "M": "#01C8CA",  # Cyan
    },
    "struct-7": {
        "B": "#e67300",  # Orange
        "E": "#000000",  # Black
        "H": "#008060",  # Teal
        "L": "#bb00cc",  # Purple
        "M": "#01C8CA",  # Cyan
        "R": "#ff006b",  # Pink
        "T": "#6b00ff",  # Blue
    },
    "seq-struct-8": {
        # For seq-struct-8, we'll split into seq and struct components
        "seq": {
            "A": "#00CC00",
            "C": "#0000CC",
            "G": "#FFB302",
            "U": "#CC0001",
        },
        "struct": {
            "U": "#000000",
            "P": "#ff006b",
        },
    },
    "seq-struct-16": {
        "seq": {
            "A": "#00CC00",
            "C": "#0000CC",
            "G": "#FFB302",
            "U": "#CC0001",
        },
        "struct": {
            "P": "#ff006b",
            "L": "#008060",
            "U": "#000000",
            "M": "#01C8CA",
        },
    },
    "seq-struct-28": {
        "seq": {
            "A": "#00CC00",
            "C": "#0000CC",
            "G": "#FFB302",
            "U": "#CC0001",
        },
        "struct": {
            "B": "#e67300",
            "E": "#000000",
            "H": "#008060",
            "L": "#bb00cc",
            "M": "#01C8CA",
            "R": "#ff006b",
            "T": "#6b00ff",
        },
    },
}

# Mapping for seq-struct alphabets
SEQ_STRUCT_MAPPING = {
    "seq-struct-8": "struct-2",
    "seq-struct-16": "struct-4",
    "seq-struct-28": "struct-7",
}


def read_pfm(pfm_file):
    """Read a PFM file and return as numpy array with row labels."""
    with open(pfm_file, 'r') as f:
        lines = f.readlines()

    symbols = []
    data = []
    for line in lines:
        if line.strip():
            parts = line.strip().split('\t')
            symbols.append(parts[0])
            data.append([float(x) for x in parts[1:]])

    return np.array(symbols), np.array(data)


def calculate_information_content(pfm_matrix):
    """Calculate information content (bits) for each position."""
    # Normalize each column to sum to 1
    pfm_normalized = pfm_matrix / (pfm_matrix.sum(axis=0) + 1e-10)

    # Calculate entropy for each position
    entropy = -np.sum(pfm_normalized * np.log2(pfm_normalized + 1e-10), axis=0)

    # Information content = max entropy - entropy
    max_entropy = np.log2(pfm_matrix.shape[0])
    ic = max_entropy - entropy

    return ic, pfm_normalized


def split_seq_struct_pfm(pfm_matrix, symbols, alphabet):
    """Split a seq-struct PFM into sequence and structure components."""
    struct_alphabet = SEQ_STRUCT_MAPPING[alphabet]
    struct_symbols = list(COLOR_SCHEMES[struct_alphabet].keys())
    n_struct = len(struct_symbols)

    # Sequence PFM (A, C, G, U)
    seq_pfm = np.zeros((4, pfm_matrix.shape[1]))
    seq_symbols = ["A", "C", "G", "U"]

    for i, seq_sym in enumerate(seq_symbols):
        for j in range(pfm_matrix.shape[1]):
            # Sum over all struct symbols for this seq symbol
            seq_pfm[i, j] = np.sum(pfm_matrix[i * n_struct:(i + 1) * n_struct, j])

    # Structure PFM
    struct_pfm = np.zeros((n_struct, pfm_matrix.shape[1]))
    for i, struct_sym in enumerate(struct_symbols):
        for j in range(pfm_matrix.shape[1]):
            # Sum over all seq symbols for this struct symbol
            struct_pfm[i, j] = np.sum(pfm_matrix[i::n_struct, j])

    return seq_pfm, seq_symbols, struct_pfm, struct_symbols


def plot_logo(pfm_matrix, symbols, alphabet, ax, title=None, method="bits"):
    """Create a sequence logo plot."""
    ic, pfm_normalized = calculate_information_content(pfm_matrix)

    if method == "bits":
        max_height = np.log2(len(symbols))
    else:  # probability
        max_height = 1.0

    n_positions = pfm_matrix.shape[1]

    # Get color scheme
    if alphabet.startswith("seq-struct"):
        # This shouldn't be called directly for seq-struct
        colors = COLOR_SCHEMES["seq-4"]
    else:
        colors = COLOR_SCHEMES.get(alphabet, {})

    # Plot each position
    x_positions = np.arange(n_positions)
    bottom = np.zeros(n_positions)

    for i, symbol in enumerate(symbols):
        heights = pfm_normalized[i, :] * ic if method == "bits" else pfm_normalized[i, :]
        color = colors.get(symbol, "#000000")

        ax.bar(x_positions, heights, bottom=bottom, width=0.8,
               color=color, edgecolor='white', linewidth=0.5, label=symbol)
        bottom += heights

    ax.set_xlim(-0.5, n_positions - 0.5)
    ax.set_ylim(0, max_height * 1.1)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(range(1, n_positions + 1))
    ax.set_xlabel("Position", fontsize=10)
    if method == "bits":
        ax.set_ylabel("Bits", fontsize=10)
    else:
        ax.set_ylabel("Probability", fontsize=10)
    if title:
        ax.set_title(title, fontsize=11, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3, linestyle='--')


def create_logo_plots(output_dir, priesstess_output_dir):
    """Create logo plots for all PFM files."""
    priesstess_path = Path(priesstess_output_dir)
    logos_dir = Path(output_dir) / "logos"
    logos_dir.mkdir(parents=True, exist_ok=True)

    # Find all alphabet directories
    alphabet_dirs = [d for d in priesstess_path.iterdir()
                     if d.is_dir() and not d.name.startswith('.')]

    for alphabet_dir in alphabet_dirs:
        alphabet_name = alphabet_dir.name
        pfm_files = sorted(alphabet_dir.glob("PFM-*.txt"))

        if not pfm_files:
            continue

        print(f"Processing {alphabet_name}: {len(pfm_files)} motifs")

        for pfm_file in pfm_files:
            try:
                symbols, pfm_matrix = read_pfm(pfm_file)
                motif_id = pfm_file.stem  # e.g., "PFM-1"

                # Handle seq-struct alphabets
                if alphabet_name.startswith("seq-struct"):
                    seq_pfm, seq_symbols, struct_pfm, struct_symbols = \
                        split_seq_struct_pfm(pfm_matrix, symbols, alphabet_name)

                    # Create figure with two subplots
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(
                        max(6, pfm_matrix.shape[1] * 0.8), 4))

                    plot_logo(seq_pfm, seq_symbols, "seq-4", ax1,
                              f"{alphabet_name}_{motif_id} - Sequence", method="bits")
                    plot_logo(struct_pfm, struct_symbols,
                              SEQ_STRUCT_MAPPING[alphabet_name], ax2,
                              f"{alphabet_name}_{motif_id} - Structure", method="bits")

                    plt.tight_layout()
                    output_file = logos_dir / f"{alphabet_name}_{motif_id}_logo.png"
                    plt.savefig(output_file, dpi=150, bbox_inches='tight')
                    plt.close()
                else:
                    # Single logo plot
                    fig, ax = plt.subplots(figsize=(max(6, pfm_matrix.shape[1] * 0.8), 3))
                    plot_logo(pfm_matrix, symbols, alphabet_name, ax,
                              f"{alphabet_name}_{motif_id}", method="bits")
                    plt.tight_layout()
                    output_file = logos_dir / f"{alphabet_name}_{motif_id}_logo.png"
                    plt.savefig(output_file, dpi=150, bbox_inches='tight')
                    plt.close()

            except Exception as e:
                print(f"Error processing {pfm_file}: {e}", file=sys.stderr)
                continue

    print(f"Logo plots saved to {logos_dir}")


def create_weight_barplot(output_dir, weights_file):
    """Create bar plot of model weights grouped by alphabet type."""
    # Read weights file
    weights_data = []
    with open(weights_file, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    feature = parts[0]
                    weight = float(parts[1])
                    weights_data.append((feature, weight))

    if not weights_data:
        print("No weights data found", file=sys.stderr)
        return

    # Parse alphabet and PFM ID
    parsed_data = []
    for feature, weight in weights_data:
        if '_' in feature:
            alphabet, pfm_id = feature.split('_', 1)
            parsed_data.append({
                'alphabet': alphabet,
                'pfm_id': pfm_id,
                'feature': feature,
                'weight': weight
            })

    if not parsed_data:
        print("Could not parse weights data", file=sys.stderr)
        return

    # Group by alphabet type
    alphabet_groups = {}
    for item in parsed_data:
        alphabet = item['alphabet']
        # Determine group
        if alphabet == "seq-4":
            group = "Sequence-only (seq-4)"
        elif alphabet.startswith("seq-struct"):
            group = f"Sequence+Structure ({alphabet})"
        elif alphabet.startswith("struct"):
            group = f"Structure-only ({alphabet})"
        else:
            group = alphabet

        if group not in alphabet_groups:
            alphabet_groups[group] = []
        alphabet_groups[group].append(item)

    # Create color palette
    n_groups = len(alphabet_groups)
    colors = sns.color_palette("husl", n_groups)
    group_colors = {group: colors[i] for i, group in enumerate(sorted(alphabet_groups.keys()))}

    # Prepare data for plotting
    all_features = []
    all_weights = []
    all_groups = []
    all_colors = []

    # Sort groups and within groups
    sorted_groups = sorted(alphabet_groups.keys())
    for group in sorted_groups:
        items = sorted(alphabet_groups[group], key=lambda x: x['weight'], reverse=True)
        for item in items:
            all_features.append(item['feature'])
            all_weights.append(item['weight'])
            all_groups.append(group)
            all_colors.append(group_colors[group])

    # Create figure with better sizing
    fig_width = max(14, len(all_features) * 0.4)
    fig, ax = plt.subplots(figsize=(fig_width, 8))

    # Create bar plot
    x_positions = np.arange(len(all_features))
    bars = ax.bar(x_positions, all_weights, color=all_colors, edgecolor='black', linewidth=0.5, alpha=0.8)

    # Add group separators
    current_group = None
    separator_positions = []
    for i, group in enumerate(all_groups):
        if group != current_group:
            if current_group is not None:
                separator_positions.append(i - 0.5)
            current_group = group
    separator_positions.append(len(all_features) - 0.5)

    # Draw separator lines
    for pos in separator_positions:
        ax.axvline(x=pos, color='gray', linestyle='--', linewidth=2, alpha=0.7)

    # Customize plot
    ax.set_xlabel("Motif Feature", fontsize=12, fontweight='bold')
    ax.set_ylabel("Model Weight", fontsize=12, fontweight='bold')
    ax.set_title("PRIESSTESS Model Weights by Alphabet Type", fontsize=14, fontweight='bold')
    ax.set_xticks(x_positions)
    
    # Improve label readability - rotate and adjust font size based on number of features
    if len(all_features) > 20:
        rotation = 90
        fontsize = 7
    else:
        rotation = 45
        fontsize = 8
    ax.set_xticklabels(all_features, rotation=rotation, ha='right', fontsize=fontsize)
    
    # Set y-axis to start at 0
    ax.set_ylim(bottom=0)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Create legend
    legend_elements = [mpatches.Patch(facecolor=group_colors[group],
                                      edgecolor='black', label=group)
                       for group in sorted_groups]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    plt.tight_layout()

    # Save figure
    output_file = Path(output_dir) / "model_weights_barplot.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Weight bar plot saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize PRIESSTESS results: create logo plots and weight bar graphs"
    )
    parser.add_argument(
        "priesstess_output_dir",
        type=str,
        help="Path to PRIESSTESS output directory (e.g., RBFOX2_output/PRIESSTESS_output)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="figures",
        help="Output directory for figures (default: figures)"
    )
    parser.add_argument(
        "--weights-file",
        type=str,
        default=None,
        help="Path to PRIESSTESS_model_weights.tab file (default: <priesstess_output_dir>/PRIESSTESS_model_weights.tab)"
    )

    args = parser.parse_args()

    # Validate input directory
    priesstess_path = Path(args.priesstess_output_dir)
    if not priesstess_path.exists():
        print(
            f"Error: PRIESSTESS output directory '{args.priesstess_output_dir}' not found", file=sys.stderr)
        sys.exit(1)

    # Set default weights file if not provided
    if args.weights_file is None:
        weights_file = priesstess_path / "PRIESSTESS_model_weights.tab"
    else:
        weights_file = Path(args.weights_file)

    if not weights_file.exists():
        print(
            f"Warning: Weights file '{weights_file}' not found. Skipping bar plot.", file=sys.stderr)
        weights_file = None

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Creating visualizations...")
    print(f"Output directory: {output_dir}")
    print(f"PRIESSTESS output: {priesstess_path}")

    # Create logo plots
    create_logo_plots(output_dir, priesstess_path)

    # Create weight bar plot
    if weights_file:
        create_weight_barplot(output_dir, weights_file)

    print("Visualization complete!")


if __name__ == "__main__":
    main()
