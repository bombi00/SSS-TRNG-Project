import time
from trng import EntropyTRNG

TOTAL_MEGABYTES = 100
FILE_NAME = "random_data.bin"

CHUNK_SIZE = 1024 * 1024
TOTAL_SIZE = TOTAL_MEGABYTES * 1024 * 1024
chunks_needed = TOTAL_MEGABYTES


generator = EntropyTRNG()
time.sleep(5)

try:
    with open(FILE_NAME, "wb") as f:
        for i in range(chunks_needed):
            # 1. Raccogli nuova entropia e genera 1MB di dati
            data_chunk = generator.get_random_bytes(CHUNK_SIZE)
            
            # 2. Scrivi il blocco sul file
            f.write(data_chunk)
            
            print(f"Generato {i+1}/{chunks_needed} MB... (Continua a muovere il mouse!)")


except KeyboardInterrupt:
    print("\nGenerazione interrotta dall'utente.")