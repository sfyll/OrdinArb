import requests
import json
import os
from os.path import dirname, join
import atexit
from networking.ssh_tunnel_handler import sshHandler


class BitcoinRpc:
    def __init__(self, host: str = '127.0.0.1', port: int = 8332):
        self.load_env_vars()
        self.host = host
        self.port = port
        self.url = f'http://{host}:{port}/'
        self.headers = {'content-type': 'application/json'}
        self.ssh_tunnel = sshHandler()
        self.ssh_tunnel.create_tunnel()
        atexit.register(self.ssh_tunnel.kill_tunnel)

    def load_env_vars(self):
        script_dir = dirname(__file__)
        env_file = join(script_dir, '.env')
        print(f"Loading environment variables from: {env_file}")

        with open(env_file, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

        self.rpc_user = os.getenv('RPCUSER')
        self.rpc_pass = os.getenv('RPCPASSWORD')

    def call(self, method: str, params: list = []):
        payload = json.dumps({
            "jsonrpc": "1.0",
            "id": "python-bitcoinrpc",
            "method": method,
            "params": params
        })

        # Set the headers to 'text/plain'
        headers = {'content-type': 'text/plain'}

        # Prepare the request to send, this does not actually send the request
        request = requests.Request('POST', self.url, data=payload, auth=(
            self.rpc_user, self.rpc_pass), headers=headers)
        prepared = request.prepare()

        # Print the prepared request details
        print("Prepared request details:")
        print(f"Method: {prepared.method}")
        print(f"URL: {prepared.url}")
        print(f"Headers: {prepared.headers}")
        print(f"Body: {prepared.body}")

        try:
            # Send the request
            with requests.Session() as session:
                response = session.send(prepared)
                # Raises an HTTPError if the HTTP request returned an unsuccessful status code
                response.raise_for_status()
                return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")

    def get_block_count(self):
        return self.call("getblockcount")


# Example usage:
if __name__ == "__main__":
    bitcoin_rpc = BitcoinRpc()
    print("Block count:", bitcoin_rpc.get_block_count())
