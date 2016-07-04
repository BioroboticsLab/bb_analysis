# Editor GUI

A gui for viewing and editing ground truth paths.

## Editing

### Shortcuts

* A, Left, Up: go to previous timestamp
* D, Right, Down: go to next timestamp
* R: remove detection on current timestamp (not possible in editing mode)
* E: enter editing mode
* Q: quit editing mode
* Escape: quit editing mode and discard detection on current timestamp
* 1,2,3: set readability value. ( 1 == completely, 2 == partially, 3 == none )

* With readability none it's not possible to select detections, only positions.

### Merging

Use the script merge.py to merge two path files.

