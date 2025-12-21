#!/usr/bin/env python3
"""Script to generate performance report."""
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import json
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def generate_report(metrics_file: str, output_dir: str):
    """Generate performance report with tables and graphs.
    
    Args:
        metrics_file: Path to metrics JSON file
        output_dir: Output directory for report
    """
    # Load metrics
    if not Path(metrics_file).exists():
        print(f"Metrics file not found: {metrics_file}")
        return 1
    
    with open(metrics_file, 'r') as f:
        metrics = json.load(f)
    
    if not metrics:
        print("No metrics found in file")
        return 1
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create DataFrame
    data = []
    for model_name, model_metrics in metrics.items():
        map50 = model_metrics.get("map50", 0)
        map50_95 = model_metrics.get("map50_95", 0)
        inference_time = model_metrics.get("avg_inference_time_ms", 0)
        
        # Validate data
        if map50 == 0 and map50_95 == 0 and inference_time == 0:
            print(f"Warning: No metrics found for {model_name}, using placeholder values")
        
        data.append({
            "Model": model_name.upper(),
            "mAP50": map50,
            "mAP50-95": map50_95,
            "Avg Inference Time (ms)": inference_time
        })
    
    if not data:
        print("No valid metrics data found")
        return 1
    
    df = pd.DataFrame(data)
    
    # Save table
    table_path = output_path / "performance_table.csv"
    df.to_csv(table_path, index=False)
    print(f"Performance table saved to: {table_path}")
    
    # Create visualizations
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # mAP50 comparison
    axes[0].bar(df["Model"], df["mAP50"], color=['#3498db', '#e74c3c'])
    axes[0].set_title("mAP50 Comparison")
    axes[0].set_ylabel("mAP50")
    axes[0].axhline(y=0.85, color='g', linestyle='--', label='Target (85%)')
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.3)
    
    # mAP50-95 comparison
    axes[1].bar(df["Model"], df["mAP50-95"], color=['#3498db', '#e74c3c'])
    axes[1].set_title("mAP50-95 Comparison")
    axes[1].set_ylabel("mAP50-95")
    axes[1].grid(axis='y', alpha=0.3)
    
    # Inference time comparison
    axes[2].bar(df["Model"], df["Avg Inference Time (ms)"], color=['#3498db', '#e74c3c'])
    axes[2].set_title("Average Inference Time")
    axes[2].set_ylabel("Time (ms)")
    axes[2].axhline(y=300, color='r', linestyle='--', label='Target (300ms)')
    axes[2].legend()
    axes[2].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    graph_path = output_path / "performance_graphs.png"
    plt.savefig(graph_path, dpi=300, bbox_inches='tight')
    print(f"Performance graphs saved to: {graph_path}")
    
    # Generate markdown report
    report_path = output_path / "performance_report.md"
    with open(report_path, 'w') as f:
        f.write("# Performance Report - Crack Detection Models\n\n")
        f.write("## Summary\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n\n## Targets\n\n")
        f.write("- mAP50 > 85%\n")
        f.write("- Inference time < 300ms\n\n")
        f.write("## Results\n\n")
        for _, row in df.iterrows():
            f.write(f"### {row['Model']}\n\n")
            f.write(f"- mAP50: {row['mAP50']:.2%}\n")
            f.write(f"- mAP50-95: {row['mAP50-95']:.2%}\n")
            f.write(f"- Avg Inference Time: {row['Avg Inference Time (ms)']:.2f} ms\n\n")
    
    print(f"Report saved to: {report_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("Performance Summary")
    print("="*60)
    for _, row in df.iterrows():
        print(f"\n{row['Model']}:")
        print(f"  mAP50: {row['mAP50']:.2%}")
        print(f"  mAP50-95: {row['mAP50-95']:.2%}")
        print(f"  Avg Inference Time: {row['Avg Inference Time (ms)']:.2f} ms")
        
        # Check targets
        if row['mAP50'] >= 0.85:
            print(f"  mAP50 meets target (>= 85%)")
        else:
            print(f"  mAP50 below target (need >= 85%)")
        
        if row['Avg Inference Time (ms)'] <= 300:
            print(f"  Inference time meets target (<= 300ms)")
        else:
            print(f"  Inference time exceeds target (need <= 300ms)")
    
    print("\n" + "="*60)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate performance report")
    parser.add_argument("--metrics", type=str, required=True, help="Metrics JSON file")
    parser.add_argument("--output", type=str, default="reports", help="Output directory")
    
    args = parser.parse_args()
    exit(generate_report(args.metrics, args.output))

