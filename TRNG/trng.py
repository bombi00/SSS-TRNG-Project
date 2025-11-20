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

    def _collect_chunk_parallel(self, sources, samples_target):
        """
        Chiede a ogni sorgente di raccogliere 'samples_target' campioni grezzi.
        """
        futures = {}
        for src in sources:
            if src in self.collectors_map:
                collector = self.collectors_map[src]
                
                # Adattamento dei target per sorgente
                # Il sistema è veloce, chiediamo tanti campioni (es. 5000)
                # Tastiera/Mouse sono lenti, se chiediamo 5000 campioni l'utente muore!
                # Riduciamo il target per le sorgenti umane.
                
                actual_target = samples_target
                if src == 'keyboard':
                    actual_target = min(10, samples_target) # Bastano pochi tasti per molta entropia
                elif src == 'mouse':
                    actual_target = min(500, samples_target) # Il mouse genera eventi veloci, 500 è ok

                futures[self.executor.submit(collector.collect, actual_target)] = src

        for future in as_completed(futures):
            try:
                bits = future.result()
                if len(bits) > 0:
                    self.pool.add_source(bits)
            except Exception as e:
                print(f"Err {futures[future]}: {e}")

    def generate_sequence(self, length_bits, sources=['system']):
        final_sequence = np.array([], dtype=int)
        
        # Definiamo quanti campioni grezzi raccogliere per ogni ciclo
        # 4096 campioni grezzi -> compressi in 256 bit (Hash) = Rapporto 16:1 (Ottimo)
        RAW_SAMPLES_PER_CHUNK = 4096 

        print(f"Generazione TRNG (Count-Based). Target: {length_bits} bit.")
        
        try:
            self.start_collectors(sources)
            start_time = time.time()
            
            while len(final_sequence) < length_bits:
                # La funzione ora BLOCCA finché non ha i dati
                self._collect_chunk_parallel(sources, RAW_SAMPLES_PER_CHUNK)
                
                if len(self.pool.raw_bits) == 0:
                    continue

                new_bits = self.pool.get_final_sequence()
                final_sequence = np.concatenate((final_sequence, new_bits))
                
                self.pool = EntropyPool()
                
                elapsed = time.time() - start_time
                rate = len(final_sequence) / elapsed if elapsed > 0 else 0
                print(f"\rProgress: {len(final_sequence)}/{length_bits} | Speed: {rate:.0f} bit/s", end="", flush=True)

        except KeyboardInterrupt:
            print("\nStop utente.")
        finally:
            self.stop_collectors()

        return final_sequence[:length_bits]
    
    # ... (save_to_file rimane uguale)
    
    def save_to_file(self, sequence, filename="random_sequence.txt"):
        bin_str = "".join(sequence.astype(str))
        with open(filename, "w") as f:
            f.write(bin_str)
        print(f"\nSalvato in {filename} ({len(sequence)} bit)")