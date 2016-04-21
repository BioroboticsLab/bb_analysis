# Renaming of beesbook images.
# The filename of images from the recent setup has 6 digits for milliseconds, while in csv and
# database there are only 3 digits. So the last 3 digits have to be deleted from the image name to
# be able to derive the exact filename for a given frame from the database.
# The filename of images from the old setup has a single digit frame number instead of milliseconds.
# From the database it's not possible to know wether a single digit was meant or the last two digits
# were zero. So the image names are padded with two zeros to get an uniforn naming scheme.

import os
import re

pattern_1 = re.compile( '^Cam\_[0-3]\_[0-9]{14}\_[0-9]{6}\.jpeg$' )
pattern_2 = re.compile( '^Cam\_[0-3]\_[0-9]{14}\_[0-9]{1}\.jpeg$' )

file_names = os.listdir( '.' )

for file_name in file_names:
	if pattern_1.match( file_name ):
		os.rename( file_name, file_name[:-8] + '.jpeg' )
	elif pattern_2.match( file_name ):
		os.rename( file_name, file_name[:-5] + '00.jpeg' )

