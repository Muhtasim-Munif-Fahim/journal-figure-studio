# Examples

## Basic bar chart

```yaml
figure_id: my-bar-chart
figure_type: bar
layout: single
data:
  path: results.csv
  column_mappings:
    category: method
    value: accuracy
profile: universal
```

## Multi-panel comparison

```yaml
figure_id: multi-panel
layout: double
figures:
  - type: bar
    source: data.csv
    x: method
    y: accuracy
    xlabel: Method
    ylabel: Accuracy
  - type: scatter
    source: data.csv
    x: method
    y: latency
    xlabel: Method
    ylabel: Latency (ms)
profile: universal
```

## With significance annotation

```yaml
figure:
  type: bar
  x: group
  y: score
  xlabel: Group
  ylabel: Score
  p_value: 0.003
```
