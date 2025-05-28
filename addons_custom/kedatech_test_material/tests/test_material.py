# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class TestKedatechMaterial(TransactionCase):
    def setUp(self):
        super(TestKedatechMaterial, self).setUp()
        _logger.info("Setting up TestKedatechMaterial test case...")
        # Create test supplier
        self.supplier = self.env['res.partner'].create({'name': 'Test Supplier'})
        _logger.info(f"Created test supplier with id {self.supplier.id} and name '{self.supplier.name}'")
        # Predefined valid material values
        self.material_vals = {
            'name': 'Test Material',
            'material_type_kedatech': 'fabric_type',
            'material_price_kedatech': 150.0,
            'supplier_id_kedatech': self.supplier.id,
        }
        _logger.info("Predefined material values set.")

    def test_material_creation(self):
        _logger.info("Starting test_material_creation...")
        material = self.env['kedatech.material'].create(self.material_vals)
        _logger.info(f"Created material with id {material.id} and name '{material.name}'")
        self.assertTrue(material, "Material should be created")
        self.assertEqual(material.name, "Test Material")
        self.assertEqual(material.supplier_id_kedatech, self.supplier)
        _logger.info("test_material_creation passed.")

    def test_material_code_generation(self):
        _logger.info("Starting test_material_code_generation...")
        material = self.env['kedatech.material'].create(self.material_vals)
        code_parts = material.material_code_kedatech.split('-')
        _logger.info(f"Material code generated: {material.material_code_kedatech}")
        self.assertEqual(len(code_parts), 3, "Code should have 3 components")
        self.assertEqual(code_parts[0], 'FBC', "Fabric type should map to FBC")
        self.assertEqual(code_parts[1], 'TM', "Name initials should be 'TM'")
        self.assertEqual(code_parts[2], str(material.id).zfill(3), "ID should be zero-padded")

        type_mapping = {
            'jeans_type': 'JNS',
            'cotton_type': 'CTN'
        }
        for mtype, expected_code in type_mapping.items():
            vals = self.material_vals.copy()
            vals['material_type_kedatech'] = mtype
            material = self.env['kedatech.material'].create(vals)
            _logger.info(f"Material created with type {mtype}, code: {material.material_code_kedatech}")
            self.assertEqual(material.material_code_kedatech.split('-')[0], expected_code)

        vals = self.material_vals.copy()
        vals['name'] = "Premium Cotton Blend"
        material = self.env['kedatech.material'].create(vals)
        initials = material.material_code_kedatech.split('-')[1]
        _logger.info(f"Material with multi-word name code initials: {initials}")
        self.assertEqual(initials, 'PCB')
        _logger.info("test_material_code_generation passed.")

    def test_missing_material_type_code_generation(self):
        _logger.info("Starting test_missing_material_type_code_generation...")
        vals = self.material_vals.copy()
        vals.pop('material_type_kedatech')
        material = self.env['kedatech.material'].create(vals)
        code_parts = material.material_code_kedatech.split('-')
        _logger.info(f"Material code with missing type: {material.material_code_kedatech}")
        self.assertEqual(code_parts[0], 'UNK', "Should use UNK for missing type")
        self.assertEqual(code_parts[1], 'TM', "Should still generate name initials")
        _logger.info("test_missing_material_type_code_generation passed.")

    def test_price_constraint(self):
        _logger.info("Starting test_price_constraint...")
        material = self.env['kedatech.material'].create(self.material_vals)
        _logger.info(f"Material created with valid price: {material.material_price_kedatech}")

        with self.assertRaises(ValidationError):
            invalid_vals = self.material_vals.copy()
            invalid_vals['material_price_kedatech'] = 99.0
            _logger.info(f"Attempting to create material with invalid price: {invalid_vals['material_price_kedatech']}")
            self.env['kedatech.material'].create(invalid_vals)

        material = self.env['kedatech.material'].create(self.material_vals)
        with self.assertRaises(ValidationError):
            _logger.info(f"Attempting to update material id {material.id} with invalid price 50.0")
            material.write({'material_price_kedatech': 50.0})
        _logger.info("test_price_constraint passed.")

    def test_required_fields(self):
        _logger.info("Starting test_required_fields...")

        with self.assertRaises(Exception):
            vals = self.material_vals.copy()
            vals.pop('name')
            _logger.info("Attempting to create material without name")
            self.env['kedatech.material'].create(vals)
            
        with self.assertRaises(Exception):
            vals = self.material_vals.copy()
            vals.pop('supplier_id_kedatech')
            _logger.info("Attempting to create material without supplier")
            self.env['kedatech.material'].create(vals)
            
        with self.assertRaises(Exception):
            vals = self.material_vals.copy()
            vals.pop('material_price_kedatech')
            _logger.info("Attempting to create material without price")
            self.env['kedatech.material'].create(vals)
        _logger.info("test_required_fields passed.")

    def test_currency_default(self):
        _logger.info("Starting test_currency_default...")
        material = self.env['kedatech.material'].create(self.material_vals)
        _logger.info(f"Material created with currency: {material.currency_id_kedatech.name}")
        self.assertEqual(
            material.currency_id_kedatech,
            self.env.company.currency_id,
            "Should default to company currency"
        )
        _logger.info("test_currency_default passed.")