import hashlib
import numpy as np

class EntropyPool:
    def __init__(self):
        self.raw_bits = np.array([])

    def add_source(self, bit_array):
        self.raw_bits = np.concatenate((self.raw_bits, bit_array))

    #def _von_neumann_extractor(self, bits):
    #    output = []
    #    for i in range(0, len(bits) - 1, 2):
    #        if bits[i] == 0 and bits[i+1] == 1:
    #            output.append(0)
    #        elif bits[i] == 1 and bits[i+1] == 0:
    #            output.append(1)
    #    return np.array(output)

    def get_hashed_bytes(self):
        bit_string = "".join(self.raw_bits.astype(int).astype(str))
        data_bytes = bit_string.encode('utf-8')
        sha256 = hashlib.sha256()
        sha256.update(data_bytes)
        return sha256.digest()

    def get_final_sequence(self):
        digest = self.get_hashed_bytes()
        binary_string = "".join(f"{byte:08b}" for byte in digest)
        return np.array([int(b) for b in binary_string])