from odoo import http
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)

class KedatechMaterialController(http.Controller):

    @http.route('/api/materials', type='json', auth='user', methods=['GET'], csrf=False)
    def get_all_materials(self, **kwargs):
        material_type = kwargs.get('material_type')
        domain = []
        if material_type:
            domain.append(('material_type_kedatech', '=', material_type))
        materials = request.env['kedatech.material'].sudo().search(domain)
        result = []
        for material in materials:
            result.append({
                'id': material.id,
                'material_code_kedatech': material.material_code_kedatech,
                'name': material.name,
                'material_type_kedatech': material.material_type_kedatech,
                'material_price_kedatech': material.material_price_kedatech,
                'currency_id_kedatech': material.currency_id_kedatech.name if material.currency_id_kedatech else None,
                'supplier_id_kedatech': material.supplier_id_kedatech.name if material.supplier_id_kedatech else None,
            })
        return result


    @http.route('/api/materials/<int:material_id>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_material_by_id(self, material_id, **kwargs):
        material = request.env['kedatech.material'].sudo().browse(material_id)
        if not material.exists():
            return {'error': 'Material not found'}
        return {
            'id': material.id,
            'material_code_kedatech': material.material_code_kedatech,
            'name': material.name,
            'material_type_kedatech': material.material_type_kedatech,
            'material_price_kedatech': material.material_price_kedatech,
            'currency_id_kedatech': material.currency_id_kedatech.name if material.currency_id_kedatech else None,
            'supplier_id_kedatech': material.supplier_id_kedatech.name if material.supplier_id_kedatech else None,
        }

    @http.route('/api/materials', type='json', auth='user', methods=['POST'], csrf=False)
    def create_material(self, **kwargs):
        try:
            vals = {
                'name': kwargs.get('name'),
                'material_type_kedatech': kwargs.get('material_type_kedatech'),
                'material_price_kedatech': kwargs.get('material_price_kedatech'),
                'currency_id_kedatech': kwargs.get('currency_id_kedatech'),
                'supplier_id_kedatech': kwargs.get('supplier_id_kedatech'),
            }
            material = request.env['kedatech.material'].sudo().create(vals)
            return {'success': True, 'material_id': material.id}
        except Exception as e:
            _logger.exception("Error creating material: %s", e)
            return {'error': str(e)}

    @http.route('/api/materials/<int:material_id>', type='json', auth='user', methods=['PUT'], csrf=False)
    def update_material(self, material_id, **kwargs):
        material = request.env['kedatech.material'].sudo().browse(material_id)
        if not material.exists():
            return {'error': 'Material not found'}
        try:
            material.write({
                'name': kwargs.get('name', material.name),
                'material_type_kedatech': kwargs.get('material_type_kedatech', material.material_type_kedatech),
                'material_price_kedatech': kwargs.get('material_price_kedatech', material.material_price_kedatech),
                'currency_id_kedatech': kwargs.get('currency_id_kedatech', material.currency_id_kedatech.id),
                'supplier_id_kedatech': kwargs.get('supplier_id_kedatech', material.supplier_id_kedatech.id),
            })
            return {'success': True}
        except Exception as e:
            _logger.exception("Error updating material: %s", e)
            return {'error': str(e)}

    @http.route('/api/materials/<int:material_id>', type='json', auth='user', methods=['DELETE'], csrf=False)
    def delete_material(self, material_id, **kwargs):
        material = request.env['kedatech.material'].sudo().browse(material_id)
        if not material.exists():
            return {'error': 'Material not found'}
        try:
            material.unlink()
            return {'success': True}
        except Exception as e:
            _logger.exception("Error deleting material: %s", e)
            return {'error': str(e)}
