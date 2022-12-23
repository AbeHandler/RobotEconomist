### Dec 16, 2022

Using seeds.txt we make training data for pseudo yeses and pseudo nos for determining if a sentence from a management science paper (or other corpus) is causal. 

We use this to train a LR model to predict if a sentence is causal.

We show high probability sentences to annotators for confirmation.

Then we extract the cause X and effect Y in a new annotation step.


### Task? 

- Take the sentence and extract a statement of the form X causes Y, or X cause Y, X causes a Y, X causes the Y
- X and Y *must* be included in the sentence.
- Sometimes you can't do this
- If X makes Y more likely or more probable, you can write that X causes Y
- Write the shortest sentence possible
- Also of the form: X increases Y, X decreases Y?
- What if there are multiple in a sentence?
- What about X affects y?