from odoo import http
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)

class KedatechMaterialController(http.Controller):

    @http.route('/api/materials', type='http', auth='user', methods=['GET'], csrf=False)
    def list_materials(self, **kwargs):
        try:
            domain = []
            if kwargs.get('type'):
                domain.append(('material_type_kedatech', '=', kwargs['type']))

            materials = request.env['kedatech.material'].sudo().search(domain)

            materials_data = []
            for material in materials:
                materials_data.append({
                    'id': material.id,
                    'code': material.material_code_kedatech,
                    'name': material.name,
                    'type': material.material_type_kedatech,
                    'price': material.material_price_kedatech,
                    'supplier': material.supplier_id_kedatech.name if material.supplier_id_kedatech else None,
                })

            return Response(json.dumps({
                'success': True,
                'count': len(materials_data),
                'data': materials_data
            }), status=200, mimetype='application/json')

        except Exception as e:
            _logger.exception("Failed to fetch materials: %s", str(e))
            return Response(json.dumps({
                'success': False,
                'error': str(e)
            }), status=500, mimetype='application/json')

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_material(self, material_id, **kwargs):
        try:
            material = request.env['kedatech.material'].sudo().browse(material_id)
            if not material.exists():
                return Response(json.dumps({
                    'success': False,
                    'error': 'Material not found'
                }), status=404, mimetype='application/json')

            data = {
                'id': material.id,
                'code': material.material_code_kedatech,
                'name': material.name,
                'type': material.material_type_kedatech,
                'price': material.material_price_kedatech,
                'supplier': material.supplier_id_kedatech.name if material.supplier_id_kedatech else None,
            }

            return Response(json.dumps({
                'success': True,
                'data': data
            }), status=200, mimetype='application/json')

        except Exception as e:
            _logger.exception("Failed to get material %s: %s", material_id, str(e))
            return Response(json.dumps({
                'success': False,
                'error': str(e)
            }), status=500, mimetype='application/json')

    @http.route('/api/materials', type='http', auth='user', methods=['POST'], csrf=False)
    def create_material(self, **kwargs):
        try:
            try:
                request_data = json.loads(request.httprequest.data)
            except ValueError:
                return Response(json.dumps({
                    'success': False,
                    'error': 'Invalid JSON body'
                }), status=400, mimetype='application/json')

            required_fields = ['name', 'type', 'price']
            for field in required_fields:
                if field not in request_data:
                    return Response(json.dumps({
                        'success': False,
                        'error': f"Missing required field: {field}"
                    }), status=400, mimetype='application/json')

            vals = {
                'name': request_data['name'],
                'material_type_kedatech': request_data['type'],
                'material_price_kedatech': float(request_data['price']),
                'supplier_id_kedatech': request_data.get('supplier_id')
            }

            material = request.env['kedatech.material'].sudo().create(vals)
            return Response(json.dumps({
                'success': True,
                'material_id': material.id
            }), status=201, mimetype='application/json')

        except Exception as e:
            _logger.exception("Failed to create material: %s", str(e))
            return Response(json.dumps({
                'success': False,
                'error': str(e)
            }), status=500, mimetype='application/json')

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['PUT'], csrf=False)
    def update_material(self, material_id, **kwargs):
        try:
            material = request.env['kedatech.material'].sudo().browse(material_id)
            if not material.exists():
                return Response(json.dumps({
                    'success': False,
                    'error': 'Material not found'
                }), status=404, mimetype='application/json')

            try:
                request_data = json.loads(request.httprequest.data)
            except ValueError:
                return Response(json.dumps({
                    'success': False,
                    'error': 'Invalid JSON data'
                }), status=400, mimetype='application/json')

            update_vals = {}
            if 'name' in request_data:
                update_vals['name'] = request_data['name']
            if 'type' in request_data:
                update_vals['material_type_kedatech'] = request_data['type']
            if 'price' in request_data:
                try:
                    update_vals['material_price_kedatech'] = float(request_data['price'])
                except ValueError:
                    return Response(json.dumps({
                        'success': False,
                        'error': 'Price must be a number'
                    }), status=400, mimetype='application/json')
            if 'supplier_id' in request_data:
                update_vals['supplier_id_kedatech'] = request_data['supplier_id']

            material.write(update_vals)

            return Response(json.dumps({
                'success': True,
                'message': 'Material updated successfully',
                'material_id': material.id
            }), status=200, mimetype='application/json')

        except Exception as e:
            _logger.exception("Failed to update material %s: %s", material_id, str(e))
            return Response(json.dumps({
                'success': False,
                'error': str(e)
            }), status=500, mimetype='application/json')

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_material(self, material_id, **kwargs):
        try:
            material = request.env['kedatech.material'].sudo().browse(material_id)
            if not material.exists():
                return Response(json.dumps({
                    'success': False,
                    'error': 'Material not found'
                }), status=404, mimetype='application/json')

            material.unlink()

            return Response(json.dumps({
                'success': True,
                'message': 'Material deleted successfully'
            }), status=200, mimetype='application/json')

        except Exception as e:
            _logger.exception("Failed to delete material %s: %s", material_id, str(e))
            return Response(json.dumps({
                'success': False,
                'error': str(e)
            }), status=500, mimetype='application/json')