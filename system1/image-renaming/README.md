# Image Renaming

The filename of images from the recent beesbook setup has 6 digits for milliseconds,
while in csv and database there are only 3 digits.
So the last 3 digits have to be deleted from the image name
to be able to derive the exact filename for a given frame from the database.

The filename of images from the old setup has a single digit frame number instead of milliseconds.
From the database it's not possible to know wether a single digit was meant or the last two digits were zero.
So the image names are padded with two zeros to get a uniforn naming scheme.

