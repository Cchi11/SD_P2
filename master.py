import grpc
from concurrent import futures
import time
import yaml
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from proto import store_pb2
from proto import store_pb2_grpc

class KeyValueStoreMaster(store_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        self.data = {}
        self.slaves = []
    
    def registerNode(self, request, context):
        self.slaves.append((request.ip, request.port))
        return store_pb2.Response(success=True)
    
    def put(self, request, context):
        key, value = request.key, request.value
        if key in self.data:
            return store_pb2.Response(success=False)
        
        can_commit_responses = []
        for ip, port in self.slaves:
            with grpc.insecure_channel(f'{ip}:{port}') as channel:
                stub = store_pb2_grpc.KeyValueStoreStub(channel)
                response = stub.canCommit(store_pb2.CanCommitRequest(key=key))
                can_commit_responses.append(response.vote)
        
        if all(can_commit_responses):
            self.data[key] = value
            for ip, port in self.slaves:
                with grpc.insecure_channel(f'{ip}:{port}') as channel:
                    stub = store_pb2_grpc.KeyValueStoreStub(channel)
                    response = stub.doCommit(store_pb2.DoCommitRequest(key=key, value=value))
                    if not response.success:
                        return store_pb2.Response(success=False)
            return store_pb2.Response(success=True)
        return store_pb2.Response(success=False)

    def get(self, request, context):
        key = request.key
        if key in self.data:
            return store_pb2.GetResponse(value=self.data[key], found=True)
        return store_pb2.GetResponse(found=False)
    
def serve():
    with open('centralized_config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    master_ip = config['master']['ip']
    master_port = config['master']['port']
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    store_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreMaster(), server)
    server.add_insecure_port(f'{master_ip}:{master_port}')
    server.start()
    
    print(f'Server started at {master_ip}:{master_port}')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
