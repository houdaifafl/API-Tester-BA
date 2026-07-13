import os
import re
import yaml
import pytest
from app import create_app

def convert_flask_path_to_openapi(path):
    # Converts Flask path variables like <type:name> or <name> to OpenAPI {name}
    return re.sub(r'<(?:[^:]+:)?([^>]+)>', r'{\1}', path)

class TestOpenAPIDrift:

    @pytest.fixture(scope="class")
    def openapi_spec(self):
        spec_path = os.path.join(os.path.dirname(__file__), '..', 'openapi.yaml')
        with open(spec_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture(scope="class")
    def flask_routes(self):
        app = create_app()
        routes = {}
        for rule in app.url_map.iter_rules():
            # Exclude internal / static / root diagnostic Flask routes
            if rule.endpoint == 'static' or rule.rule.startswith('/_') or rule.rule == '/':
                continue
            
            openapi_path = convert_flask_path_to_openapi(rule.rule)
            methods = {m.upper() for m in rule.methods if m.upper() not in ('OPTIONS', 'HEAD')}
            if methods:
                if openapi_path not in routes:
                    routes[openapi_path] = {
                        'methods': set(),
                        'arguments': set(rule.arguments)
                    }
                routes[openapi_path]['methods'].update(methods)
        return routes

    def test_all_flask_routes_are_documented(self, flask_routes, openapi_spec):
        openapi_paths = openapi_spec.get('paths', {})
        
        for flask_path, flask_info in flask_routes.items():
            # 1. Assert the path is documented in openapi.yaml
            assert flask_path in openapi_paths, (
                f"Route '{flask_path}' exists in the Flask application but is missing "
                f"from openapi.yaml. Please add it to the API documentation."
            )
            
            # 2. Assert all HTTP methods for this route are documented
            spec_methods = {m.upper() for m in openapi_paths[flask_path].keys()}
            for method in flask_info['methods']:
                assert method in spec_methods, (
                    f"HTTP method '{method}' is active on route '{flask_path}' in the code, "
                    f"but is not documented for that path in openapi.yaml."
                )

    def test_all_documented_routes_exist_in_flask(self, flask_routes, openapi_spec):
        openapi_paths = openapi_spec.get('paths', {})
        
        for spec_path, spec_operations in openapi_paths.items():
            # 1. Assert the documented path actually exists in the Flask app
            assert spec_path in flask_routes, (
                f"openapi.yaml documents route '{spec_path}' but it does not exist "
                f"in the Flask application. Please remove or update this dead documentation."
            )
            
            # 2. Assert documented HTTP methods actually exist in the code
            flask_methods = flask_routes[spec_path]['methods']
            for op_method in spec_operations.keys():
                # Ignore metadata fields like 'parameters' at the path level
                if op_method.upper() in ('PARAMETERS', 'SUMMARY', 'DESCRIPTION', 'SERVERS'): 
                    continue
                assert op_method.upper() in flask_methods, (
                    f"openapi.yaml documents '{op_method.upper()} {spec_path}' but that "
                    f"method is not allowed or registered in the Flask application."
                )

    def test_path_parameters_match(self, flask_routes, openapi_spec):
        openapi_paths = openapi_spec.get('paths', {})
        
        for flask_path, flask_info in flask_routes.items():
            if not flask_info['arguments']:
                continue
            
            spec_path_entry = openapi_paths.get(flask_path, {})
            
            # Retrieve path-level parameters
            path_params = []
            if 'parameters' in spec_path_entry:
                path_params = spec_path_entry['parameters']
            
            # Check parameter definitions across each operation method (GET, POST, etc.)
            for op_name, op_details in spec_path_entry.items():
                if op_name.upper() in ('PARAMETERS', 'SUMMARY', 'DESCRIPTION', 'SERVERS'):
                    continue
                if isinstance(op_details, dict) and 'parameters' in op_details:
                    path_params.extend(op_details['parameters'])
            
            # Extract names of path parameters documented in OpenAPI
            documented_param_names = {
                p['name'] for p in path_params if isinstance(p, dict) and p.get('in') == 'path'
            }
            
            # Assert all path arguments in the Flask route are documented
            for arg in flask_info['arguments']:
                assert arg in documented_param_names, (
                    f"Path parameter '{arg}' in route '{flask_path}' is missing "
                    f"its path parameter definition in openapi.yaml."
                )
