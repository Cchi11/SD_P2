# Distributed storage systems and the CAP theorem

```
Project/
│
├── proto/
│   ├── store.proto
│   ├── store_pb2.py
│   ├── store_pb2_grpc.py
│
├── centralized_config.yaml
├── decentralized_config.yaml
├── centralized.py
├── decentralized.py
├── eval/
│   ├── test_centralized_system.py
│   ├── test_decentralized_system.py
│
├── binary_dict.pickle
├── requirements.txt
├── store_service.py
├── test_centralized.py
├── README.md
├── .vscode/
│   └── settings.json
└── __pycache__/
    ├── store_pb2_grpc.cpython-312.pyc
    ├── store_pb2.cpython-312.pyc
    ├── centralized_node.cpython-312.pyc
    └── decentralized_node.cpython-312.pyc
```

## Directory Structure Explanation

- **proto/**: Contains Protocol Buffer files used for defining gRPC services and messages. Generated Python files (`store_pb2.py` and `store_pb2_grpc.py`) based on `store.proto` should be stored here.

- **centralized_config.yaml and decentralized_config.yaml**: YAML configuration files containing settings for the centralized and decentralized systems.

    - ***Centralized Format***: 

    ```yaml
    master:
      ip: <IP>
      port: <Port>

    slaves:
      - id: <slave_1_ID>
        ip: <slave_1_IP>
        port: <slave_1_Port>
      - id: <slave_2_ID>
        ip: <slave_2_IP>
        port: <slave_2_Port>
      ...
    ```

    - ***Decentralized Format***: 

    ```yaml
    nodes:
      - id: <node_1_ID>
        ip: <node_1_IP>
        port: <node_1_Port>
      - id: <node_2_ID>
        ip: <node_2_IP>
        port: <node_2_Port>
      ...
    ```

- **eval/**: Directory containing evaluation scripts and tests.

  - **test_centralized_system.py**: Script containing unit tests for the centralized system.
  
  - **test_decentralized_system.py**: Script containing unit tests for the decentralized system.

Each component of the project is organized into its respective directory, facilitating clear separation of concerns and ease of navigation. The `eval` directory specifically houses test scripts for evaluating the functionality and correctness of the implemented systems.

## Brief description

This project involves the creation of distributed key-value storage systems using Python and gRPC. There are two types of implementations:

Centralized (centralized.py): This system features a master node that coordinates the entire system and several slave nodes that store data. The master node manages data replication and fault tolerance. It uses a two-phase commit (2PC) protocol to ensure consistency between the slave nodes.

Decentralized (decentralized.py): This system does not have a master node. Instead, all nodes coordinate using consensus algorithms to achieve fault tolerance and data consistency. Each node can handle client requests, and quorum-based methods are used to ensure data integrity and replication.

The project demonstrates the principles of distributed storage systems, including fault tolerance, scalability, and data consistency, by implementing simplified versions of centralized and decentralized architectures.

## Run

To run the distributed system, follow these steps:

1. Execute the `centralized.py` or `decentralized.py` file, which act as servers, and leave them running in the background.
2. Use another Python file to create a client that interacts with the server.

These steps will ensure the distributed system operates correctly, whether in centralized or decentralized mode.
