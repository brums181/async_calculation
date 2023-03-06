"""Модель клиента. Вспомогательный модуль для сервера"""
import asyncio
import sys
from aioconsole import ainput


class ClientModel:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.__reader: asyncio.StreamReader = reader
        self.__writer: asyncio.StreamWriter = writer
        self.__ip: str = writer.get_extra_info('peername')[0]
        self.__port: int = writer.get_extra_info('peername')[1]

    def __str__(self):
        return f" {self.ip}:{self.port}"

    @property
    def reader(self):
        return self.__reader

    @property
    def writer(self):
        return self.__writer

    @property
    def ip(self):
        return self.__ip

    @property
    def port(self):
        return self.__port

    async def get_message(self):
        return str((await self.reader.read(255)).decode('utf8'))



    