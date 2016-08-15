# determine whether to close a path or not
def hard_closing( path ):

	pending_count = 0
	PENDING_THRESHOLD = 16

	for d in reversed( path.get_sorted_detections() ):
		if d.is_empty():
			pending_count += 1
			if pending_count >= PENDING_THRESHOLD:
				return True
		else:
			return False

	return False


