import socket


class Clientconn:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.host = host
        self.port = port


class Serverconn:
    def __init__(self, host, port, connection_limit):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.host = host
        self.port = port
        self.socket.listen(connection_limit)

class Button:

    def __init__(self, rect, ):
        self.rect = rect
        self.enabled = True
        self.e_sprite = pygame.image.load(data("dice_button.png"))
        self.d_sprite = pygame.image.load(data("dice_empty.png"))
        self.load_imgs()

    def draw(self):
        if self.enabled:
            screen.blit(self.e_sprite, self.rect)
        else:
            screen.blit(self.d_sprite, self.rect)


class DiceButton(Button):

    def load_imgs(self):
        self.e_sprite = pygame.image.load(data("dice_button.png"))
        self.d_sprite = pygame.image.load(data("dice_empty.png"))

    def press(self):
        pass



