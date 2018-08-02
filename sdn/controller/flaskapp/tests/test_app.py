import unittest
import json
from ..app import app, ServerError, _assert_proper_request, controller
from unittest.mock import patch, MagicMock

from sdn.controller.container import Container


class Req(object):
    def __init__(self):
        self.content_type = 'application/json'
        self.json = {}


class TestControllerFlaskaap(unittest.TestCase):
    ROUTER_URL = "10.0.0.1"
    ROUTER_ID = "router-id"
    CONTAINER_RED_URL = "10.0.0.2"
    CONTAINER_RED_ID = "red-id"
    CONTAINER_GREEN_URL = "10.0.0.3"
    CONTAINER_GREEN_ID = "green-id"

    def setUp(self):
        controller.add_logical_port = MagicMock(return_value=1)
        self.client = app.test_client()

    def test_hello(self):
        """Start with a blank database."""
        rv = self.client.get('/hello')
        self.assertEqual(b'hello', rv.data)
        self.assertEqual(200, rv.status_code)

    def test_assert_proper_request(self):
        req = Req()
        _assert_proper_request(req)

    def test_assert_proper_request_wrong_content_type(self):
        req = Req()
        req.content_type = 'wrong_content_type'
        with self.assertRaises(ServerError) as context:
            _assert_proper_request(req)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.message, 'Malformed request, expected json payload and type')
        self.assertIsNone(context.exception.payload)

    def test_assert_proper_request_without_json(self):
        req = Req()
        del req.json
        with self.assertRaises(ServerError) as context:
            _assert_proper_request(req)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.message, 'Malformed request, expected json payload and type')
        self.assertIsNone(context.exception.payload)

    def test_get_index(self):
        rv = self.client.get('/')
        self.assertTrue(b'Available endpoints:' in rv.data)
        self.assertEqual(200, rv.status_code)
        rv = self.client.get('/index')
        self.assertTrue(b'Available endpoints:' in rv.data)
        self.assertEqual(200, rv.status_code)

    def test_force_clean(self):
        rv = self.client.post('/force_clean')
        self.assertEqual(b'Success\n', rv.data)
        self.assertEqual(200, rv.status_code)

    def test_create_network(self):
        with patch.object(controller, 'add_network') as mock:
            data = {
                'name': 'ala',
                'cidr': '192.168.0.0/24'
            }
            rv = self.client.post('/create/network', data=json.dumps(data),
                                  content_type='application/json')
            self.assertEqual(b'Success\n', rv.data)
            self.assertEqual(200, rv.status_code)

    def test_create_network_fail(self):
        with patch.object(controller, 'add_network') as mock:
            data = {
                'name': 'ala'
            }
            rv = self.client.post('/create/network', data=json.dumps(data),
                                  content_type='application/json')
            self.assertEqual(500, rv.status_code)
            data = json.loads(rv.data.decode('utf-8'))
            self.assertTrue('Internal server error creating network' in data['message'])

    @patch.object(Container, 'start')
    def test_start_container(self, mock):
        data = {
            'id': 'ala',
        }
        rv = self.client.post('/create/container', data=json.dumps(data),
                              content_type='application/json')
        self.assertEqual(b'Success\n', rv.data)
        self.assertEqual(200, rv.status_code)

    @patch.object(Container, 'stop')
    def test_start_container(self, mock):
        data = {
            'id': 'ala',
        }
        rv = self.client.post('/delete/container', data=json.dumps(data),
                              content_type='application/json')
        self.assertEqual(b'Success\n', rv.data)
        self.assertEqual(200, rv.status_code)

    @patch.object(controller, 'add_logical_port')
    @patch.object(controller, 'get_network')
    @patch.object(controller, 'add_network')
    def test_create_logical_port(self, mock, mock2, mock3):
        data_net = {
            'name': 'ala',
            'cidr': '192.168.0.0/24'
        }
        self.client.post('/create/network', data=json.dumps(data_net),
                              content_type='applicatilogical_porton/json')
        data = {
            'net_id': 'ala',
            'container':
                {'id': 'kot',
                 'ip': '192.168.0.77'}
        }
        rv = self.client.post('/create/logical_port', data=json.dumps(data),
                              content_type='application/json')
        self.assertEqual(b'Success\n', rv.data)
        self.assertEqual(200, rv.status_code)

    @patch.object(controller, 'add_logical_port')
    @patch.object(controller, 'get_network')
    @patch.object(controller, 'add_network')
    def test_create_logical_port_fail(self,  mock, mock2, mock3):
        with patch.object(controller, 'add_logical_port') as mock:

            data_net = {
                'name': 'ala',
                'cidr': '192.168.0.0/24'
            }
            self.client.post('/create/network', data=json.dumps(data_net),
                                  content_type='application/json')
            data = {
                'net_id': 'ala',
                'container':
                    {'id': 'kot'}
            }
            rv = self.client.post('/create/logical_port', data=json.dumps(data),
                                  content_type='application/json')
            self.assertEqual(500, rv.status_code)
            data = json.loads(rv.data.decode('utf-8'))
            self.assertTrue('Internal server error creating logical port' in data['message'])