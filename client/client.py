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
    
    while True:
        print("\nCRUD User Management")
        print("1. Create User")
        print("2. Get User")
        print("3. Update User")
        print("4. Delete User")
        print("5. List Users")
        print("0. Exit")
        
        choice = input("Enter your choice: ")
        
        try:
            if choice == '1':
                # Create user
                name = input("Enter name: ")
                email = input("Enter email: ")
                phone = input("Enter phone: ")
                
                # Call the CreateUser RPC
                response = stub.CreateUser(crud_pb2.CreateUserRequest(
                    name=name,
                    email=email,
                    phone=phone
                ))
                
                print(f"User created successfully with ID: {response.user.id}")
                
            elif choice == '2':
                # Get user
                user_id = int(input("Enter user ID: "))
                
                try:
                    # Call the GetUser RPC
                    response = stub.GetUser(crud_pb2.GetUserRequest(id=user_id))
                    print(f"User details:")
                    print(f"ID: {response.user.id}")
                    print(f"Name: {response.user.name}")
                    print(f"Email: {response.user.email}")
                    print(f"Phone: {response.user.phone}")
                except grpc.RpcError as e:
                    print(f"Error: {e.details()}")
                
            elif choice == '3':
                # Update user
                user_id = int(input("Enter user ID: "))
                
                try:
                    # First get the current user details
                    current_user = stub.GetUser(crud_pb2.GetUserRequest(id=user_id)).user
                    
                    # Get new values, with current values as defaults
                    name = input(f"Enter name [{current_user.name}]: ") or current_user.name
                    email = input(f"Enter email [{current_user.email}]: ") or current_user.email
                    phone = input(f"Enter phone [{current_user.phone}]: ") or current_user.phone
                    
                    # Call the UpdateUser RPC
                    response = stub.UpdateUser(crud_pb2.UpdateUserRequest(
                        id=user_id,
                        name=name,
                        email=email,
                        phone=phone
                    ))
                    
                    print(f"User updated successfully:")
                    print(f"ID: {response.user.id}")
                    print(f"Name: {response.user.name}")
                    print(f"Email: {response.user.email}")
                    print(f"Phone: {response.user.phone}")
                except grpc.RpcError as e:
                    print(f"Error: {e.details()}")
                
            elif choice == '4':
                # Delete user
                user_id = int(input("Enter user ID: "))
                
                try:
                    # Call the DeleteUser RPC
                    response = stub.DeleteUser(crud_pb2.DeleteUserRequest(id=user_id))
                    
                    if response.success:
                        print(f"User with ID {user_id} deleted successfully")
                    else:
                        print(f"Failed to delete user with ID {user_id}")
                except grpc.RpcError as e:
                    print(f"Error: {e.details()}")
                
            elif choice == '5':
                # List users
                page = input("Enter page number (default 1): ") or 1
                size = input("Enter page size (default 10): ") or 10
                
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
                
            elif choice == '0':
                # Exit the application
                print("Exiting application")
                break
                
            else:
                print("Invalid choice. Please try again.")
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    try:
        # Give the server a moment to start up
        import time
        print("Waiting for server to start...")
        time.sleep(3)
        
        print("Starting CRUD client...")
        run_client()
    except KeyboardInterrupt:
        print("Client stopped by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)