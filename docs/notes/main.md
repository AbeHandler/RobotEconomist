---
id: ep3hm7spo8ja9z5r7fwez4u
title: Main
desc: ''
updated: 1662742801983
created: 1658681337744
---

## ideas

we may want to run the tagger in high-recall mode that is noisy and makes a noisy dag
For context you can use vector-based similarity. So like you can find that the China vertex is close to the Japan one

- "Dag on demand": At query time, build a dag on demand. Perform a search over the similar things. So do a bfs to see if you can get from instrument to outcome over what level of semantic similarity? You could query for similar nodes at query time, or build the similar nodes into the graph at index time.
- Vector database?

## What are the overall steps?
- Information extraction.
- Vector representations of the extracted entities.
- Building a dag (at index or query time)
- Querying the dag


### Other

p(phrase | instrument) vs p(phrase)

Make a tiny corpus where you can reason about it perfectly.
This is in fixtures. We are missing an edge

We need a tiny corpus to test it or you can reason about it perfectly.


Iv
- [x] Tagger find certain number of tags with certain properties from the file.
- [x] The vertex should have a list of papers associated with it. Not a single paper.
- [x] Analyzer dedupes all those tags.
Analyzer correctly infers relationship vertex is between the tags.
Auditor finds that it is not kosher.
The example should have duplicate tags in it. The same affects relationship should be two papers the same tag should be in two papers.
Edges can also have evidence tags in them. So a dag data  edge has It was associated evidence  papers.
Vertex merger class. Determines co-reference. Between a list of vortexes. For now, string co reference.
Human assisted code reference merger.

What needs to work?
Vertex co reference needs to work.
What else needs to work? Edge imputation
Information extraction. Just add money.

[[root]]