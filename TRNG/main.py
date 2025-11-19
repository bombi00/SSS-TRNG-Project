import sys
import numpy as np
from trng import TRNG
from test_nist import NISTTestSuite

def run_experiment(seq_length, sources, filename):
    print(f"\n{'='*60}")
    print(f"AVVIO ESPERIMENTO: {filename}")
    print(f"Sorgenti: {sources} | Target Bit: {seq_length}")
    print(f"{'='*60}")

    # 1. Inizializzazione e Generazione
    trng = TRNG()
    
    # chunk_duration basso (0.1s) rende il loop più reattivo
    random_seq = trng.generate_sequence(seq_length, sources=sources, chunk_duration=0.1)
    
    print(f"\nGenerazione completata. Lunghezza sequenza: {len(random_seq)} bit")

    # 2. Salvataggio su file (utile per analisi future o comparison)
    trng.save_to_file(random_seq, filename)

    # 3. Esecuzione Test NIST
    print(f"\n--- Esecuzione Test Statistici NIST ---")
    nist = NISTTestSuite(random_seq)
    results = nist.run_all()

    # 4. Stampa Report
    print("\n" + "-"*45)
    print(f"RISULTATI TEST ({filename})")
    print("-" * 45)
    print(f"{'TEST':<20} | {'P-VALUE':<10} | {'ESITO':<10}")
    print("-" * 45)
    
    success_count = 0
    for name, res in results.items():
        status = "PASS" if res['Pass'] else "FAIL !!"
        if res['Pass']: success_count += 1
        print(f"{name:<20} | {res['P-Value']:<10} | {status:<10}")
    print("-" * 45)
    
    if success_count == len(results):
        print(">>> TUTTI I TEST SUPERATI CON SUCCESSO <<<")
    else:
        print(f">>> ATTENZIONE: {len(results) - success_count} TEST FALLITI <<<")

def main():
    # Configurazione della lunghezza della sequenza
    # Per test rapidi: 20000 bit. Per risultati statisticamente solidi: > 1.000.000 bit
    TARGET_BITS = 20000 

    print("Seleziona lo scenario di test:")
    print("1. IDLE (Solo System Noise - Nessuna interazione)")
    print("2. NON-IDLE (System + Mouse + Keyboard - Richiede interazione)")
    
    choice = input("\nScelta (1/2): ").strip()

    if choice == "1":
        # Scenario IDLE: Usa solo il rumore di sistema (interrupts, jitter temporale)
        # Ideale per vedere se la macchina genera entropia da sola.
        run_experiment(TARGET_BITS, sources=['system'], filename="trng_idle.txt")
        
    elif choice == "2":
        # Scenario NON-IDLE: Aggiunge input utente
        # Qui dovrai muovere il mouse e premere tasti durante la generazione.
        print("\n!!! ATTENZIONE: Muovi il mouse e premi tasti durante la raccolta !!!")
        run_experiment(TARGET_BITS, sources=['system', 'mouse', 'keyboard'], filename="trng_active.txt")
        
    else:
        print("Scelta non valida.")

if __name__ == "__main__":
    main()
