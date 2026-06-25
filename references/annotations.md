# Statistical Annotation Reference

## Significance notation

| p-value range | Symbol | Meaning |
|--------------|--------|---------|
| p ≤ 0.001 | *** | Highly significant |
| p ≤ 0.01 | ** | Very significant |
| p ≤ 0.05 | * | Significant |
| p > 0.05 | n.s. | Not significant |

## Usage

Add `p_value` field to your figure request:
```yaml
figure:
  type: bar
  x: category
  y: value
  p_value: 0.003
```

The annotation bracket is drawn automatically above the data.
