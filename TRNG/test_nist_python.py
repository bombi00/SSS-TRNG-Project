import numpy as np
from trng import EntropyTRNG
import time
from nistrng.functions import run_all_battery
from nistrng.functions import SP800_22R1A_BATTERY

BYTES_DA_TESTARE = 1 * 1024 * 1024  # 10 MB
LIVELLO_SIGNIFICATIVITA = 0.01

# 1. Crea il generatore. I collettori partono automaticamente.
generator = EntropyTRNG()

print("Avvio generatore. Attendi 10s per la raccolta di entropia...")
print("Muovi il mouse e digita!")
# 2. Aspetta 10 secondi per lasciare che i thread daemon raccolgano entropia
time.sleep(10) 
print("Inizio generazione dati in memoria...")


print(f"\nInizio generazione di {BYTES_DA_TESTARE / (1024*1024):.0f} MB di dati...")
random_bytes = generator.get_random_bytes(BYTES_DA_TESTARE)
print("Generazione completata.")

binary_sequence = np.unpackbits(np.frombuffer(random_bytes, dtype=np.uint8)).astype(np.int32)
print(f"Generati {len(binary_sequence)} bit per il test.")

try:
    print("--- Inizio dei Test ---")
    results_list = run_all_battery(binary_sequence, SP800_22R1A_BATTERY)
    print("--- Test completati ---")

    print("\n--- RISULTATI ---")
    fail_count = 0
    for result, elapsed_time in results_list:
        test_name = result.name
        p_value_avg = result.score
        
        success = p_value_avg >= LIVELLO_SIGNIFICATIVITA
        status = "PASS" if success else "FAIL"
        if not success:
            fail_count += 1
            
        print(f"- {test_name:<30} P-Value Medio: {p_value_avg:.6f} \t {status} (Tempo: {elapsed_time/1000:.2f}s)")
    
    print("\n--- RIEPILOGO ---")
    print(f"Test superati: {len(results_list) - fail_count}/{len(results_list)}")
    if fail_count > 0:
        print(f"ATTENZIONE: {fail_count} TEST FALLITI.")
    else:
        print("OTTIMO: Tutti i test sono stati superati.")

except Exception as e:
    print(f"\nERRORE DURANTE L'ESECUZIONE DEI TEST:")
    print(f"Tipo di errore: {type(e).__name__}")
    print(f"Messaggio: {e}")
    print("Potrebbe essere necessario un campione di dati ancora più grande.")