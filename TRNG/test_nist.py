import numpy as np
from nistrng import run_all_battery, SP800_22R1A_BATTERY

class NISTTestSuite:
    def __init__(self, bit_sequence):
        self.bits = np.array(bit_sequence, dtype=int)
        self.alpha = 0.01

    def run_all(self):
        formatted_results = {}
        
        if len(self.bits) < 1000:
            print(f"ATTENZIONE: Sequenza molto breve ({len(self.bits)} bit). Molti test NIST verranno saltati.")

        try:
            results_list = run_all_battery(self.bits, SP800_22R1A_BATTERY)
            
            for item in results_list:
                if item is None:
                    continue
                
                try:
                    result, elapsed_time = item
                except TypeError:
                    continue

                if result is None or not hasattr(result, 'name') or not hasattr(result, 'score'):
                    continue

                test_name = result.name
                p_value = result.score
                passed = p_value >= self.alpha
                
                formatted_results[test_name] = {
                    'P-Value': round(p_value, 6),
                    'Pass': passed
                }
                
            return formatted_results

        except Exception as e:
            print(f"\nERRORE CRITICO nistrng durante l'esecuzione: {e}")
            return {"Suite Error": {'P-Value': 0.0, 'Pass': False}}
