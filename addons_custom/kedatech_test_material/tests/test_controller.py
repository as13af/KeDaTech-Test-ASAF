# -*- coding: utf-8 -*-
from http import HTTPStatus
from odoo.tests.common import HttpCase, tagged
import json
import logging
import requests

_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class TestKedatechMaterialController(HttpCase):

    def setUp(self):
        super().setUp()
        _logger.info("Setting up test data for KedatechMaterialController tests.")

        self.authenticate('admin', 'admin')

        self.supplier = self.env['res.partner'].create({'name': 'Test Supplier'})

        _logger.info("Test data setup complete.")

    def test_material_crud_flow(self):
        # 1. Create material
        create_response = self.url_open(
            '/api/materials',
            data=json.dumps({
                'name': 'Test Material',
                'type': 'fabric_type',
                'price': 200,
                'supplier_id': self.supplier.id,
            }),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(create_response.status_code, HTTPStatus.CREATED)
        material_id = json.loads(create_response.text)['material_id']

        # 2. Get material by ID
        get_response = self.url_open(f'/api/materials/{material_id}')
        self.assertEqual(get_response.status_code, HTTPStatus.OK)
        material_data = json.loads(get_response.text)['data']
        self.assertEqual(material_data['name'], 'Test Material')

        # 3. Update material
        update_response = self.url_open(
            f'/api/materials/{material_id}',
            data=json.dumps({'price': 250}),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(update_response.status_code, HTTPStatus.OK)
        updated_info = json.loads(update_response.text)
        self.assertEqual(updated_info['message'], 'Material updated successfully')

        # 4. List materials
        list_response = self.url_open('/api/materials')
        self.assertEqual(list_response.status_code, HTTPStatus.OK)
        materials = json.loads(list_response.text)['data']
        self.assertTrue(any(m['id'] == material_id for m in materials))

        # 5. Delete material - requires using the werkzeug client directly
        delete_response = self.opener.delete(
            f'{self.base_url()}/api/materials/{material_id}',
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(delete_response.status_code, HTTPStatus.OK)
        self.assertIn('deleted', json.loads(delete_response.text)['message'].lower())

        # 6. Confirm deletion
        confirm_delete = self.url_open(f'/api/materials/{material_id}')
        self.assertEqual(confirm_delete.status_code, HTTPStatus.NOT_FOUND)

