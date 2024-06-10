import asyncio
import yaml
from master import serve as serve_master
from slave import serve as serve_slave

async def main():
    with open('centralized_config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    # Iniciar el nodo maestro
    master_task = asyncio.create_task(serve_master())
    
    await asyncio.sleep(5)  # Dar tiempo para que el maestro se inicie
    
    # Iniciar nodos esclavos
    slave_config = config['slaves']
    slave_tasks = []
    for slave in slave_config:
        slave_task = asyncio.create_task(
            serve_slave(slave['ip'], slave['port'], config['master']['ip'], config['master']['port'])
        )
        slave_tasks.append(slave_task)
    
    # Esperar a que todos los nodos terminen
    await master_task
    await asyncio.gather(*slave_tasks)

if __name__ == '__main__':
    asyncio.run(main())
