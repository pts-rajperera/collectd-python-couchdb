import collectd
import requests
import numbers

DB_METRICS = ('data_size', 'doc_count', 'doc_del_count', 'disk_size')


def _type(key, subkey):
    if key == 'httpd_request_methods':
        return "http_request_methods"
    elif key == 'httpd_status_codes':
        return "http_response_codes"
    elif subkey.endswith("requests"):
        return "http_requests"
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
    for interval in (0, 60, 300, 900):
        r = requests.get("{}/_stats?range={}".format(configuration['url'], interval))
        for key, data in r.json().iteritems():
            for subkey, metrics in data.iteritems():
                for m_type, value in metrics.iteritems():
                    if isinstance(value, numbers.Number):
                        val = collectd.Values(plugin='couchdb', type=_type(key, subkey))
                        val.plugin_instance = "{}_{}".format(key, subkey)
                        val.type_instance = "{}_{}".format(m_type, interval)
                        val.values = [value]
                        val.dispatch()
    dbs = set(requests.get("{}/_all_dbs".format(configuration['url'])).json())
    for db in dbs ^ set(['_replicator', '_users']):
        metrics = requests.get("{}/{}".format(configuration['url'], db)).json()
        for metric in DB_METRICS:
            if metric in metrics:
                val = collectd.Values(plugin='couchdb', type="gauge", plugin_instance='db_stats')
                val.values = [metrics[metric]]
                val.type_instance = metric
                val.dispatch()


# register callbacks
configuration = {}
collectd.register_config(lambda conf: configure_callback(configuration, conf))
collectd.register_read(read_callback, 10, configuration)
