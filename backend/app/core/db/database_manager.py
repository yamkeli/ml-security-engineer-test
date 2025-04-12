from contextlib import contextmanager
import psycopg2
import psycopg2.pool
from fastapi import HTTPException
from typing import Generator, Optional


class DatabaseManager:

    _instance: Optional['DatabaseManager'] = None

    
    def __init__(
        self, 
        host: str, 
        user: str, 
        password: str, 
        database: str, 
        port: int = 5432,
        min_connections: int = 4, 
        max_connections: int = 64
    ):
        
        self.db_config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port
        }
        
        self.connection_pool = None
        self.min_connections = min_connections
        self.max_connections = max_connections

    # singleton method to make sure only one dbmg exist, returns it if exist, init if not
    @classmethod
    def get_instance(
        cls, 
        host: str = None, 
        user: str = None, 
        password: str = None, 
        database: str = None,
        port: int = 5432,
        min_connections: int = 4, 
        max_connections: int = 64
    ) -> 'DatabaseManager':

        if not cls._instance:
            if not all([host, user, password, database]):
                raise ValueError("All database configuration parameters are required for first instantiation")
            
            cls._instance = cls(
                host, 
                user, 
                password, 
                database, 
                port,
                min_connections, 
                max_connections
            )

            if not cls._instance.connection_pool:
                cls._instance._initialize_pool()

        return cls._instance


    # initialise the connection pool and put in class variable
    def _initialize_pool(self):
        if not self.connection_pool:
            try:
                self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=self.min_connections,
                    maxconn=self.max_connections,
                    **self.db_config
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Database connection pool initialization failed: {str(e)}"
                )


    # return connection back to the pool to be reused
    def _return_connection(self, conn):
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)

    def close_pool(self):

        if self.connection_pool:
            self.connection_pool.closeall()
            self.connection_pool = None
    
    # retrieve a connection from the pool
    def _get_connection(self):
        conn = None
        
        if not self.connection_pool:
            self._initialize_pool()
        
        try:
            conn = self.connection_pool.getconn()
            conn.autocommit = True
            return conn
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to get database connection: {str(e)}"
            )
    
    @contextmanager
    def _get_db_cursor(self):
        conn = None
        try:
            conn = self._get_connection()
            yield conn.cursor()
            # used in "with... as ...", escapes after yield

        finally:
            # after with block
            if conn:
                self._return_connection(conn)

    def execute_query(self, query: str, params: list, return_result: bool = True):
        with self._get_db_cursor() as db_cursor:
            db_cursor.execute(query, params)

            if return_result:
                result = db_cursor.fetchall()

                return result