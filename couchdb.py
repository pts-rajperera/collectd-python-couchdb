import collectd
import requests
import json
import numbers


def _type(key, subkey):
    if key == 'httpd_request_methods':
        return "http_request_methods"
    elif key == 'httpd_status_codes':
        return "http_response_codes"
    elif subkey.endswith("requests"):
        return"http_requests"
    else:
        return "gauge"


def configure_callback(configuration, conf):
    collectd.debug("CouchDB plugin configure callback")
    for node in conf.children:
        if node.key.lower() == 'url':
            configuration['url'] = node.values[0].rstrip("/")
        else:
            raise RuntimeError("Unknown configuration key %s" % node.key)

def read_callback(configuration):
    r = requests.get(configuration['url'] + "/_stats")
    for key, data in r.json().iteritems():
        for subkey, metrics in data.iteritems():
            for m_type, value in metrics.iteritems():
                if isinstance(value, numbers.Number):
                    val = collectd.Values(plugin='couchdb', type=_type(key, subkey))
                    val.plugin_instance = key + "_" + subkey
                    val.type_instance = m_type
                    val.values = [value]
                    val.dispatch()

# register callbacks
configuration = {}
collectd.register_config(lambda conf: configure_callback(configuration, conf))
collectd.register_read(read_callback, 10, configuration)
