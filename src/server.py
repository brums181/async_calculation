"""Модуль сервера"""
import asyncio
import sys
import numexpr as ne
import json
import logging
from typing import Union
from client_model import ClientModel
from logger import initialize_logger


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
        self.__clients: dict[asyncio.Task, ClientModel] = {}
        self.__logger: logging.Logger = initialize_logger('server')
        self.logger.info(f"Инициализирован сервер {self.ip}:{self.port}")

    @property
    def ip(self):
        return self.__ip

    @property
    def port(self):
        return self.__port
    
    @property
    def logger(self):
        return self.__logger

    @property
    def loop(self):
        return self.__loop
    
    @property
    def clients(self):
        return self.__clients

    def start_server(self):
        """Запуск сервера по заданному адресу и порту"""
        try:
            server = asyncio.start_server(
                self.accept_client, self.ip, self.port
            )
            self.loop.run_until_complete(server)
            self.loop.run_forever()
        except Exception as e:
            self.logger.error("Ошибка при запуске сервера")
        
        self.shutdown_server()

    def accept_client(self, client_reader: asyncio.StreamReader, 
                    client_writer: asyncio.StreamWriter):
        """Callback-функция, запускаемая при подключении клиента
        :param client_reader: StreamReader
        :type client_reader: asyncio.StreamReader
        :param client_writer: StreamWriter
        :type client_writer: asyncio.StreamWriter
        """
        client = ClientModel(client_reader, client_writer)
        task = asyncio.create_task(self.receiving_and_calc(client))
        self.clients[task] = client
        client_ip = client_writer.get_extra_info('peername')[0]
        client_port = client_writer.get_extra_info('peername')[1]
        info_str = f"Подключен новый клиент: {client_ip}:{client_port}"
        print(info_str)
        # Заверение выполнения задачи
        self.logger.info(info_str)
        task.add_done_callback(self.disconnect_client)
    
    async def receiving_and_calc(self, client: ClientModel):
        """Прием сообщения пользователя, возвращение результатов вычисления
        Возвращает результат в случае верного ввода, иначе сообщение об ошибке
        :param client: клиент, посылающий сообщение
        :type client: Client
        """
        client_message = await client.get_message()
        self.logger.info(f"Получено сообщение от клиента {client_message}")
        result_eval = None
        res = None
        info_str = None
        try:
            result_eval = ne.evaluate(client_message)
        except (KeyError, TypeError, SyntaxError):
            info_str = f"{client_message} не вычислено. "\
                    f"Не является простым математическим выражением"

        if result_eval is not None:
            res = float(result_eval)
            print("RESEVAL", res)
            info_str = (
                f"Выражение {client_message} вычислено. Результат = {res}"
            )

        self.logger.info(info_str)
        json_mess_en = self.to_json(client_message, res)
        print(json_mess_en)
        client.writer.write(json_mess_en)
        await client.writer.drain()
    
    def disconnect_client(self, task: asyncio.Task):
        """Отсоединение клиента
        :param task: задача
        :type task: asyncio.Task
        """
        client = self.clients[task]
        del self.clients[task]
        client.writer.close()
        self.logger.info("Соединение с клиентом прервано")

    def shutdown_server(self):
        """Отключение сервера"""
        info_str = "Сервер отключен"
        print(info_str)
        self.logger.info(info_str)
        self.loop.stop()

    def to_json(self, message: str, res: Union[float, None]):
        """Функция для превращения данных для отправки в json и их кодирование
        :param message: сообщение, пришедее от клиента
        :type message: str
        :param res: результат, вычисленный сервером
        :type res: float | str
        """
        return json.dumps(
            {'expression': message, 'result': res}
        ).encode()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(
            f"Неверный хост или порт."
            f"Введите строку типа: {sys.argv[0]} HOST_IP PORT"
        )

    loop = asyncio.get_event_loop()
    server = Server(sys.argv[1], sys.argv[2], loop)
    server.start_server()
