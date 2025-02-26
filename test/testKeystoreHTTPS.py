#!/usr/bin/env python
import docker
import os
import unittest
from utils import DockerUtil

"""
SCENARIO - downloading Connect keystore
    Verify keystore download over HTTPS, self-signed cert fails
"""
class DockerTestsKeystoreHTTPS(unittest.TestCase):
    docker_image = ""
    container = ""
    test_yml = os.path.join('.','tmp','keystore-https.yml')
    composeCmd = 'docker-compose -f '+ test_yml +' -p mctest_keystore_https'
    max_wait_time = 120

    @classmethod
    def setUpClass(cls):
        print(' \n >>>> ==== Running Test Keystore - Verify Compose with keystore download HTTPS' + ' ===== ') 
        print( ' >>>> ==== using IMAGE = ' + cls.docker_image + ' ===== ')
        DockerUtil.empty_test_folder("tmp")

        # Setup test dir as volume to by mounted by container
        if os.name == 'nt':
            DockerUtil.create_test_dir("tmp")
            os.system('xcopy /E /I /Y .\\testdata\\web .\\tmp\\web')
        else:
            DockerUtil.create_test_dir("tmp")
            os.system('cp -r ./testdata/web ./tmp/web')
        DockerUtil.generate_compose_yml(cls.test_yml, cls.docker_image, 'keystore-https.yml')
        
        # Run docker compose
        os.system(cls.composeCmd + " up -d")
        client = docker.from_env()
        cls.container = client.containers.get("mctest_keystore_https_mc_1")

    def test_keystore_http(self):
        # HTTPS but not allowing insecure

        # expect to find downloading keystore message
        # expect to find SSL cert problem
        try:
            DockerUtil.wait_for_log_message([self.container], "Downloading keystore at", self.max_wait_time)
            DockerUtil.wait_for_log_message([self.container], "SSL certificate problem: self signed certificate", self.max_wait_time)
        except Exception as e:
            self.fail(e)

        # expect Connect to not start
        with self.assertRaises(Exception) as e:
            DockerUtil.wait_for_containers([self.container], self.max_wait_time)

    @classmethod
    def tearDownClass(cls):
        # clean up at the end of the test
        os.system(cls.composeCmd + " down")
        DockerUtil.empty_test_folder("tmp")
