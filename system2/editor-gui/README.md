# Editor GUI

A gui for viewing and editing ground truth paths.

## Editing

### Shortcuts

* A, Left, Up: go to previous timestamp
* D, Right, Down: go to next timestamp
* P: add new path
* R: remove detection on current timestamp (not possible in editing mode)
* E: enter editing mode
* Q: quit editing mode
* Escape: quit editing mode and discard detection on current timestamp, same as Q+R
* C: correct the current detection and leave editing mode immediately, same as E+Q
* 1,2,3: set readability value. ( 1 == completely, 2 == partially, 3 == none )

* With readability none it's not possible to select detections, only positions.

### Merging

Use the script merge.py to merge two path files.

### Paths File

Paths are saved in a Python pickle file.

```python
{
	'source': 'filename_of_video.mkv',
	'paths': {
		tag_id: {                  # int
			path_id: {             # int
				frame_number: (    # int
					detection_id,  # int
					position_x,    # int
					position_y,    # int
					readability    # int
				)
			}
		}
	}
}
```

The readability value should be interpreted as follows:

```python
class Readability:
	Unknown    = 0
	Completely = 1
	Partially  = 2
	Not_At_All = 3
```


