import network
import time

class WiFi:

    def __init__(self, ssid, password, max_wait_s=10, retries=2, retry_timeout_s=5):
        self.ssid = ssid
        self.password = password
        self.max_wait_s = max_wait_s
        self.retries = retries
        self.retry_timeout_s = retry_timeout_s
        self.wlan = network.WLAN(network.STA_IF)


    def connect(self):
        print('WiFi#connect')
        print('  ssid = ', self.ssid)
        print('  password = ', self.password)
        print('  max_wait_s = ', self.max_wait_s)
        print('  retries = ', self.retries)
        print('  retry_timeout_s = ', self.retry_timeout_s)

        self.wlan.active(True)

        retry_count = 0
        while retry_count <= self.retries:
            if retry_count > 0:
                print('   retrying (', retry_count, ')')
                time.sleep(self.retry_timeout_s)

            self.do_connect()
            self.wait_for_status()

            if self.is_status_ok():
                ip_address = self.wlan.ifconfig()[0]
                print('   ok: ip = ', ip_address)
                return ip_address
            else:
                print('   error: status = ', self.wlan.status())
                retry_count += 1

        return None


    def do_connect(self):
        self.wlan.connect(self.ssid, self.password)


    def wait_for_status(self):
        wait_count = 0

        while wait_count <= self.max_wait_s:
            if wait_count > 0:
                print('   waiting for connection (', wait_count, ')')
                time.sleep(1)

            status = self.wlan.status()
            print('   status = ', status)

            if status < 0 or status >= 3:
                break

            wait_count += 1


    def is_status_ok(self):
        return self.wlan.status() == 3


    def disconnect(self):
        print('WiFi#disconnect')
        self.wlan.disconnect()
        self.wlan.active(False)
        self.wlan.deinit()
