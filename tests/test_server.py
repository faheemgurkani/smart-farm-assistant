import sys
import os

# Adding the project root (the directory containing 'src' and 'scripts') to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

import grpc
import generated.farm_pb2 as farm_pb2
import generated.farm_pb2_grpc as farm_pb2_grpc

def test_grpc_request():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = farm_pb2_grpc.FarmingStub(channel)

        req = farm_pb2.FarmRequest(
            text="What should I do after harvesting rice?",
            image=b"",
            audio=""
        )

        response = stub.Analyze(req)
        print("Advice:", response.advice)
        print("Audio bytes returned:", len(response.audio))

test_grpc_request()
