# bb_analysis system 2

This program depends on our custom [Cap'n Proto binary format](https://github.com/BioroboticsLab/bb_binary) for input.

It further uses a [custom Python pickle file format](path-file-format.md) for the tracking output and the ground truth paths.

## Usage

1. Data

	* Get pipeline output in the [Cap'n Proto binary format](https://github.com/BioroboticsLab/bb_binary).
	* Get video file and convert to image sequence.
		```
		ffmpeg -c:v hevc -r 3 -i video.mkv -f image2 %03d.jpg
		```

2. Preparation

	1. Use the [editor gui](./editor-gui) to track some ground truth data manually.
	2. [Generate a dataset](./learning-data-generator) for machine learning from the ground truth.
		- *copy the dataset to /xgboost-learning*
	4. [Train the xgboost learning model](./xgboost-learning) with the dataset.
		- *copy the trained model to /straight-filtering*
	5. Calculate the [bit flip probability](./bit-flip-probability) from the ground truth data.
		- *copy the file bit-flip-probability.pkl to /straight-filtering*

	**or**

	* Get the xgb-model.bin and bit-flip-probability.pkl from someone who has already calculated them.
	  Copy the files to /straight-filtering.

3. Computation

	* [Run the filtering algorithm](./straight-filtering).

4. Evaluation

	* Use the [editor gui](./editor-gui) to visually inspect the filtering results.
	* [Evaluate](./evaluation) the filtering results against the ground truth.

## Utils

* [Calculate some statistics](./statistics) about the truth data.
* [Render a video](./video-renderer)

