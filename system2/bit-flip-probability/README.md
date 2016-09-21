# Bit Flip Probability

Calculates a matrix of bit flip probabilities.

The matrix is calculated from clicked ground truth data (see [editor gui](../editor-gui)).
For every bit of the tag (12), for every combination with its two neighbors (8),
the ground truth result for the bit is summed and averaged.
The result is a 12 x 8 matrix where every row is a bit and every column a neighborhood pattern.

Read it this way: for a specific bit position, if the decoder outputted this specific neighborhood pattern,
the value in the matrix is the likelihood this bit was really 1.
Using this information for the average id calculation we simply add the likelihood to the sum instead
of the bit value the decoder gave us.

Will output the file bit-flip-probability.pkl.

Use plot.py to plot the matrix for visual comparisons.

## Input

* Adjusted config.py
* [Pipeline data](https://github.com/BioroboticsLab/bb_binary)
* [Ground Truth Path file](../path-file-format.md)

