"""Модуль клиента"""
import asyncio
import sys
import logging
import json
from aioconsole import ainput
from logger import initialize_logger


class Client:
    """Класс клиента
    :param server_ip: ip сервера
    :type server_ip: str
    :param server_port: порт сервера
    :type server_port: int
    :param reader: StreamReader
    :type reader: asyncio.StreamReader
    :param writer: StreamWriter
    :type writer: asyncio.StreamWriter
    :param logger: логгер
    :type logger: logging.Logger
    """
    def __init__(self, server_ip: str, server_port: int):
        self.__server_ip = server_ip
        self.__server_port = server_port
        self.__reader: asyncio.StreamReader = None
        self.__writer: asyncio.StreamWriter = None
        self.__logger: logging.Logger = initialize_logger('client')

    @property
    def server_ip(self):
        return self.__server_ip

    @property
    def server_port(self):
        return self.__server_port

    @property
    def reader(self):
        return self.__reader

    @property
    def writer(self):
        return self.__writer
    
    @property
    def logger(self):
        return self.__logger

    async def connect_to_server(self):
        """Подключение клиента к серверу"""
        try:
            self.__reader, self.__writer = await asyncio.open_connection(
                self.server_ip, self.server_port)
            await asyncio.gather(
                self.receive_messages(),
                self.client_input()
            )
        except Exception as e:
            self.logger.error("Ошибка при подключении к серверу")

    async def receive_messages(self):
        """Принятие сообщения от сервера"""
        server_message: dict = {'result': None}
        server_message = await self.get_server_message()
        if server_message['result']:
            result_str = f"Принято сообщение от сервера. "\
                        f"Выражение {server_message['expression']} = "\
                        f"{server_message['result']}"
        else:
            result_str = "Не является простым математическим выражением"
        print(result_str)
        self.logger.info(result_str)

    async def get_server_message(self):
        """Чтение сообщения и его декодирование"""
        return json.loads((await self.reader.read(255)).decode('utf8'))   

    async def client_input(self):
        """Клиентский ввод"""
        client_message: str = None
        wrong_input = True
        while wrong_input:
            client_message = await ainput(
                "Введите простое математическое выражение: \n"
            )
            if all(ch in '0123456789 +-*/()' for ch in client_message):
                wrong_input = False
            else: 
                print("Ошибка ввода. ")
                print("Выражение не должно содержать буквы или знаки кроме +-*/")
        self.writer.write(client_message.encode('utf8'))
        await self.writer.drain()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(
            f"Неверный хост или порт."
            f"Введите строку типа: {sys.argv[0]} HOST_IP PORT"
        )

    client = Client(sys.argv[1], sys.argv[2])
    asyncio.run(client.connect_to_server())
