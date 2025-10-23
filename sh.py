import asyncio
import os
import re
import logging
from datetime import datetime, timedelta, timezone

__version__ = '0.2'


class IpLoggerServer:
    __ip_last_time_checked = datetime.now(timezone.utc)
    ipdb = dict()
    addr = '127.0.0.1'
    port = 8080
    kill_time = timedelta(minutes=30)
    refresh_rate = timedelta(seconds=60)
    data_filepath = os.path.join(os.path.dirname(__file__), 'ipdata.txt')
    log_filepath = os.path.join(os.path.dirname(__file__), 'IpLogger.log')
    ip_get_view = '/get'
    ip_log_view = '/log'

    @classmethod
    async def __log_ip(cls, reader, writer):
        try:
            data = await reader.read(100)
            if len(data) < 10:  # Минимальная проверка валидности HTTP запроса
                return
                
            addr = writer.get_extra_info('peername')[0]
            writer.write('HTTP/1.0 200 OK\r\n'.encode())
            writer.write('Content-Type: text/html\r\n\r\n'.encode())
            logging.info('connection accepted: {}'.format(addr))
            
            decoded_data = data.decode('utf-8', errors='ignore')
            parts = decoded_data.split()
            if len(parts) < 2:
                return
                
            view = parts[1]
            time = datetime.now(timezone.utc)
            
            if view == cls.ip_get_view:
                if time - cls.__ip_last_time_checked > cls.refresh_rate:
                    cls.__ip_last_time_checked = time
                    await cls.__ip_time_check()
                writer.write(';'.join(cls.ipdb.keys()).encode('utf-8'))
                logging.info('data sent')
            elif view == cls.ip_log_view:
                cls.ipdb[addr] = time
                logging.info('ip logged: {}'.format(addr))
            else:
                logging.info('unknown view: {}'.format(view))
                
            await writer.drain()
        except Exception as e:
            logging.error('Error in __log_ip: {}'.format(e))
        finally:
            writer.close()

    @classmethod
    async def __ip_time_check(cls):
        if not cls.ipdb:
            return
        current_time = datetime.now(timezone.utc)
        ips_to_remove = []
        
        for ip, last_seen in cls.ipdb.items():
            if current_time - last_seen > cls.kill_time:
                ips_to_remove.append(ip)
                
        for ip in ips_to_remove:
            removed_ip = cls.ipdb.pop(ip, None)
            if removed_ip:
                logging.info('ip removed: {}'.format(ip))

    @classmethod
    async def __periodic_ip_check(cls):
        """Фоновая задача для периодической проверки IP"""
        while True:
            await asyncio.sleep(cls.refresh_rate.total_seconds())
            await cls.__ip_time_check()

    @classmethod
    def __stop(cls, loop):
        cls.save()
        loop.close()
        logging.info('server terminated.')
        logging.shutdown()

    @classmethod
    def save(cls):
        try:
            with open(cls.data_filepath, 'w', encoding='utf-8') as f:
                for ip, timestamp in cls.ipdb.items():
                    f.write('{}|{}\n'.format(ip, timestamp.isoformat()))
            logging.info('Data saved successfully')
        except Exception as e:
            logging.error('Unable to write to data file: {}'.format(e))

    @classmethod
    def load(cls):
        try:
            if not os.path.exists(cls.data_filepath):
                logging.info('ipdata file not found, starting fresh')
                return
                
            with open(cls.data_filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '|' in line:
                        ip, timestamp_str = line.split('|', 1)
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str)
                            cls.ipdb[ip] = timestamp
                        except ValueError:
                            # Если не удалось распарсить timestamp, используем текущее время
                            cls.ipdb[ip] = datetime.now(timezone.utc)
            logging.info('Data loaded successfully: {} IPs'.format(len(cls.ipdb)))
        except Exception as e:
            logging.error('Error loading data file: {}'.format(e))

    @classmethod
    def run(cls):
        logging.basicConfig(
            filename=cls.log_filepath, 
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s'
        )
        logging.info('Server started: {}:{}'.format(cls.addr, cls.port))
        
        cls.load()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # ИСПРАВЛЕННАЯ СТРОКА - убран параметр loop
            server_coro = asyncio.start_server(cls.__log_ip, cls.addr, cls.port)
            server = loop.run_until_complete(server_coro)
            
            # Запускаем фоновую задачу для периодической проверки
            periodic_task = loop.create_task(cls.__periodic_ip_check())
            
            logging.info('Serving on {}'.format(server.sockets[0].getsockname()))
            print(f"Сервер запущен на {cls.addr}:{cls.port}")
            print("Для остановки нажмите Ctrl+C")
            loop.run_forever()
            
        except (KeyboardInterrupt, SystemExit):
            logging.info('Server shutdown requested')
            print("\nСервер остановлен...")
        except Exception as e:
            logging.error('Server error: {}'.format(e))
            print(f"Ошибка сервера: {e}")
        finally:
            if 'periodic_task' in locals():
                periodic_task.cancel()
            cls.__stop(loop)


# Добавленные принты для отладки
print(f"IP Logger Server v{__version__} starting on {IpLoggerServer.addr}:{IpLoggerServer.port}")
print(f"Логи будут сохраняться в: {IpLoggerServer.log_filepath}")
print(f"Данные IP будут в: {IpLoggerServer.data_filepath}")

if __name__ == "__main__":
    IpLoggerServer.run()