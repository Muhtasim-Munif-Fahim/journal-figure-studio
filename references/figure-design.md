# Figure Design

Build one figure around one message. Show the estimate and uncertainty before decoration.

## Choose The Form

- Use `forest` for effect estimates with confidence intervals.
- Use `line` or `time_series` for trajectories, training, and responses over ordered horizons.
- Use `scatter` for association with the fitted relationship clearly distinguished from observations.
- Use `bar` only for limited categorical comparisons; prefer dots or intervals when individual estimates matter.
- Use `distribution` for spread, skew, and sample-level variability.
- Use `heatmap` for a dense matrix with an explicit colour scale.
- Use `calibration` for predicted versus observed risk or probability.
- Use `ablation` for controlled component removal with the same metric and data split.

## Caption Contract

Start with what the figure shows. State the data or population, measure, uncertainty definition, and one conclusion warranted by the plotted evidence. Do not write causal language for descriptive or predictive results.

## Panel Contract

Order panels from primary evidence to qualification or robustness. Use panel labels only for a multi-panel figure. Share scales only when a shared scale permits a valid comparison.
