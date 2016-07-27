# bb_analysis system 2

This program depends on our custom [Cap'n Proto binary format](https://github.com/BioroboticsLab/bb_binary).

## Usage

1. Data

	* Get pipeline output in the [Cap'n Proto binary format](https://github.com/BioroboticsLab/bb_binary).
	* Get video file and covert to image sequence.
		```
		ffmpeg -i video.mkv $filename%03d.jpg
		```

2. Preparation

	1. Use the [editor gui](./editor-gui) to track some ground truth data manually.
	2. Generate a dataset for machine learning from the ground truth. *TODO*
		- *copy the dataset to /xgboost-learning*
	4. Train the xgboost learning model with the dataset. *TODO*
		- *copy the trained model to /straight-filtering*
	5. Calculate the [bit flip probability](./bit-flip-probability) from the ground truth data.
		- *copy the file bit-flip-probability.pkl to /straight-filtering*

	**or**

	* Get the xgb-model.bin and bit-flip-probability.pkl from someone who has already calculated them.
	  Copy the files to /straight-filtering.

3. Computation

	* [Run the simple filtering algorithm](./straight-filtering).

4. Evaluation

	* Use the [editor gui](./editor-gui) to visually inspect the filtering results.
	* [Evaluate](./evaluation) the filtering results against the ground truth.

