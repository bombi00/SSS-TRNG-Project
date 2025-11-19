import math
import numpy as np

class NISTTestSuite:
    def __init__(self, bit_sequence):
        # Assicurarsi che l'input sia un array numpy di 0 e 1
        self.bits = np.array(bit_sequence, dtype=int)
        self.n = len(bit_sequence)

    def _erfc(self, x):
        # Complementary error function (disponibile in math da Python 3.2)
        return math.erfc(x)

    def monobit_test(self):
        # Test 1: Frequency (Monobit) Test
        # Verifica se il numero di 0 e 1 è approssimativamente uguale
        # Converti 0 -> -1 e 1 -> +1
        signed_bits = np.where(self.bits == 0, -1, 1)
        s_obs = np.abs(np.sum(signed_bits)) / math.sqrt(self.n)
        p_value = self._erfc(s_obs / math.sqrt(2))
        return p_value, p_value >= 0.01

    def block_frequency_test(self, block_size=128):
        # Test 2: Frequency Test within a Block
        # Verifica la proporzione di 1 all'interno di blocchi di M bit
        if self.n < block_size:
            return 0.0, False 
        
        num_blocks = self.n // block_size
        # Taglia i bit in eccesso
        truncated_bits = self.bits[:num_blocks * block_size]
        blocks = truncated_bits.reshape((num_blocks, block_size))
        
        proportions = np.sum(blocks, axis=1) / block_size
        chi_squared = 4 * block_size * np.sum((proportions - 0.5) ** 2)
        
        p_value = self.gammaincc(num_blocks / 2, chi_squared / 2)
        return p_value, p_value >= 0.01

    def runs_test(self):
        # Test 3: Runs Test
        # Verifica se il numero di sequenze consecutive (runs) di 0 o 1 è anomalo
        prop_ones = np.sum(self.bits) / self.n
        
        # Precondizione del test
        if abs(prop_ones - 0.5) >= (2 / math.sqrt(self.n)):
            return 0.0, False # Fallisce se c'è troppo bias iniziale

        v_obs = 1 + np.sum(self.bits[:-1] != self.bits[1:])
        numerator = abs(v_obs - 2 * self.n * prop_ones * (1 - prop_ones))
        denominator = 2 * math.sqrt(2 * self.n) * prop_ones * (1 - prop_ones)
        
        p_value = self._erfc(numerator / denominator)
        return p_value, p_value >= 0.01

    def gammaincc(self, a, x):
        # Upper incomplete gamma function (necessaria per Block Frequency)
        # Utilizziamo scipy se disponibile, altrimenti una approx o math.gamma (se completa)
        # Per semplicità in standard library, usiamo un'approssimazione o richiediamo scipy.
        try:
            import scipy.special
            return scipy.special.gammaincc(a, x)
        except ImportError:
            print("Warning: Scipy not found, skipping Block Frequency precise calc.")
            return 0.0

    def run_all(self):
        results = {}
        
        p1, res1 = self.monobit_test()
        results['Monobit'] = {'P-Value': round(p1, 6), 'Pass': res1}
        
        p2, res2 = self.block_frequency_test()
        results['Block Freq'] = {'P-Value': round(p2, 6), 'Pass': res2}
        
        p3, res3 = self.runs_test()
        results['Runs'] = {'P-Value': round(p3, 6), 'Pass': res3}
        
        return results