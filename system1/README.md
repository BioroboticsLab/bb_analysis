# bb_analysis system 1

From the ongoing bb_analysis project the first release of a minimal productive system.

This program depends on our PostgreSQL database schema for the pipeline output.
Since we already have plans to migrate to a revised database there is likely to be a `system2` released.

## Usage

1. Data

	* Make sure you have access to the database.
	  The database has to conform to our [old schema described below](#database).
	* [Rename images](./image-renaming).

2. Preparation

	1. Use our [editor gui](./editor-gui) to track some ground truth data manually.
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

	* [Run the simple filtering algorithm](./straight-filtering).
	* [A graph filtering algorithm is in the works](./graph-filtering).

4. Evaluation

	* [Use the gui](./editor-gui) to visually inspect the filtering results.
	* [Evaluate](./evaluation) the filtering results against the ground truth.

## Utils

* Remove double detections from database. *TODO*
* Export results to CSV. *TODO*
* [Calculate some statistics](./statistics) about the truth data.

## Database

Has two tables for every minute of data.

column | type | comment
-------|------|--------
id | bigint |
timestamp | timestamp without time zone |
camID | smallint |
x | smallint |
y | smallint |
orientation | smallint | unused
updatedID | smallint |
isDancing | boolean | unused
isFollowing | boolean | unused
followedBeeID | smallint | unused
truthID | smallint | automatically added to the table
pathID | smallint | automatically added to the table

column | type
-------|-----
id | bigint
candidateid | smallint
x | smallint
y | smallint
xrotation | real
yrotation | real
zrotation | real
score | smallint
beeID | smallint

