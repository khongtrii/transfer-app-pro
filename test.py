import asyncio


async def main():
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)

    writer.write(b"LIST\n")
    await writer.drain()

    data = await reader.read(4096)
    print("Server response:")
    print(data.decode())

    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())