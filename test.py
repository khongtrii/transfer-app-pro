import asyncio
import pandas as pd

async def main():
    ip_host = input("Entry server ip: ")
    reader, writer = await asyncio.open_connection(ip_host, 8888)

    writer.write(b"PING_LIST\n")
    await writer.drain()

    data = await reader.read(4096)
    print("Server response:")
    display(pd.DataFrame(data.decode()))

    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
