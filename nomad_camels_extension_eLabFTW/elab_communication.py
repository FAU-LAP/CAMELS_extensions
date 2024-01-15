import elabapi_python as elabapi

configuration = elabapi.Configuration()
test_key = '2-bfa1f693b02ea88f4cb23d9b059ec85fe66c8686f7eeb61ce4dc49073f0a758ca2dcfb4094f61a9603812'
configuration.api_key['api_key'] = test_key
configuration.api_key_prefix['api_key'] = 'Authorization'
configuration.debug = False
configuration.verify_ssl = False
configuration.host = 'https://demo.elabftw.net/api/v2'

api_client = elabapi.ApiClient(configuration)
api_client.set_default_header(header_name='Authorization', header_value=test_key)
items = elabapi.ItemsApi(api_client)
print(items.read_items())

token = ''
url = ''


def login_to_elab(parent=None):
	global url, token
	

