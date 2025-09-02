import xmlrpc.client
import os
from dotenv import load_dotenv

load_dotenv()

class OdooClient:
    def __init__(self):
        self.url = os.getenv("ODOO_URL")
        self.db = os.getenv("ODOO_DB")
        self.username = os.getenv("ODOO_USER")
        self.password = os.getenv("ODOO_PASSWORD")

        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.uid = self.common.authenticate(self.db, self.username, self.password, {})
        if not self.uid:
            raise Exception("Échec de l'authentification à Odoo.")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def call(self, model, method, *args, **kwargs):
        # Si args a au moins un élément et kwargs est vide
        if method == 'message_post' and args and not kwargs and isinstance(args[-1], dict):
            kwargs = args[-1]
            args = args[:-1]
        return self.models.execute_kw(self.db, self.uid, self.password, model, method, args, kwargs or {})
