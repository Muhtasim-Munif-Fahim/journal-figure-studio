# Integration Guide

## With LaTeX documents
Include the output package's latex_include.tex in your document:
```latex
\input{figures/my-figure/latex_include.tex}
```

## With Word documents
Use the word_insertion.txt instructions to place figures.

## With CI/CD
Run render_recipe.py as part of your analysis pipeline:
```yaml
- name: Generate figures
  run: python scripts/render_recipe.py --request figure_request.yaml
```
