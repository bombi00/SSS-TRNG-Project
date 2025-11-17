import numpy as np        
from trng import EntropyTRNG    
import time
from nistrng.functions import run_all_battery
from nistrng.functions import SP800_22R1A_BATTERY

BYTES_DA_TESTARE = 1 * 1024 * 1024  # 1 MB
LIVELLO_SIGNIFICATIVITA = 0.01   # Standard NIST

generator = EntropyTRNG()

print("Avvio generatore. Attendi 5s per la raccolta di entropia...")
print("Muovi il mouse e digita!")
time.sleep(5)
print("Inizio generazione dati in memoria...")

random_bytes = generator.get_random_bytes(BYTES_DA_TESTARE)

binary_sequence = np.unpackbits(np.frombuffer(random_bytes, dtype=np.uint8)).astype(np.int32)

print(f"Generati {len(binary_sequence)} bit per il test.")

try:
    print("--- Inizio dei Test ---")
    results_list = run_all_battery(binary_sequence, SP800_22R1A_BATTERY)

    print("--- Test completati ---")

    for result, elapsed_time in results_list:
        test_name = result.name
        # Usiamo 'score' che è la media dei P-value del test
        p_value_avg = result.score

        # Controlliamo il risultato del test
        success = p_value_avg >= LIVELLO_SIGNIFICATIVITA

        # Stampiamo l'output
        print(f"- {test_name}: \t P-Value Medio: {p_value_avg:.6f} \t {'PASS' if success else 'FAIL'} (Tempo: {elapsed_time/1000:.2f}s)")

except Exception as e:
    print(f"\nERRORE DURANTE L'ESECUZIONE DEI TEST:")
    print(f"Tipo di errore: {type(e).__name__}")
    print(f"Messaggio: {e}")
    print("Potrebbe essere necessario un campione di dati ancora più grande.")