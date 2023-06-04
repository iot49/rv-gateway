import unittest
import requests

import app

# !cp -a $IOT_PROJECTS/micropython-lib/python-ecosys/urequests/urequests.py $IOT_PROJECTS/code/lib/requests.py

class TestHttpd(unittest.TestCase):

    def test_http_routes(self):
        if False:
            base_url = f'http://{app.wifi.ip()}'
            print(f" RUN on other machine! base_url = {base_url} ", end="")
            time_url = base_url + '/time'
            config_url = base_url + '/config'
            backup_url = config_url + '/backup'
            backups_url = config_url + '/backups'

        if False:
            # THIS DEADLOCKS!

            # get current config
            config = requests.get(config_url).json()

            # create backup
            requests.get(backup_url).json()

            # verify backup equals current
            name = requests.get(backups_url).json()[-1]
            backup_config = requests.get(backups_url + '/' + name).json()
            self.assertEqual(backup_config, config)

            # delete newly created backup


            n = len(requests.get(backups_url).json())
            requests.delete(backups_url + '/' + name)
            self.assertEqual(len(requests.get(backups_url).json()), n-1)

            # upload new config
            dummy_config = {
                'app': {
                    'wifi': {
                        'ssid': 'TPA', 
                        'pwd': 'TurbenThal'
                    }, 
                    'hostname': 'rv.local'
                }, 
            }
            requests.post(config_url, json=dummy_config)
            self.assertEqual(requests.get(config_url).json(), dummy_config)
            name = requests.get(backups_url).json()[-1]
            self.assertEqual(requests.get(backups_url + '/' + name).json(), config)

            # revert to prior state
            requests.delete(backups_url + '/' + name)
            requests.post(config_url, json=config)
            self.assertEqual(requests.get(config_url).json(), config)

if __name__ == '__main__':
    unittest.main()