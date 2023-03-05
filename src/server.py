"""Модуль сервера"""
import asyncio
import sys


class Server:
    """Класс сервера
    :param ip: ip, который будет использоваться
    :type server_ip: str
    :param port: порт сервера
    :type port: int
    :param loop: запущенный цикл событий
    :type loop: asyncio.AbstractEventLoop
    """
    def __init__(self, ip: str, port: int, loop: asyncio.AbstractEventLoop):
        self.__ip = ip
        self.__port = port
        self.__loop = loop

    @property
    def ip(self):
        return self.__ip

    @property
    def port(self):
        return self.__port

    @property
    def loop(self):
        return self.__loop

    def start_server(self):
        """Запуск сервера по заданному адресу и порту"""
        try:
            server = asyncio.start_server(
                self.accept_client, self.ip, self.port
            )
            self.loop.run_until_complete(server)
            self.loop.run_forever()
        except Exception as e:
            print("Ошибка при запуске сервера")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(f"Usage: {sys.argv[0]} HOST_IP PORT")

    loop = asyncio.get_event_loop()
    server = Server(sys.argv[1], sys.argv[2], loop)
    server.start_server()
    