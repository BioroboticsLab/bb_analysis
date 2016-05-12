# Evaluation

## Global

Evaluates the result of the complete tracking algorithm.

Calculates four evaluation criteria:

* Equality
* Long Path Equality
* Pairs Continuity
* Path Congruence

## Average ID

Builds up paths from ground truth data
and tries different algorithms to calculate the correct id for the path
by averaging over the candidate ids of the detections.

Needs the files [bit-flip-probability.pkl](../bit-flip-probability) and distribution_binary_lut_fixed_12bits.pkl.

