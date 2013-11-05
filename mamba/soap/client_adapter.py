from zope.interface import Interface


class ClientAdapter(Interface):

	def set_headers(headers):
		pass

	def send_request(method_name, params):
		pass

	def get_last_request():
		pass

	def get_last_response():
		pass