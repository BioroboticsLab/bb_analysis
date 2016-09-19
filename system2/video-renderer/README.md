# Video Renderer

The video renderer generates a colored animation of bee paths.

This gui outputs an image sequence into the subfolder /image.
Convert to video with the following command:
	```
	ffmpeg -framerate 6 -i %03d.png -c:v libx264 -r 6 -pix_fmt yuv420p out.mp4
	```

