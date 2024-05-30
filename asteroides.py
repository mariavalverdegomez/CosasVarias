import pygame
import math
import random
from pydub import AudioSegment
from pydub.generators import Sine

# Inicialización de Pygame
pygame.init()

# Configuración de la pantalla al tamaño máximo disponible
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Juego de Nave Espacial")

# Colores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Generar sonido de rebote
def crear_sonido_rebote():
    frecuencia = 400  # Frecuencia del sonido de rebote
    duracion = 200  # Duración en milisegundos
    volumen = -10  # Volumen en decibelios

    rebote = Sine(frecuencia).to_audio_segment(duration=duracion, volume=volumen)
    rebote.export("rebote.wav", format="wav")

# Generar sonido de disparo
def crear_sonido_disparo():
    frecuencia = 800  # Frecuencia del sonido de disparo
    duracion = 100  # Duración en milisegundos
    volumen = -5  # Volumen en decibelios

    disparo = Sine(frecuencia).to_audio_segment(duration=duracion, volume=volumen)
    disparo.export("disparo.wav", format="wav")

# Crear los sonidos
crear_sonido_rebote()
crear_sonido_disparo()

# Cargar sonidos
sonido_rebote = pygame.mixer.Sound('rebote.wav')
sonido_disparo = pygame.mixer.Sound('disparo.wav')

# Configuración de la nave
class Nave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # Ángulo en grados
        self.size = 20  # Tamaño del triángulo

    def draw(self, screen):
        # Calcular los vértices del triángulo para que parezca una nave
        tip = (self.x + math.cos(math.radians(self.angle)) * self.size,
               self.y + math.sin(math.radians(self.angle)) * self.size)
        left = (self.x + math.cos(math.radians(self.angle + 135)) * self.size,
                self.y + math.sin(math.radians(self.angle + 135)) * self.size)
        right = (self.x + math.cos(math.radians(self.angle + 225)) * self.size,
                 self.y + math.sin(math.radians(self.angle + 225)) * self.size)
        rear_left = (self.x + math.cos(math.radians(self.angle + 180)) * self.size / 2,
                     self.y + math.sin(math.radians(self.angle + 180)) * self.size / 2)
        rear_right = (self.x + math.cos(math.radians(self.angle + 180)) * self.size / 2,
                      self.y + math.sin(math.radians(self.angle + 180)) * self.size / 2)

        pygame.draw.polygon(screen, BLUE, [tip, left, rear_left, rear_right, right])

    def rotate(self, direction):
        self.angle += direction * 5

# Configuración de los disparos
class Disparo:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.life = WIDTH // self.speed  # Vida del disparo basada en la anchura de la pantalla

    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        self.life -= 1
        # Reaparecer en el lado opuesto de la pantalla
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 3)

