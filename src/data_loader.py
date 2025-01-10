import pandas as pd
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder
import urllib.parse
from sqlalchemy import text


class DatabaseConnection:
    def __init__(self, ssh_host, ssh_port, ssh_user,
                 db_host, db_port, db_user, db_password, db_name,
                 ssh_password=None, ssh_pkey=None):
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_pkey = ssh_pkey
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.tunnel = None
        self.engine = None

    def start_tunnel(self):
        if self.ssh_password is not None:
            self.tunnel = SSHTunnelForwarder(
                (self.ssh_host, self.ssh_port),
                ssh_username=self.ssh_user,
                ssh_password=self.ssh_password,
                remote_bind_address=(self.db_host, self.db_port)
            )
        elif self.ssh_pkey is not None:
            self.tunnel = SSHTunnelForwarder(
                (self.ssh_host, self.ssh_port),
                ssh_username=self.ssh_user,
                ssh_pkey=self.ssh_pkey,
                remote_bind_address=(self.db_host, self.db_port)
            )

        self.tunnel.start()
        local_port = self.tunnel.local_bind_port
        db_password_encoded = urllib.parse.quote_plus(self.db_password)
        self.engine = create_engine(f'mysql+pymysql://{self.db_user}:{db_password_encoded}@127.0.0.1:{local_port}/{self.db_name}')
        print(f"SSHトンネルが {local_port} にバインドされました。")

    def execute_query(self, query):
        if self.engine is None:
            raise Exception("SSHトンネルが開始されていません。")
        return pd.read_sql_query(query, self.engine)

    def execute_write_query(self, query):
        if self.engine is None:
            raise Exception("SSHトンネルが開始されていません。")
        connection = self.engine.connect()
        connection.execute(text(query))
        connection.commit()
        connection.close()

    def close_tunnel(self):
        if self.tunnel is not None:
            self.tunnel.close()
        print("SSHトンネルを閉じました。")