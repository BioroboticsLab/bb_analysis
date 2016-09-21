# Evaluation

## Average ID

Builds up paths from ground truth data
and tries different algorithms to calculate the correct id for the path
by averaging over the candidate ids of the detections.

Uses 100 iterations to sample truth path subsets of size 20 by default.

### Input

* Adjusted config.py
* [Pipeline data](https://github.com/BioroboticsLab/bb_binary)
* [Ground Truth Path file](../path-file-format.md)
* [bit-flip-probability.pkl](../bit-flip-probability)

## Global

Compares the tracking result with the ground truth data.

Calculates 4 values:
* Congruence:
What percentage of the ground truth paths were found.
Whether the correct Bee ID was identified is thereby irrelevant.
If the path was not found completely the largest connected part counts.
* Excesss:
What percentage of the tracked paths was not part of the ground truth path.
This measures detections assigned by mistake to a path.
* Jumps:
How often the path loses a pursued bee and continues to follow another.
The value is a percentage in relation to all connections between detections.
* Identification:
For how many of the detections the correct Bee ID was identified at the end.
If a path is tracked correctly but the right ID could not be determined each of the detections is counted as an error.

### Input

* Adjusted config.py
* [Pipeline data](https://github.com/BioroboticsLab/bb_binary)
* [Tracked Path file](../path-file-format.md)
* [Ground Truth Path file](../path-file-format.md)

