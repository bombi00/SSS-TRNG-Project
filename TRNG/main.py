from trng import TRNG
from test import NISTTestSuite

def run_experiment(seq_length, sources, filename):
    print(f"\n{'='*60}")
    print(f"AVVIO ESPERIMENTO: {filename}")
    print(f"Sorgenti: {sources} | Target Bit: {seq_length}")
    print(f"{'='*60}")

    trng = TRNG()
    random_seq = trng.generate_sequence(seq_length, sources=sources, chunk_duration=0.1)
    
    print(f"\nGenerazione completata. Lunghezza sequenza: {len(random_seq)} bit")
    trng.save_to_file(random_seq, filename)

    print(f"\n--- Esecuzione Test Statistici NIST ---")
    nist = NISTTestSuite(random_seq)
    results = nist.run_all()
    
    print("-" * 63)
    print(f"|{'TEST':<40} | {'P-VALUE':<10} | {'ESITO':<6}|")
    print("-" * 63)
    
    success_count = 0
    for name, res in results.items():
        status = "PASS" if res['Pass'] else "FAIL"
        if res['Pass']: success_count += 1
        print(f"|{name:<40} | {res['P-Value']:<10} | {status:<6}|")
    print("-" * 63)
    
    if success_count == len(results):
        print(">>> TUTTI I TEST SUPERATI CON SUCCESSO <<<")
    else:
        print(f">>> ATTENZIONE: {len(results) - success_count} TEST FALLITI <<<")

def main():
    TARGET_BITS = 10000

    print("Select the test:")
    print("1. IDLE")
    print("2. NON-IDLE (System + Mouse + Keyboard - Richiede interazione)")
    
    choice = input("\nScelta (1/2): ").strip()

    if choice == "1":
        run_experiment(TARGET_BITS, sources=['system'], filename="trng_idle.txt")
        
    elif choice == "2":
        print("\n!!! ATTENZIONE: Muovi il mouse e premi tasti durante la raccolta !!!")
        run_experiment(TARGET_BITS, sources=['system', 'mouse', 'keyboard'], filename="trng_active.txt")
        
    else:
        print("Scelta non valida.")

if __name__ == "__main__":
    main()
