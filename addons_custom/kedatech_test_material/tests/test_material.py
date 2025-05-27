# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class TestKedatechMaterial(TransactionCase):

    def setUp(self):
        super(TestKedatechMaterial, self).setUp()
        self.Material = self.env['kedatech.material']
        self.company = self.env.company
        self.supplier = self.env['res.partner'].create({'name': 'Test Supplier'})
        _logger.info("Test setup complete: Supplier 'Test Supplier' created.")

    def test_create_material(self):
        """Test basic material creation with code generation"""
        _logger.info("Starting test_create_material...")
        material = self.Material.create({
            'name': 'Test Fabric',
            'material_type_kedatech': 'fabric_type',
            'material_price_kedatech': 150.0,
            'supplier_id_kedatech': self.supplier.id,
        })
        _logger.info(f"Material created: {material.name} with code {material.material_code_kedatech}")
        self.assertEqual(material.material_code_kedatech, 'FBC-TF-001')
        self.assertEqual(material.currency_id_kedatech, self.company.currency_id)
        _logger.info("test_create_material passed.")

    def test_material_code_generation(self):
        """Test various material code generation scenarios"""
        _logger.info("Starting test_material_code_generation...")
        test_cases = [
            ('jeans_type', 'Blue Jeans', 'JNS-BJ-002'),
            ('cotton_type', 'Egyptian Cotton', 'CTN-EC-003'),
            ('fabric_type', 'Silk', 'FBC-S-004'),
            (False, 'Test Material', 'UNK-TM-005'),
            ('invalid_type', '', 'UNK-UNK-006'),
        ]
        for idx, (mtype, name, expected) in enumerate(test_cases, start=2):
            with self.subTest(mtype=mtype, name=name):
                material = self.Material.create({
                    'name': name,
                    'material_type_kedatech': mtype,
                    'material_price_kedatech': 100 + idx*10,
                })
                _logger.info(f"Material created: {material.name} with code {material.material_code_kedatech}")
                self.assertEqual(material.material_code_kedatech, expected)
        _logger.info("test_material_code_generation passed.")

    def test_price_validation(self):
        """Test material price validation constraints"""
        _logger.info("Starting test_price_validation...")
        # Test valid price
        valid_material = self.Material.create({
            'name': 'Valid Material',
            'material_price_kedatech': 100.0,
        })
        _logger.info(f"Valid material created: {valid_material.name}")
        self.assertTrue(valid_material.id)

        # Test invalid price
        with self.assertRaises(ValidationError) as cm:
            self.Material.create({
                'name': 'Invalid Material',
                'material_price_kedatech': 99.99,
            })
        _logger.error(f"ValidationError raised: {cm.exception}")
        self.assertIn('must be at least 100', str(cm.exception))
        _logger.info("test_price_validation passed.")

    def test_default_currency(self):
        """Test automatic currency assignment"""
        _logger.info("Starting test_default_currency...")
        material = self.Material.create({
            'name': 'Currency Test',
            'material_price_kedatech': 200.0,
        })
        _logger.info(f"Material created: {material.name} with currency {material.currency_id_kedatech.name}")
        self.assertEqual(material.currency_id_kedatech, self.company.currency_id)
        _logger.info("test_default_currency passed.")

    def test_material_without_name(self):
        """Test material creation without name"""
        _logger.info("Starting test_material_without_name...")
        material = self.Material.create({
            'material_type_kedatech': 'cotton_type',
            'material_price_kedatech': 150.0,
        })
        _logger.info(f"Material created: {material.name} with code {material.material_code_kedatech}")
        self.assertTrue(material.material_code_kedatech.startswith('CTN-UNK-'))
        _logger.info("test_material_without_name passed.")

    def test_supplier_relationship(self):
        """Test supplier relationship functionality"""
        _logger.info("Starting test_supplier_relationship...")
        material = self.Material.create({
            'name': 'Supplier Test',
            'material_price_kedatech': 300.0,
            'supplier_id_kedatech': self.supplier.id,
        })
        _logger.info(f"Material created: {material.name} with supplier {material.supplier_id_kedatech.name}")
        self.assertEqual(material.supplier_id_kedatech.name, 'Test Supplier')
        _logger.info("test_supplier_relationship passed.")
