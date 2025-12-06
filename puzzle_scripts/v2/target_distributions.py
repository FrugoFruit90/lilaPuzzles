import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

def load_data():
    """Load both competition datasets"""
    # Load first competition from JSON
    with open('data/puzzle_evaluation2024-09-01.json', 'r') as f:
        first_comp_dict = json.load(f)
    first_comp = pd.DataFrame(list(first_comp_dict.items()), columns=['puzzle', 'rating'])
    
    # Load second competition from CSV
    second_comp = pd.read_csv('data/puzzle_ratings_final_2025-02-24.csv')
    
    return first_comp, second_comp

def plot_rating_distributions(first_comp, second_comp):
    """Create overlapping bar chart of rating distributions"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Define bins for ratings (500-3100 range)
    bins = np.arange(500, 3150, 50)
    
    # Create histograms with explicit edge colors to avoid overlap confusion
    ax.hist(first_comp['rating'], bins=bins, alpha=0.6, color='blue', 
            edgecolor='darkblue', linewidth=0.5,
            label=f'First Competition)', density=True)
    ax.hist(second_comp['rating'], bins=bins, alpha=0.6, color='red', 
            edgecolor='darkred', linewidth=0.5,
            label=f'Second Competition)', density=True)
    
    # Customize plot
    ax.set_xlabel('Rating', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.set_title('Distribution of Chess Puzzle Ratings: First vs Second Competition', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Set x-axis limits
    ax.set_xlim(500, 3100)
    
    plt.tight_layout()
    return fig

def print_summary_stats(first_comp, second_comp):
    """Print summary statistics for both datasets"""
    print("FIRST COMPETITION STATISTICS:")
    print(f"Count: {len(first_comp)}")
    print(f"Mean: {first_comp['rating'].mean():.2f}")
    print(f"Median: {first_comp['rating'].median():.2f}")
    print(f"Std: {first_comp['rating'].std():.2f}")
    print(f"Min: {first_comp['rating'].min()}")
    print(f"Max: {first_comp['rating'].max()}")
    
    print("\nSECOND COMPETITION STATISTICS:")
    print(f"Count: {len(second_comp)}")
    print(f"Mean: {second_comp['rating'].mean():.2f}")
    print(f"Median: {second_comp['rating'].median():.2f}")
    print(f"Std: {second_comp['rating'].std():.2f}")
    print(f"Min: {second_comp['rating'].min()}")
    print(f"Max: {second_comp['rating'].max()}")

def main():
    # Load data
    first_comp, second_comp = load_data()
    
    # Print summary statistics
    print_summary_stats(first_comp, second_comp)
    
    # Create and show plot
    fig = plot_rating_distributions(first_comp, second_comp)
    plt.show()
    
    # Save plot
    fig.savefig('puzzle_scripts/v2/rating_distributions_comparison.png', dpi=300, bbox_inches='tight')
    print("\nPlot saved as 'puzzle_scripts/v2/rating_distributions_comparison.png'")

if __name__ == "__main__":
    main()