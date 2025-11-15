# main.py

import time
from trng import EntropyTRNG

def main():
    # 1. Inizializza il generatore.
    # Questo avvia automaticamente tutti i thread collettori.
    generator = EntropyTRNG()

    # 2. Dai tempo ai collettori di raccogliere entropia iniziale.
    print("\n--- Raccogliendo entropia per 5 secondi ---")
    print("Muovi il mouse e digita qualcosa!")
    time.sleep(5)
    print("--- Raccolta iniziale completata ---")

    # 3. Genera byte casuali
    print("\nGenerazione di 16 byte casuali (in esadecimale):")
    rand_bytes = generator.get_random_bytes(16)
    print(f"==> {rand_bytes.hex()}")
    
    time.sleep(0.5) # Pausa per nuova entropia
    
    print("\nGenerazione di altri 32 byte casuali (in esadecimale):")
    rand_bytes_2 = generator.get_random_bytes(32)
    print(f"==> {rand_bytes_2.hex()}")

    # 4. Genera interi casuali
    print(f"\nGenerazione di 5 interi casuali tra 1 e 100:")
    for i in range(5):
        print(f"Lancio {i+1}: {generator.get_random_int(1, 100)}")
        time.sleep(0.2) # Pausa per nuova entropia

    # 5. Genera float casuali
    print(f"\nGenerazione di 5 float casuali [0.0, 1.0):")
    for i in range(5):
        print(f"Float {i+1}: {generator.get_random_float():.10f}")
        time.sleep(0.2)

    # 6. Mantieni il programma attivo
    # I collettori sono 'daemon threads', quindi si chiuderebbero
    # se il programma principale terminasse.
    print("\n--- Generazione completata. I collettori sono ancora attivi. ---")
    print("Premi Ctrl+C per uscire.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nUscita richiesta. Arrivederci.")

if __name__ == "__main__":
    main()