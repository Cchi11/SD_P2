import grpc
import concurrent
import os
import time
import sys
from concurrent import futures
import yaml

# Asumiendo que los archivos protobuf están en el directorio 'proto'
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proto'))
sys.path.append(os.getcwd())

import store_pb2
import store_pb2_grpc
import store_service


class Node:
    def __init__(self, node_id, node_ip, node_port):
        self.node_id = node_id
        self.node_ip = node_ip
        self.node_port = node_port


class StorageServiceServicer(store_pb2_grpc.KeyValueStoreServicer):
    def __init__(self, is_master, node_id):
        self.node_id = node_id
        self.is_master = is_master
        node_id == node_id
        self.delay = 0
        self.store = store_service.StoreService()
        self.nodes2PC = list()
        self.allNodes = list()
        self.config = self.load_config()

        if self.is_master:
            self.ip = self.config['master']['ip']
            self.port = self.config['master']['port']
            self.id = 'master'
        else:
            slave_config = next((s for s in self.config['slaves'] if s['id'] == node_id), None)
            if slave_config:
                self.ip = slave_config['ip']
                self.port = slave_config['port']

        self.node_registration(self.config['master']['ip'], self.config['master']['port'])

    # Load config data from YAML file
    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'centralized_config.yaml')
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
        
    def stop(self):
        self.server.stop(0)

    def start_server(self):
        # Create gRPC server
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        # Add our service to the server
        store_pb2_grpc.add_KeyValueStoreServicer_to_server(
            self,
            self.server
        )

        self.server.add_insecure_port(f'{self.ip}:{self.port}')
        self.server.start()

    def node_registration(self, ip, port):
        
        if not self.is_master:
            channel = grpc.insecure_channel(f'{ip}:{port}')
            self.master_stub = store_pb2_grpc.KeyValueStoreStub(channel)
            response = self.master_stub.registerNode(store_pb2.NodeInfo(id=self.node_id, ip=self.ip, port=self.port))
            if response.success:
                print(f'Node {self.node_id} registered successfully')
                return True
            else:
                print(f'Node {self.node_id} registration failed')
                return False
        else:
            self.nodes2PC.append(Node(self.node_id, self.ip, self.port))
            self.allNodes.append(Node(self.node_id, self.ip, self.port))
            return True

    def registerNode(self, request, context):
        new_slave = Node(request.id, request.ip, request.port)
        self.nodes2PC.append(new_slave)
        self.allNodes.append(new_slave)
        return store_pb2.Response(success=True)
    

    def canCommit(self, request, context):
        #time.sleep(self.delay)
        return store_pb2.Response(success=True)

    def doCommit(self, request, context):
        #time.sleep(self.delay)

        response = self.store.put(request.key, request.value)
        return store_pb2.Response(success=response)
    

    def requestVotes(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = list()
            for node in self.nodes2PC:
                stub = store_pb2_grpc.KeyValueStoreStub(grpc.insecure_channel(f'{node.node_ip}:{node.node_port}'))
                futures.append(executor.submit(stub.canCommit, store_pb2.CanCommitRequest(key='')))
            
            concurrent.futures.wait(futures)

            #transform futures list only with futures results
            futures = [future.result() for future in futures]
            
            #check if all results are successful
            if all(f.success for f in futures):
                return True
            else:
                return False

    def multicastCommit(self, key, value):
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = list()
            for node in self.nodes2PC:
                stub = store_pb2_grpc.KeyValueStoreStub(grpc.insecure_channel(f'{node.node_ip}:{node.node_port}'))
                futures.append(executor.submit(stub.doCommit, store_pb2.DoCommitRequest(key=key, value=value)))
            
            concurrent.futures.wait(futures)

            #transform futures list only with futures results
            futures = [future.result() for future in futures]
            
            #check if all results are successful
            if all(f.success for f in futures):
                return True
            else:
                return False
            
    def newMasterRequest(self, request, context):

        self.node_registration(request.ip, request.port)
        return store_pb2.Response(success=True)
            
    def imNewMaster(self):
        self.is_master = True
        
        for node in self.allNodes:
            try:
                stub = store_pb2_grpc.KeyValueStoreStub(grpc.insecure_channel(f'{node.node_ip}:{node.node_port}'))
                response = stub.newMasterRequest(store_pb2.NodeInfo(id=self.node_id, ip=self.ip, port=self.port))
            except Exception:
                pass
                
    
    def get(self, request, context):
        time.sleep(self.delay)
        found, value = self.store.get(request.key)
        return store_pb2.GetResponse(found=found, value=value)
    
    
    
    def put(self, request, context):
        #time.sleep(self.delay)
        response = store_pb2.PutResponse(success=False)

        if self.is_master:
            try:
                vote = self.requestVotes()

                if vote:
                    multicast_success = self.multicastCommit(request.key, request.value)
                else:
                    multicast_success = False
                
                response = store_pb2.PutResponse(success=multicast_success)
            except grpc.RpcError:
                
                for node in self.nodes2PC:
                    try:
                        stub = store_pb2_grpc.KeyValueStoreStub(grpc.insecure_channel(f'{node.node_ip}:{node.node_port}'))
                        ping = stub.ping(store_pb2.PingRequest())
                    except Exception:
                        self.nodes2PC.remove(node)
                
                response = store_pb2.PutResponse(success=False)
        else:

            try: 
                ping = self.master_stub.ping(store_pb2.PingRequest())
            except Exception:

                self.imNewMaster()

                vote = self.requestVotes()
                if vote:
                    multicast_success = self.multicastCommit(request.key, request.value)
                else:
                    multicast_success = False

                response = store_pb2.PutResponse(success=multicast_success)
            

        return response


    def slowDown(self, request, context):
        time.sleep(self.delay)
        self.delay = request.seconds
        print(f"SlowDown: {self.delay}")
        return store_pb2.SlowDownResponse(success=True)
    
    def restore(self, request, context):
        time.sleep(self.delay)
        self.delay = 0
        print(f"Restore: {self.delay}")
        return store_pb2.RestoreResponse(success=True)
        

        


