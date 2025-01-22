from models import Vehicle, Key, AuthResult, Position, RelayAttack
import random

class AuthenticationSystem:
    def __init__(self, vehicle: Vehicle, key: Key):
        self.vehicle = vehicle
        self.key = key
        self.debug_info = {}
        
    def authenticate(self, relay_attack: RelayAttack = None) -> tuple[AuthResult, dict]:
        distance = self.vehicle.position.distance_to(self.key.position)
        
        # Raccogli informazioni per debug
        self.debug_info = {
            "real_distance": distance,
            "attack_present": relay_attack is not None
        }
        
        # Verifica distanza più permissiva
        if distance > self.vehicle.MAX_DISTANCE and relay_attack is None:
            self.debug_info["reason"] = "Chiave troppo lontana"
            return AuthResult.TOO_FAR, self.debug_info
            
        round_trip_time, variance, measurements = self.vehicle.measure_distance_bound(
            self.key.position, relay_attack)
            
        self.debug_info.update({
            "round_trip_time": round_trip_time,
            "variance": variance,
            "measurements": measurements,
            "estimated_distance": (round_trip_time * 3e8) / (2 * 1e9)
        })
        
        # Soglie più realistiche per il rilevamento
        if variance > self.vehicle.VARIANCE_THRESHOLD:
            if random.random() < 0.9:  # 90% di probabilità di rilevamento
                self.debug_info["reason"] = "Varianza troppo alta"
                return AuthResult.RELAY_DETECTED, self.debug_info
            
        # Margine di tolleranza aumentato
        max_allowed_time = (2 * self.vehicle.MAX_DISTANCE / self.vehicle.LIGHT_SPEED) * 1e9 * 2.0
        if round_trip_time > max_allowed_time:
            if random.random() < 0.85:  # 85% di probabilità di rilevamento
                self.debug_info["reason"] = "Tempo di risposta troppo alto"
                return AuthResult.RELAY_DETECTED, self.debug_info
            
        return AuthResult.SUCCESS, self.debug_info 