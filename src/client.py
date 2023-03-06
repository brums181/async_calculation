import asyncio
import sys
from aioconsole import ainput


class Client:
    def __init__(self, server_ip: str, server_port: int):
        self.__server_ip: str = server_ip
        self.__server_port: int = server_port
        self.__reader: asyncio.StreamReader = None
        self.__writer: asyncio.StreamWriter = None

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
            print("Ошибка в подключении клиента")


    async def receive_messages(self):
        server_message: str = None
        while server_message != 'exit':
            server_message = await self.get_server_message()
            print(f"{server_message}")


    async def get_server_message(self):
        return str((await self.reader.read(255)).decode('utf8'))

    async def client_input(self):
        client_message: str = None
        client_message = await ainput("Enter")
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
