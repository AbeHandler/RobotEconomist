### Dec 16, 2022

Using seeds.txt we make training data for pseudo yeses and pseudo nos for determining if a sentence from a management science paper (or other corpus) is causal. 

We use this to train a LR model to predict if a sentence is causal.

We show high probability sentences to annotators for confirmation.

Then we extract the cause X and effect Y in a new annotation step.