# server.py
import grpc
import time
from concurrent import futures
import logging

# Import the generated protocol buffer code
import crud_pb2
import crud_pb2_grpc

# Import database functions
from database import get_db_connection, UserModel

# Configure logging
logging.basicConfig(level=logging.INFO)

class CrudServiceServicer(crud_pb2_grpc.CrudServiceServicer):
    """Implementation of the CrudService service"""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    def CreateUser(self, request, context):
        """Create a new user in the database"""
        logging.info(f"Creating user with name: {request.name}, email: {request.email}")
        
        # Create a new session
        session = self.session_factory()
        try:
            # Create a new user model instance
            user = UserModel(
                name=request.name,
                email=request.email,
                phone=request.phone
            )
            
            # Add to session and commit to database
            session.add(user)
            session.commit()
            
            # Refresh to get the id assigned by the database
            session.refresh(user)
            
            # Create the response
            response = crud_pb2.CreateUserResponse(
                user=crud_pb2.User(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    phone=user.phone
                )
            )
            
            return response
        except Exception as e:
            # Rollback in case of error
            session.rollback()
            logging.error(f"Error creating user: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating user: {str(e)}")
            return crud_pb2.CreateUserResponse()
        finally:
            # Always close the session
            session.close()
    
    def GetUser(self, request, context):
        """Get a user by ID from the database"""
        logging.info(f"Getting user with ID: {request.id}")
        
        session = self.session_factory()
        try:
            # Query the user by ID
            user = session.query(UserModel).filter(UserModel.id == request.id).first()
            
            if user is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return crud_pb2.GetUserResponse()
            
            # Create the response
            return crud_pb2.GetUserResponse(
                user=crud_pb2.User(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    phone=user.phone
                )
            )
        except Exception as e:
            logging.error(f"Error getting user: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting user: {str(e)}")
            return crud_pb2.GetUserResponse()
        finally:
            session.close()
    
    def UpdateUser(self, request, context):
        """Update an existing user in the database"""
        logging.info(f"Updating user with ID: {request.id}")
        
        session = self.session_factory()
        try:
            # Query the user by ID
            user = session.query(UserModel).filter(UserModel.id == request.id).first()
            
            if user is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return crud_pb2.UpdateUserResponse()
            
            # Update user attributes
            user.name = request.name
            user.email = request.email
            user.phone = request.phone
            
            # Commit changes to database
            session.commit()
            
            # Create the response
            return crud_pb2.UpdateUserResponse(
                user=crud_pb2.User(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    phone=user.phone
                )
            )
        except Exception as e:
            session.rollback()
            logging.error(f"Error updating user: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating user: {str(e)}")
            return crud_pb2.UpdateUserResponse()
        finally:
            session.close()
    
    def DeleteUser(self, request, context):
        """Delete a user from the database"""
        logging.info(f"Deleting user with ID: {request.id}")
        
        session = self.session_factory()
        try:
            # Query the user by ID
            user = session.query(UserModel).filter(UserModel.id == request.id).first()
            
            if user is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return crud_pb2.DeleteUserResponse(success=False)
            
            # Delete the user
            session.delete(user)
            session.commit()
            
            # Create the response
            return crud_pb2.DeleteUserResponse(success=True)
        except Exception as e:
            session.rollback()
            logging.error(f"Error deleting user: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error deleting user: {str(e)}")
            return crud_pb2.DeleteUserResponse(success=False)
        finally:
            session.close()
    
    def ListUsers(self, request, context):
        """List all users from the database with optional pagination"""
        page = max(1, request.page) if request.page else 1
        size = max(1, request.size) if request.size else 10
        offset = (page - 1) * size
        
        logging.info(f"Listing users with page: {page}, size: {size}")
        
        session = self.session_factory()
        try:
            # Count total users
            total = session.query(UserModel).count()
            
            # Query users with pagination
            users = session.query(UserModel).offset(offset).limit(size).all()
            
            # Create the response
            response = crud_pb2.ListUsersResponse(total=total)
            
            # Add each user to the response
            for user in users:
                user_proto = crud_pb2.User(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    phone=user.phone
                )
                response.users.append(user_proto)
            
            return response
        except Exception as e:
            logging.error(f"Error listing users: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error listing users: {str(e)}")
            return crud_pb2.ListUsersResponse()
        finally:
            session.close()

def serve():
    """Start the gRPC server"""
    # Get database connection and session factory
    _, session_factory = get_db_connection()
    
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add the servicer to the server
    crud_pb2_grpc.add_CrudServiceServicer_to_server(
        CrudServiceServicer(session_factory), server
    )
    
    # Listen on port 50051
    server.add_insecure_port('[::]:50051')
    server.start()
    
    logging.info("Server started on port 50051")
    
    try:
        # Keep the server running until interrupted
        while True:
            time.sleep(86400)  # Sleep for a day
    except KeyboardInterrupt:
        server.stop(0)
        logging.info("Server stopped")

if __name__ == '__main__':
    serve()