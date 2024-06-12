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
    channel = grpc.insecure_channel('127.0.0.1:32770')
    stub = store_pb2_grpc.KeyValueStoreStub(channel)

    # Lista de pruebas
    tests = [
        {"key": "testKey1", "value": "testValue1"},
        {"key": "testKey2", "value": "testValue2"},
        {"key": "testKey3", "value": "testValue3"}
    ]

    # Probar el método .put
    print("Probando .put")
    for test in tests:
        put_response = stub.put(store_pb2.PutRequest(key=test["key"], value=test["value"]))
        assert put_response.success, f"Put falló para key={test['key']}"
        print(f"Put response para key={test['key']}: {put_response.success}")

    # Probar el método .get
    print("\nProbando .get")
    for test in tests:
        get_response = stub.get(store_pb2.GetRequest(key=test["key"]))
        assert get_response.found, f"Get falló al encontrar key={test['key']}"
        assert get_response.value == test["value"], f"Valor inesperado para key={test['key']}: {get_response.value}"
        print(f"Get response para key={test['key']}: found={get_response.found}, value={get_response.value}")

    # Probar el método .slowDown
    print("\nProbando .slowDown")
    slow_down_response = stub.slowDown(store_pb2.SlowDownRequest(seconds=2))
    assert slow_down_response.success, "SlowDown falló"
    print(f"SlowDown response: {slow_down_response.success}")

    # Esperar unos segundos para observar el efecto de slowDown
    time.sleep(3)

    # Probar el método .get nuevamente
    print("\nProbando .get después de slowDown")
    for test in tests:
        get_response = stub.get(store_pb2.GetRequest(key=test["key"]))
        assert get_response.found, f"Get falló al encontrar key={test['key']} después de slowDown"
        assert get_response.value == test["value"], f"Valor inesperado para key={test['key']} después de slowDown: {get_response.value}"
        print(f"Get response para key={test['key']} después de slowDown: found={get_response.found}, value={get_response.value}")

    # Probar el método .restore
    print("\nProbando .restore")
    restore_response = stub.restore(store_pb2.RestoreRequest())
    assert restore_response.success, "Restore falló"
    print(f"Restore response: {restore_response.success}")

    # Probar el método .get después de restore
    print("\nProbando .get después de restore")
    for test in tests:
        get_response = stub.get(store_pb2.GetRequest(key=test["key"]))
        assert get_response.found, f"Get falló al encontrar key={test['key']} después de restore"
        assert get_response.value == test["value"], f"Valor inesperado para key={test['key']} después de restore: {get_response.value}"
        print(f"Get response para key={test['key']} después de restore: found={get_response.found}, value={get_response.value}")
    

if __name__ == '__main__':
    run()
