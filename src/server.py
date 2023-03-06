"""Модуль сервера"""
import asyncio
import sys
import numexpr as ne

from client import Client


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
        client = Client(client_reader, client_writer)
        task = asyncio.create_task(self.receiving_and_calc(client))
        client_ip = client_writer.get_extra_info('peername')[0]
        client_port = client_writer.get_extra_info('peername')[1]
        print(f"Подключен новый клиент: {client_ip}:{client_port}")
    
    async def receiving_and_calc(self, client: Client):
        """Прием сообщения пользователя, возвращение результатов вычисления
        Возвращает результат в случае верного ввода, иначе сообщение об ошибке
        :param client: клиент, посылающий сообщение
        :type client: Client
        """
        while True:
            client_message = await client.send_message()
            if client_message == "exit":
                break
            try:
                result_eval = str(float(ne.evaluate(client_message)))
            except ValueError:
                result_eval = "Вычисление невозможно."\
                    "Не является простым математическим выражением."
                
            client.writer.write(result_eval)
            await client.writer.drain()

        print("Соединение с клиентом прервано")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(
            f"Неверный хост или порт."
            f"Введите строку типа: {sys.argv[0]} HOST_IP PORT"
        )

    loop = asyncio.get_event_loop()
    server = Server(sys.argv[1], sys.argv[2], loop)
    server.start_server()
