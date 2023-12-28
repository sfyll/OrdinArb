import subprocess
import psutil


class sshHandler:
    def __init__(self, host: str = "ordinArb", port_number: int = 8332):
        self.host = host
        self.port_number = port_number

    def find_ssh_tunnel_process(self):
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] == "ssh":
                cmdline = proc.info['cmdline']
                print(f"{cmdline=}")
                if ["-N", "-L", f"{self.port_number}:localhost:{self.port_number}", self.host] == cmdline[1:]:
                    return proc
        return None

    # Function to create the SSH tunnel
    def create_tunnel(self):
        ssh_command = [
            "ssh",
            "-N",
            "-L", f"{self.port_number}:localhost:{self.port_number}",
            self.host
        ]

        if self.find_ssh_tunnel_process() is None:
            try:
                subprocess.Popen(ssh_command)
                print("SSH tunnel established.")
            except Exception as e:
                print(f"Error establishing SSH tunnel: {e}")
        else:
            print("SSH tunnel is already running.")

    # Function to kill the SSH tunnel
    def kill_tunnel(self):
        process = self.find_ssh_tunnel_process()
        if process is not None:
            process.terminate()
            print("SSH tunnel terminated.")
        else:
            print("No SSH tunnel was running.")

# Main code to handle user input
if __name__ == "__main__":
    action = input("Do you want to 'create' or 'kill' the SSH tunnel? ").strip().lower()
    executor = sshHandler()
    if action == 'create':
        executor.create_tunnel()
    elif action == 'kill':
        executor.kill_tunnel()
    else:
        print("Invalid action. Use 'create' or 'kill'.")

