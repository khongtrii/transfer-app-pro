import asyncio
import json
import pandas as pd

async def main():
    ip_host = input("Entry server ip: ")
    reader, writer = await asyncio.open_connection(ip_host, 8888)

    writer.write(b"PING_LIST\n")
    await writer.drain()

    data = await reader.read(4096)
    print("Server response:")

    data_json = json.loads(data.decode())
    df = pd.DataFrame(data_json)
    print(df)

    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
