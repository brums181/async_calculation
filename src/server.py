"""Модуль сервера"""
import asyncio
import sys
import numexpr as ne
import json

from client_model import ClientModel


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

    @property
    def ip(self):
        return self.__ip

    @property
    def port(self):
        return self.__port

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
            print("Ошибка при запуске сервера")
        
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
        print(self.clients)
        client_ip = client_writer.get_extra_info('peername')[0]
        client_port = client_writer.get_extra_info('peername')[1]
        print(f"Подключен новый клиент: {client_ip}:{client_port}")
        # Заверение выполнения задачи
        task.add_done_callback(self.disconnect_client)
    
    async def receiving_and_calc(self, client: ClientModel):
        """Прием сообщения пользователя, возвращение результатов вычисления
        Возвращает результат в случае верного ввода, иначе сообщение об ошибке
        :param client: клиент, посылающий сообщение
        :type client: Client
        """
        while True:
            client_message = await client.get_message()
            result_eval = None
            res = None
            if client_message == "exit":
                break
            try:
                result_eval = ne.evaluate(client_message)
            except (KeyError, TypeError):
                res = "Вычисление невозможно."\
                    "Не является простым математическим выражением."
            
            if result_eval:
                res = str(float(result_eval))

            json_mess_en = json.dumps({'expression': client_message, 'result': res}).encode()
            client.writer.write(json_mess_en)
            await client.writer.drain()

        print("Соединение с клиентом прервано")

    
    def disconnect_client(self, task: asyncio.Task):
        """Отсоединение клиента
        :param task: задача
        :type task: asyncio.Task
        """
        client = self.clients[task]
        del self.clients[task]
        client.writer.write('exit'.encode('utf8'))
        client.writer.close()
        print("Соединение с клиентом закрыто")

    def shutdown_server(self):
        """Отключение сервера"""
        print("Отключение сервера")
        # for client in self.clients.values():
        #     client.writer.write('exit'.encode('utf8'))
        self.loop.stop()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(
            f"Неверный хост или порт."
            f"Введите строку типа: {sys.argv[0]} HOST_IP PORT"
        )

    loop = asyncio.get_event_loop()
    server = Server(sys.argv[1], sys.argv[2], loop)
    server.start_server()
