import numpy as np
import collectors
from pool import EntropyPool

class TRNG:
    def __init__(self):
        self.pool = EntropyPool()

    def _collect_chunk(self, sources, duration):
        if 'mouse' in sources:
            bits = collectors.collectMouseEntropy(plot_mouse=False, plot_bit=False, seconds=duration)
            self.pool.add_source(bits)
        
        if 'keyboard' in sources:
            bits = collectors.collectKeyboardEntropy(plot_bit=False, seconds=duration)
            self.pool.add_source(bits)
            
        if 'system' in sources:
            bits = collectors.collectSystemEntropy(plot_bit=False, seconds=duration)
            self.pool.add_source(bits)

    def generate_sequence(self, length_bits, sources=['system'], chunk_duration=1):
        final_sequence = np.array([], dtype=int)
        
        print(f"Generazione di {length_bits} bit avviata. Sorgenti: {sources}")
        
        while len(final_sequence) < length_bits:
            self._collect_chunk(sources, chunk_duration)
            new_bits = self.pool.get_final_sequence(method='hash')      
            final_sequence = np.concatenate((final_sequence, new_bits))
            
            self.pool = EntropyPool() 
            
            print(f"Progress: {len(final_sequence)}/{length_bits} bits")
            
        print(f"Collected :{length_bits} bits")
        return final_sequence[:length_bits]

    def save_to_file(self, sequence, filename="random_sequence.txt"):
        bin_str = "".join(sequence.astype(str))
        with open(filename, "w") as f:
            f.write(bin_str)
        print(f"Salvato in {filename}")