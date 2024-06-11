import grpc
import os
import sys
import time

# Asumiendo que los archivos protobuf están en el directorio 'proto'
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proto'))

import store_pb2
import store_pb2_grpc


def run():
    # Conectar al servidor gRPC
    channel = grpc.insecure_channel('localhost:50051')
    stub = store_pb2_grpc.KeyValueStoreStub(channel)

    # Probar el método .put
    print("Probando .put")
    put_response = stub.put(store_pb2.PutRequest(key='testKey', value='testValue'))
    print(f"Put response: {put_response.success}")

    # Probar el método .get
    print("Probando .get")
    get_response = stub.get(store_pb2.GetRequest(key='testKey'))
    print(f"Get response: found={get_response.found}, value={get_response.value}")

    # Probar el método .slowDown
    print("Probando .slowDown")
    slow_down_response = stub.slowDown(store_pb2.SlowDownRequest(delay=2))
    print(f"SlowDown response: {slow_down_response.success}")

    # Esperar unos segundos para observar el efecto de slowDown
    time.sleep(3)

    # Probar el método .get nuevamente
    print("Probando .get después de slowDown")
    get_response = stub.get(store_pb2.GetRequest(key='testKey'))
    print(f"Get response: found={get_response.found}, value={get_response.value}")

    # Probar el método .restore
    print("Probando .restore")
    restore_response = stub.restore(store_pb2.RestoreRequest())
    print(f"Restore response: {restore_response.success}")

    # Probar el método .get después de restore
    print("Probando .get después de restore")
    get_response = stub.get(store_pb2.GetRequest(key='testKey'))
    print(f"Get response: found={get_response.found}, value={get_response.value}")


if __name__ == '__main__':
    run()
