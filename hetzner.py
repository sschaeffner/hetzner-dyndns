import subprocess

class HetznerIp:
    url = "https://ip.hetzner.com"

    def get_ip4(self):
        process = subprocess.run(["curl", "-4", self.url], capture_output=True)
        process.check_returncode()
        return process.stdout.decode("utf-8").strip()

    def get_ip6(self):
        process = subprocess.run(["curl", "-6", self.url], capture_output=True)
        process.check_returncode()
        return process.stdout.decode("utf-8").strip()
