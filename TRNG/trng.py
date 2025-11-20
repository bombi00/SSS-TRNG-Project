import numpy as np
import time
from pool import EntropyPool
from concurrent.futures import ThreadPoolExecutor, as_completed
from collectors import MouseEntropyCollector, KeyboardEntropyCollector, SystemEntropyCollector

class TRNG:
    def __init__(self):
        self.pool = EntropyPool()
        self.collectors_map = {
            'mouse': MouseEntropyCollector(),
            'keyboard': KeyboardEntropyCollector(),
            'system': SystemEntropyCollector()
        }
        self.executor = None

    def start_collectors(self, sources):
        for src in sources:
            if src in self.collectors_map:
                self.collectors_map[src].start()

        self.executor = ThreadPoolExecutor(max_workers=len(sources))

    def stop_collectors(self):
        for collector in self.collectors_map.values():
            collector.stop()

        if self.executor:
            self.executor.shutdown(wait=False)

    def _collect_chunk_parallel(self, sources, duration):
        futures = {}
        
        for src in sources:
            if src in self.collectors_map:
                collector = self.collectors_map[src]
                futures[self.executor.submit(collector.collect, duration)] = src

        for future in as_completed(futures):
            try:
                bits = future.result()
                if len(bits) > 0:
                    self.pool.add_source(bits)
            except Exception as e:
                print(f"Err {futures[future]}: {e}")

    def generate_sequence(self, length_bits, sources=['system'], chunk_duration=0.2):
        final_sequence = np.array([], dtype=int)
        
        print(f"Avvio Generatore TRNG. Target: {length_bits} bit.")
        print(f"Sorgenti attive: {sources}")
        
        try:
            # 1. Setup una tantum (evita l'incartamento del sistema)
            self.start_collectors(sources)
            
            start_time = time.time()
            
            while len(final_sequence) < length_bits:
                # 2. Raccolta Parallela
                self._collect_chunk_parallel(sources, chunk_duration)
                
                if len(self.pool.raw_bits) == 0:
                    continue

                # 3. Estrazione (Hashing)
                new_bits = self.pool.get_final_sequence()
                final_sequence = np.concatenate((final_sequence, new_bits))
                
                # Reset pool e stampa
                self.pool = EntropyPool()
                elapsed = time.time() - start_time
                rate = len(final_sequence) / elapsed if elapsed > 0 else 0
                
                print(f"\rProgress: {len(final_sequence)}/{length_bits} bits | Velocità: {rate:.0f} bit/s", end="", flush=True)

        except KeyboardInterrupt:
            print("\nInterrotto dall'utente.")
        finally:
            # 4. Pulizia risorse garantita
            self.stop_collectors()
            print("\nRisorse rilasciate.")

        return final_sequence[:length_bits]

    def save_to_file(self, sequence, filename="random_sequence.txt"):
        bin_str = "".join(sequence.astype(str))
        with open(filename, "w") as f:
            f.write(bin_str)
        print(f"Salvato in {filename} ({len(sequence)} bit)")