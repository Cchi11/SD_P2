import grpc
import concurrent
import os
import time
import sys
from concurrent import futures
import yaml
import concurrent.futures

# Asumiendo que los archivos protobuf están en el directorio 'proto'
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proto'))
sys.path.append(os.getcwd())

import store_pb2
import store_pb2_grpc
import store_service

class Decentralized_Node():

    def __init__(self, node_id, node_ip, node_port):
        self.node_id = node_id
        self.node_ip = node_ip
        self.node_port = node_port
        self.weight = None

class DecentralizedStorageServiceServicer(store_pb2_grpc.KeyValueStoreServicer):

    def __init__(self, node_id):
        self.store = store_service.StoreService()
        self.config = self.load_config()
        self.delay = 0
        self.store = store_service.StoreService()
        
        self.id = node_id
        self.node = Decentralized_Node(node_id, self.config['nodes'][node_id]['ip'], self.config['nodes'][node_id]['port'])
        if (node_id == 1):
            self.node.weight = 2
        else:
            self.node.weight = 1

        

        
    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'decentralized_config.yaml')
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
        
        
    def start_server(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        store_pb2_grpc.add_KeyValueStoreServicer_to_server(self, self.server)
        self.server.add_insecure_port(f'{self.node.node_ip}:{self.node.node_port}')
        self.server.start()
        print(f"Node {self.id} running on {self.node.node_ip}:{self.node.node_port}")

    def stop(self):
        self.server.stop(0)


    def quorumRequest(self, request, context):
        print(f"Node {self.id} received a quorum request of type {request.operation}")
        return store_pb2.QuorumResponse(weight=self.node.weight, success=True, id=self.id, ip=self.node.node_ip, port=self.node.node_port)
    
    
    def put(self, request, context):
        time.sleep(self.delay)
        key = request.key
        value = request.value

        # Send quorum request to other nodes
        quorum_count = self.node.weight
        quorum_threshold = 3  # Number of nodes needed to reach quorum for write
        responses = []
        reached_nodes = []

        if quorum_count >= quorum_threshold:
            self.store.put(key, value)
            return store_pb2.Response(success=True)
        else:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for node_info in self.config['nodes']:  # Iterating over the list of nodes
                    if node_info['id'] != self.id:
                        channel = grpc.insecure_channel(f"{node_info['ip']}:{node_info['port']}")
                        stub = store_pb2_grpc.KeyValueStoreStub(channel)
                        future = executor.submit(stub.quorumRequest, store_pb2.QuorumRequest(operation='put'))
                        responses.append(future)

                for future in concurrent.futures.as_completed(responses):
                    response = future.result()
                    quorum_count += response.weight
                    new_node = Decentralized_Node(response.id, response.ip, response.port)
                    new_node.weight = response.weight
                    reached_nodes.append(new_node)
                    if quorum_count >= quorum_threshold:
                        break

                # Once quorum is reached, do the commit
                for node in reached_nodes:
                    channel = grpc.insecure_channel(f"{node.node_ip}:{node.node_port}")
                    stub = store_pb2_grpc.KeyValueStoreStub(channel)
                    future = executor.submit(stub.doCommit, store_pb2.DoCommitRequest(key=key, value=value))
                    responses.append(future)

            return store_pb2.Response(success=True)
        
    def get(self, request, context):
        time.sleep(self.delay)
        key = request.key

        # Send quorum request to other nodes
        quorum_count = self.node.weight
        quorum_threshold = 2  # Number of nodes needed to reach quorum for write
        responses = []
        reached_nodes = []
        found, value = self.store.get(key)
        if quorum_count >= quorum_threshold:
            if found:
                return store_pb2.GetResponse(found=True, value=value)
            else:
                return store_pb2.GetResponse(found=False, value='')
        else:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for node_info in self.config['nodes']:  # Iterating over the list of nodes
                    if node_info['id'] != self.id:
                        channel = grpc.insecure_channel(f"{node_info['ip']}:{node_info['port']}")
                        stub = store_pb2_grpc.KeyValueStoreStub(channel)
                        future = executor.submit(stub.quorumRequest, store_pb2.QuorumRequest(operation='get'))
                        responses.append(future)

                for future in concurrent.futures.as_completed(responses):
                    response = future.result()
                    quorum_count += response.weight
                    new_node = Decentralized_Node(response.id, response.ip, response.port)
                    new_node.weight = response.weight
                    reached_nodes.append(new_node)
                    if quorum_count >= quorum_threshold:
                        break

                if found:
                    return store_pb2.GetResponse(found=True, value=value)
                else:
                    return store_pb2.GetResponse(found=False, value='')
            


    def doCommit(self, request, context):
        key = request.key
        value = request.value
        self.store.put(key, value)
        return store_pb2.Response(success=True)
    
    def slowDown(self, request, context):
        time.sleep(request.seconds)
        self.delay = request.seconds
        print(f"Node {self.id} slowed down for {request.seconds} seconds")
        return store_pb2.SlowDownResponse(success=True)
    
    def restore(self, request, context):
        time.sleep(self.delay)
        self.delay = 0
        print(f"Node {self.id} delay restored to 0 seconds")
        return store_pb2.RestoreResponse(success=True)
        


    
