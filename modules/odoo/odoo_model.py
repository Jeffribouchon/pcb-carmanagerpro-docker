# https://www.odoo.com/documentation/18.0/fr/developer/reference/external_api.html

class OdooModel:
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name

    def _build_options(self, fields=None, limit=None, offset=None, order=None):
        """Construit dynamiquement le dict des options pour les appels Odoo."""
        options = {}
        if fields:
            options['fields'] = fields
        if limit:
            options['limit'] = limit
        if offset:
            options['offset'] = offset
        if order:
            options['order'] = order
        return options
        
    def search(self, domain):
        return self.client.call(self.model_name, "search", domain)

    def search_count(self, domain):
        return self.client.call(self.model_name, "search_count", domain)
        
    def read(self, ids, fields=None):
        options = self._build_options(fields=fields, limit=limit, offset=offset, order=order)
        return self.client.call(self.model_name, "read", ids, fields or [], **options)

    def search_read(self, domain, fields=None, limit=None, offset=None, order=None):
        options = self._build_options(fields=fields, limit=limit, offset=offset, order=order)
        return self.client.call(self.model_name, "search_read", domain, fields or [], **options)
       
    def create(self, data):
        return self.client.call(self.model_name, "create", [data])

    def write(self, ids, values):
        return self.client.call(self.model_name, "write", [ids] if isinstance(ids, int) else ids, values)

    def unlink(self, ids):
        return self.client.call(self.model_name, "unlink", [ids] if isinstance(ids, int) else ids)

    def active(self, ids, active=True):
        return self.write(ids, {'active': active})

    def upsert(self, domain, data):
        ids = self.search(domain)
        if ids:
            self.write(ids, data)
            return ids[0]
        else:
            return self.create(data)

    # ⚡ Ajout spécifique pour poster un message
    def message_post(self, ids, body, message_type="notification", subtype_xmlid="mail.mt_note"):
        return self.client.call(
            self.model_name,
            "message_post",
            [ids] if isinstance(ids, int) else ids, 
            {
                "body": body,
                "message_type": message_type,
                "subtype_xmlid": subtype_xmlid
            }
        )

# fields_get()
# models.execute_kw(db, uid, password, 'res.partner', 'fields_get', [], {'attributes': ['string', 'help', 'type']})
