import asyncio
import time

from centralized_node import StorageServiceServicer
import centralized_node

async def main():
    # Create The master node
    node_master = StorageServiceServicer(True, 0)
    node_master.start_server()

    # Create the slave node 1
    node_1 = StorageServiceServicer(False, 1)
    node_1.start_server()

    # Create the slave node 2
    node_2 = StorageServiceServicer(False, 2)
    node_2.start_server()

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        node_master.stop(0)
        node_1.stop(0)
        node_2.stop(0)

if __name__ == '__main__':
    asyncio.run(main())