# Configuración de las bolas
class Bola:
    def __init__(self, x, y, vx, vy, mass):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.size = int(mass ** 0.5) * 5  # Tamaño proporcional a la masa
        self.max_speed = 5  # Velocidad máxima

    def update(self, bolas):
        # Afectar velocidad por la gravedad de otras bolas
        for bola in bolas:
            if bola != self:
                dx = bola.x - self.x
                dy = bola.y - self.y
                distance = math.hypot(dx, dy)
                if distance > 0 and distance < self.size + bola.size:
                    # Colisiones entre bolas
                    self.collide(bola)
                elif distance > 0:
                    # Gravedad entre bolas
                    force = self.mass * bola.mass / distance**2
                    self.vx += force * dx / distance / self.mass
                    self.vy += force * dy / distance / self.mass

        self.x += self.vx
        self.y += self.vy

        # Limitar la velocidad
        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed

        # Reaparecer en el lado opuesto de la pantalla
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

    def divide(self):
        if self.mass > 4:  # Si la masa es mayor que 4, se puede dividir
            new_mass = self.mass // 4
            new_speed = 2
            return [
                Bola(self.x, self.y, random.uniform(-new_speed, new_speed), random.uniform(-new_speed, new_speed), new_mass),
                Bola(self.x, self.y, random.uniform(-new_speed, new_speed), random.uniform(-new_speed, new_speed), new_mass),
                Bola(self.x, self.y, random.uniform(-new_speed, new_speed), random.uniform(-new_speed, new_speed), new_mass),
                Bola(self.x, self.y, random.uniform(-new_speed, new_speed), random.uniform(-new_speed, new_speed), new_mass)
            ]
        return []

    def collide(self, other):
        # Calcula el nuevo vector de velocidad después de la colisión
        total_mass = self.mass + other.mass
        new_vx_self = (self.vx * (self.mass - other.mass) + 2 * other.mass * other.vx) / total_mass
        new_vy_self = (self.vy * (self.mass - other.mass) + 2 * other.mass * other.vy) / total_mass
        new_vx_other = (other.vx * (other.mass - self.mass) + 2 * self.mass * self.vx) / total_mass
        new_vy_other = (other.vy * (other.mass - self.mass) + 2 * self.mass * self.vy) / total_mass

        self.vx = new_vx_self
        self.vy = new_vy_self
        other.vx = new_vx_other
        other.vy = new_vy_other

        # Ajustar las posiciones para separarlas
        overlap = 0.5 * (self.size + other.size - math.hypot(self.x - other.x, self.y - other.y) + 1)
        angle = math.atan2(self.y - other.y, self.x - other.x)
        self.x += math.cos(angle) * overlap
        self.y += math.sin(angle) * overlap
        other.x -= math.cos(angle) * overlap
        other.y -= math.sin(angle) * overlap

        # Reproducir sonido de rebote
        sonido_rebote.play()

# Función principal del juego
def main():
    running = True
    clock = pygame.time.Clock()
    nave = Nave(WIDTH // 2, HEIGHT // 2)
    disparos = []
    bolas = [Bola(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(-1, 1), random.uniform(-1, 1), 64) for _ in range(4)]  # Aumentamos la masa inicial de 16 a 64

    # Marcador de bolas destruidas
    bolas_destruidas_grandes = 0
    bolas_destruidas_medianas = 0
    bolas_destruidas_pequenas = 0
    font = pygame.font.Font(None, 36)

    # Tiempo de espera entre disparos (en milisegundos)
    tiempo_espera_disparo = 500  # 0.5 segundos
    ultimo_disparo = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            nave.rotate(-1)
        if keys[pygame.K_RIGHT]:
            nave.rotate(1)
        if keys[pygame.K_SPACE] and len(disparos) < 5:
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - ultimo_disparo > tiempo_espera_disparo:
                angle = nave.angle
                x = nave.x + math.cos(math.radians(angle)) * nave.size
                y = nave.y + math.sin(math.radians(angle)) * nave.size
                disparos.append(Disparo(x, y, angle))
                sonido_disparo.play()
                ultimo_disparo = tiempo_actual

        screen.fill((0, 0, 0))
        nave.draw(screen)

        for disparo in disparos[:]:
            disparo.update()
            if disparo.life <= 0:
                disparos.remove(disparo)
            else:
                disparo.draw(screen)

        for bola in bolas[:]:
            bola.update(bolas)
            bola.draw(screen)
            for disparo in disparos[:]:
                if math.hypot(disparo.x - bola.x, disparo.y - bola.y) < bola.size:
                    disparos.remove(disparo)
                    nuevas_bolas = bola.divide()
                    if bola.mass == 64:
                        bolas_destruidas_grandes += 1
                    elif bola.mass == 16:
                        bolas_destruidas_medianas += 1
                    elif bola.mass == 4:
                        bolas_destruidas_pequenas += 1
                    bolas.remove(bola)
                    bolas.extend(nuevas_bolas)
                    break

        # Mostrar el marcador en la pantalla
        marcador = f"Bolas grandes destruidas: {bolas_destruidas_grandes}  Bolas medianas destruidas: {bolas_destruidas_medianas}  Bolas pequeñas destruidas: {bolas_destruidas_pequenas}"
        texto = font.render(marcador, True, WHITE)
        screen.blit(texto, (20, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
