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

def accept_client(self, client_reader: asyncio.StreamReader, 
                  client_writer: asyncio.StreamWriter):
    """Callback-функция, запускаемая при подключении клиента
    :param client_reader: StreamReader
    :type client_reader: asyncio.StreamReader
    :param client_writer: StreamWriter
    :type client_writer: asyncio.StreamWriter
    """
    task = asyncio.create_task(self.handle_client(client_reader, client_writer))
    client_ip = client_writer.get_extra_info('peername')[0]
    client_port = client_writer.get_extra_info('peername')[1]
    print(f"Подключен новый клиент: {client_ip}:{client_port}")
 
async def handle_client(self, client_reader: asyncio.StreamReader):
    """ Получение сообщения клиента
    :param client_reader: StreamReader
    :type client_reader: asyncio.StreamReader
    """
    # пока простое чтение строки
    client_message = str((await client_reader.read(255)).decode('utf8'))
    print(client_message)


if __name__ == '__main__':
    argv_len = 3
    if len(sys.argv) < argv_len:
        sys.exit(
            f"Неверный хост или порт."
            f"Введите строку типа: {sys.argv[0]} HOST_IP PORT"
        )

    loop = asyncio.get_event_loop()
    server = Server(sys.argv[1], sys.argv[2], loop)
    server.start_server()
