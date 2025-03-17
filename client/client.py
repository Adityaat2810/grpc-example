# client.py
import grpc
import logging
import sys

# Import the generated protocol buffer code
import crud_pb2
import crud_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO)

def run_client():
    """Run the gRPC client with a simple command-line interface"""
    # Create a channel to the server
    channel = grpc.insecure_channel('server:50051')
    
    # Create a stub (client)
    stub = crud_pb2_grpc.CrudServiceStub(channel)
    
      

    page =  1
    size = 10
    
    try:
        # Convert inputs to integers
        page = int(page)
        size = int(size)
        
        # Call the ListUsers RPC
        response = stub.ListUsers(crud_pb2.ListUsersRequest(
            page=page,
            size=size
        ))
        
        print(f"Total users: {response.total}")
        print(f"Users (page {page}, showing {len(response.users)} of {response.total}):")
        
        for user in response.users:
            print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}, Phone: {user.phone}")
        
    except grpc.RpcError as e:
        print(f"Error: {e.details()}")
    except ValueError:
        print("Please enter valid numbers for page and size")
            

if __name__ == '__main__':
    run_client()
   