from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError
import logging


_logger = logging.getLogger(__name__)

class KedatechMaterial(models.Model):
    _name = 'kedatech.material'
    _description = 'Material'

    name = fields.Char(string="Material Name", required=True)
    material_code_kedatech = fields.Char(string="Material Code")
    material_type_kedatech = fields.Selection([
        ('fabric_type', 'Fabric'),
        ('jeans_type', 'Jeans'),
        ('cotton_type', 'Cotton')
    ], string="Material Type", required=True)
    material_price_kedatech = fields.Float(string="Material Buy Price", required=True)
    currency_id_kedatech = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True
    )
    supplier_id_kedatech = fields.Many2one('res.partner', string="Related Supplier", required=True)

    @api.constrains('material_price_kedatech')
    def _check_material_price(self):
        for record in self:
            if record.material_price_kedatech < 100:
                _logger.error(f"Validation error: material price {record.material_price_kedatech} is less than 100.")
                raise ValidationError('Material Buy Price must be at least 100.')

    @api.model
    def create(self, vals):
        _logger.info(f"Creating KedatechMaterial with values: {vals}")
        record = super(KedatechMaterial, self).create(vals)

        material_type = vals.get('material_type_kedatech')
        material_name = vals.get('name')

        # Mapping selection values to abbreviations
        type_mapping = {
            'fabric_type': 'FBC',
            'jeans_type': 'JNS',
            'cotton_type': 'CTN'
        }

        if material_type and material_name:
            type_code = type_mapping.get(material_type, 'UNK')
            name_code = ''.join(word[0] for word in material_name.split()).upper()
            record_id = str(record.id).zfill(3)

            material_code = f"{type_code}-{name_code}-{record_id}"
            _logger.info(f"Generated material code: {material_code}")
            record.material_code_kedatech = material_code
        else:
            material_code = f"UNK-UNK-{str(record.id).zfill(3)}"
            _logger.warning(f"Material type or name missing. Set material code as: {material_code}")
            record.material_code_kedatech = material_code

        return record