import numpy as np
import matplotlib.pyplot as plt
from models import Vehicle, Key, Position, RelayAttack, AuthResult
from authentication import AuthenticationSystem
import random

class PKESSimulator:
    def __init__(self):
        self.results = []
        
    def run_scenario(self, key_distance: float, relay_distance: float = None) -> dict:
        vehicle = Vehicle(Position(0, 0))
        key = Key(Position(key_distance, 0))
        auth_system = AuthenticationSystem(vehicle, key)
        
        relay = RelayAttack(relay_distance) if relay_distance else None
        result, debug = auth_system.authenticate(relay)
        
        return {
            "key_distance": key_distance,
            "relay_distance": relay_distance,
            "result": result,
            "debug": debug
        }
        
    def run_simulation(self, iterations: int = 100):
        # Test scenari normali
        key_distances = np.linspace(0.1, 5, 10)
        for dist in key_distances:
            for _ in range(iterations):
                self.results.append(self.run_scenario(dist))
        
        # Test scenari di attacco
        attack_scenarios = [
            (5, 10), (10, 20), (15, 30), (20, 40), (25, 50)
        ]
        
        for key_dist, relay_dist in attack_scenarios:
            for _ in range(iterations):
                self.results.append(self.run_scenario(key_dist, relay_dist))
    
    def plot_results(self):
        plt.figure(figsize=(15, 10))
        
        # 1. Grafico successo autenticazione per distanza chiave
        plt.subplot(2, 2, 1)
        distances = sorted(set(r["key_distance"] for r in self.results if r["relay_distance"] is None))
        success_rates = []
        
        for d in distances:
            attempts = [r for r in self.results if r["key_distance"] == d and r["relay_distance"] is None]
            if attempts:
                success_rate = sum(1 for r in attempts if r["result"] == AuthResult.SUCCESS) / len(attempts) * 100
                success_rates.append(success_rate)
            
        plt.plot(distances, success_rates, 'b-', marker='o')
        plt.title('Autenticazione Normale vs Distanza')
        plt.xlabel('Distanza Chiave (m)')
        plt.ylabel('Successo (%)')
        plt.grid(True)
        
        # 2. Grafico rilevamento attacchi
        plt.subplot(2, 2, 2)
        attack_distances = sorted(set(r["relay_distance"] for r in self.results if r["relay_distance"] is not None))
        detection_rates = []
        
        for d in attack_distances:
            attacks = [r for r in self.results if r["relay_distance"] == d]
            if attacks:
                detection_rate = sum(1 for r in attacks if r["result"] == AuthResult.RELAY_DETECTED) / len(attacks) * 100
                detection_rates.append(detection_rate)
            
        plt.plot(attack_distances, detection_rates, 'r-', marker='o')
        plt.title('Rilevamento Attacchi Relay')
        plt.xlabel('Distanza Relay (m)')
        plt.ylabel('Rilevamento (%)')
        plt.grid(True)
        
        # 3. Grafico tempi di risposta
        plt.subplot(2, 2, 3)
        normal_times = [r["debug"].get("round_trip_time", 0) for r in self.results 
                       if r["relay_distance"] is None and "round_trip_time" in r["debug"]]
        attack_times = [r["debug"].get("round_trip_time", 0) for r in self.results 
                       if r["relay_distance"] is not None and "round_trip_time" in r["debug"]]
        
        plt.hist([normal_times, attack_times], label=['Normale', 'Attacco'], bins=30, alpha=0.7)
        plt.title('Distribuzione Tempi di Risposta')
        plt.xlabel('Tempo (ns)')
        plt.ylabel('Frequenza')
        plt.legend()
        plt.grid(True)
        
        # 4. Grafico motivi di fallimento
        plt.subplot(2, 2, 4)
        reasons = {}
        for r in self.results:
            if r["result"] != AuthResult.SUCCESS and "reason" in r["debug"]:
                reason = r["debug"]["reason"]
                reasons[reason] = reasons.get(reason, 0) + 1
                
        if reasons:
            plt.pie(reasons.values(), labels=reasons.keys(), autopct='%1.1f%%')
            plt.title('Motivi di Rilevamento Attacco')
        
        plt.tight_layout()
        plt.savefig('pkes_results.png')
        print("\nGrafici salvati in 'pkes_results.png'")
        plt.close()

    def print_results(self):
        total = len(self.results)
        attacks = sum(1 for r in self.results if r["relay_distance"] is not None)
        detected = sum(1 for r in self.results if r["relay_distance"] is not None 
                      and r["result"] == AuthResult.RELAY_DETECTED)
        
        print(f"\n=== Risultati Simulazione ===")
        print(f"Totale scenari: {total}")
        print(f"Attacchi tentati: {attacks}")
        print(f"Attacchi rilevati: {detected}")
        print(f"Efficacia rilevamento: {(detected/attacks)*100:.2f}%")
        
        # Analisi per distanza
        for key_dist in sorted(set(r["key_distance"] for r in self.results)):
            attacks_at_dist = [r for r in self.results if r["key_distance"] == key_dist 
                             and r["relay_distance"] is not None]
            if attacks_at_dist:
                detected_at_dist = sum(1 for r in attacks_at_dist 
                                     if r["result"] == AuthResult.RELAY_DETECTED)
                print(f"\nDistanza chiave: {key_dist:.1f}m")
                print(f"Attacchi rilevati: {detected_at_dist}/{len(attacks_at_dist)}")
                print(f"Efficacia: {(detected_at_dist/len(attacks_at_dist))*100:.2f}%")

def main():
    sim = PKESSimulator()
    print("Avvio simulazione...")
    sim.run_simulation(iterations=100)
    
    print("\nGenerazione grafici...")
    sim.plot_results()
    
    print("\nAnalisi risultati:")
    sim.print_results()

if __name__ == "__main__":
    main() 