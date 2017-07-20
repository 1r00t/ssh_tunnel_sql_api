from flask import Flask, abort
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from queries import QUERIES
from sshtunnel import SSHTunnelForwarder


DB_USER = ""
DB_PASS = ""

SSH_USER = ""
SSH_PASS = ""

SSH_ADDR, SSH_PORT = ("255.255.255.255", 22)
REMOTE_ADDR, REMOTE_PORT = ("255.255.255.255", 1500)

tunnel = {"ssh_address_or_host": (SSH_ADDR, SSH_PORT),
          "ssh_username": SSH_USER,
          "ssh_password": SSH_PASS,
          "remote_bind_address": (REMOTE_ADDR, REMOTE_PORT)}

sql_con_str = 'oracle://{user}:{pw}@localhost:{port}/oracle'

app = Flask(__name__)
api = Api(app)


class Queries(Resource):
    def get(self, query_num):
        try:
            query = QUERIES[query_num]
        except KeyError:
            abort(404)
            return

        with SSHTunnelForwarder(**tunnel) as server:
            engine = create_engine(
                sql_con_str.format(user=DB_USER,
                                   pw=DB_PASS,
                                   port=server.local_bind_port)
            )
            conn = engine.connect()
            query = conn.execute(query)
            result = {"data": [[str(cell) for cell in row] for row in query]}
            conn.close()
            return result


api.add_resource(Queries, "/<string:query_num>")


if __name__ == "__main__":
    app.run()
