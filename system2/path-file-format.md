# Path File Format

The exchange format for ground truth paths and the tracking results is a Python pickle file.

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

