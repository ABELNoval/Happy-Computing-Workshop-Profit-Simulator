import random
import math


class RandomVariables:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    # -------------------------
    # Uniforme (0,1)
    # -------------------------
    def uniforme(self):
        return self.rng.random()

    # -------------------------
    # Exponencial
    # media = tiempo promedio
    # -------------------------
    def exponencial(self, media):
        if media <= 0:
            raise ValueError("La media debe ser positiva")

        u = self.uniforme()

        while u == 0:
            u = self.uniforme()

        return -media * math.log(u)

    # -------------------------
    # Tipo de servicio
    # Distribución discreta
    # -------------------------
    def tipo_servicio(self):
        u = self.uniforme()

        # Servicio 1
        if u <= 0.45:
            return 1

        # Servicio 2
        elif u <= 0.70:
            return 2

        # Servicio 3
        elif u <= 0.80:
            return 3

        # Servicio 4
        return 4

    # -------------------------
    # Normal (Box-Muller)
    # -------------------------
    def normal(self, media, varianza):
        if varianza < 0:
            raise ValueError("La varianza no puede ser negativa")

        u1 = self.uniforme()
        u2 = self.uniforme()

        z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)

        valor = media + math.sqrt(varianza) * z

        # evitar tiempos negativos
        while valor <= 0:
            u1 = self.uniforme()
            u2 = self.uniforme()

            z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)

            valor = media + math.sqrt(varianza) * z

        return valor

    # -------------------------
    # Llegada de clientes
    # media = 20 minutos
    # -------------------------
    def tiempo_entre_llegadas(self):
        return self.exponencial(20)

    # -------------------------
    # Tiempo del vendedor
    # N(5,2)
    # -------------------------
    def tiempo_vendedor(self):
        return self.normal(5, 2)

    # -------------------------
    # Tiempo técnico
    # Exp(media = 20)
    # -------------------------
    def tiempo_tecnico(self):
        return self.exponencial(20)

    # -------------------------
    # Tiempo técnico especializado
    # Exp(media = 15)
    # -------------------------
    def tiempo_tecnico_especializado(self):
        return self.exponencial(15)
