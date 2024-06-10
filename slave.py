import grpc
from concurrent import futures
import yaml
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proto import store_pb2
from proto import store_pb2_grpc

class KeyValueStoreSlave(store_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        self.data = {}
    
    def canCommit(self, request, context):
        return store_pb2.VoteResponse(vote=True)
    
    def doCommit(self, request, context):
        self.data[request.key] = request.value
        return store_pb2.CommitResponse(success=True)
    
    def get(self, request, context):
        key = request.key
        if key in self.data:
            return store_pb2.GetResponse(value=self.data[key], found=True)
        return store_pb2.GetResponse(found=False)
    
def serve(ip, port, master_ip, master_port):
    with grpc.insecure_channel(f'{master_ip}:{master_port}') as channel:
        stub = store_pb2_grpc.KeyValueStoreStub(channel)
        stub.registerNode(store_pb2.NodeInfo(ip=ip, port=port))
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    store_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreSlave(), server)
    server.add_insecure_port(f'{ip}:{port}')
    server.start()
    
    print(f'Slave started at {ip}:{port}')
    server.wait_for_termination()

if __name__ == '__main__':
    with open('centralized_config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    slave_config = config['slaves']
    for slave in slave_config:
        serve(slave['ip'], slave['port'], config['master']['ip'], config['master']['port'])
