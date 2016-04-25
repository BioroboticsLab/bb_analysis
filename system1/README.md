# bb_analysis system 1

From the ongoing bb_analysis project the first release of a minimal productive system.

## Database

Has two tables for every minute of data.

column | type
-------|-----
id | bigint
timestamp | timestamp without time zone
camID | smallint
x | smallint
y | smallint
orientation | smallint
updatedID | smallint
isDancing | boolean
isFollowing | boolean
followedBeeID | smallint
truthID | smallint
pathID | smallint

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

## Workflow

1. [Rename images](./image-renaming).
2. Use our gui to track some ground truth data manually. *(to be released)*
3. [Generate a dataset](./learning-data-generator) for machine learning from the ground truth.
   - *copy the dataset to /xgboost-learning*
4. [Train the xgboost learning model](./xgboost-learning) with the dataset.
   - *copy the trained model to /straight-filtering*
5. [Run the filtering algorithm](./straight-filtering).
6. Visually inspect the filtering results. *(to be released)*
7. Evaluate the filtering results against the ground truth. *(to be released)*

