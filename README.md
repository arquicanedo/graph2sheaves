# graph2sheaves
Sheaves library for graph abstractions based on NetworkX

## General
This library, inspired by [1], provides the basic functionality to create sheaves from graphs. The goal is to explore novel algorithms for graph abstraction, summarization, compositionality, and learning.

## Related Work
* PySheaf: Sheaf-theoretic toolbox (https://github.com/kb1dds/pysheaf)

## Sheaves from Text
Consider the following example from [1]. 

```
'fly like a butterfly'
'airplanes that fly'
'fly fishing'
'fly away home'
'fly ash in concrete'
'when sparks fly'
'lets fly a kite'
'learn to fly helicopters'
```

In this example, every sentence represents a section in a sheaf. For every germ (i.e., word) in the sheaf's projection, a stalk is created. The resulting sheaf is shown below. The solid blue lines represent stalks, and the dotted blue lines are the projections of stalks into the base space.


![alt text](figures/sheaf_text_fly.png)


## References
[1] Linas Vepstas, "Sheaves: A Topological Approach to Big Data", https://arxiv.org/abs/1901.01341, 2019.  
[2] Justin Michael Curry, "Sheaves, Cosheaves and Applications", https://arxiv.org/pdf/1303.3255.pdf, 2014.
