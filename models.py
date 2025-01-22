from dataclasses import dataclass
from enum import Enum
import random
import numpy as np

class AuthResult(Enum):
    SUCCESS = "SUCCESS"
    RELAY_DETECTED = "RELAY_DETECTED"
    TOO_FAR = "TOO_FAR"
    ERROR = "ERROR"

@dataclass
class Position:
    x: float
    y: float
    
    def distance_to(self, other: 'Position') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

class RelayAttack:
    def __init__(self, distance: float):
        """
        Simula un attacco relay
        distance: lunghezza del cavo/distanza del relay in metri
        """
        self.cable_length = distance
        self.propagation_speed = 2/3 * 3e8  # velocità nel cavo (2/3 della luce)
        
    def get_delay(self) -> float:
        """Calcola il ritardo introdotto dal relay"""
        cable_delay = (self.cable_length / self.propagation_speed)
        # Delay hardware più realistico e variabile
        equipment_delay = random.uniform(50e-9, 150e-9)  # 50-150ns
        # Aggiunge rumore ambientale
        noise = random.gauss(0, 10e-9)  # ±10ns di rumore
        return cable_delay + equipment_delay + noise

class Vehicle:
    def __init__(self, position: Position):
        self.position = position
        self.LIGHT_SPEED = 3e8
        self.MAX_DISTANCE = 2.0  # Aumentato a 2m per essere più realistico
        # Soglie più realistiche basate sul paper
        self.PROCESSING_TIME = 50e-9  # 50ns come citato nel paper
        self.VARIANCE_THRESHOLD = 20e-9  # Aumentato per considerare più rumore
        
    def measure_distance_bound(self, key_position: Position, relay_attack: RelayAttack = None) -> tuple[float, float, list[float]]:
        distance = self.position.distance_to(key_position)
        theoretical_time = (2 * distance / self.LIGHT_SPEED)
        
        measurements = []
        for _ in range(20):  # Aumentato il numero di misurazioni
            processing_time = self.PROCESSING_TIME + random.gauss(0, 62e-12)
            
            if relay_attack:
                relay_delay = relay_attack.get_delay()
                round_trip = theoretical_time + processing_time + relay_delay
            else:
                round_trip = theoretical_time + processing_time
                
            measurements.append(round_trip * 1e9)  # Converti in ns
            
        return np.mean(measurements), np.std(measurements), measurements

class Key:
    def __init__(self, position: Position):
        self.position = position
        self.processing_time = 1e-9 