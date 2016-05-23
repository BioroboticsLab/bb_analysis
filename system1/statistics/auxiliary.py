def hamming_distance( a, b, bits=12 ):

	xor = (a ^ b) & ((1 << bits) - 1)
	count = 0
	while xor:
		count += xor & 1
		xor >>= 1
	return count


