# Figure Type Selection Guide

| Figure type | Best for | Required columns |
|------------|----------|-----------------|
| bar | Comparing categories | category, value |
| ablation | Component removal experiments | category, value |
| line | Trends over continuous x | x, y |
| time_series | Temporal data | x, y |
| training_curve | ML training progress | x, y |
| scatter | Correlation between variables | x, y |
| distribution | Data spread per group | x, y |
| forest | Effect sizes with CIs | x, y, lower, upper |
| heatmap | Matrix/2D intensity | row, col, value |
| calibration | Predicted vs observed | x, y |
