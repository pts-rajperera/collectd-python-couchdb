# Collectd CouchDB plugin

This is a Collectd plugin to monitor CouchDB instances.

The plugin depends on python support in Collectd and the python `requests` module.

## Usage

Place the following config in `/etc/collectd/plugins/python.conf` and drop `couchdb.py` in `/etc/collectd/python`:

```
LoadPlugin python
<Plugin python>
  ModulePath "/etc/collectd/python"
  LogTraces true
  Interactive false
  Import "couchdb"
  <Module couchdb>
    url "http://localhost:5984/"
  </Module>
</Plugin>
```


This plugin was written for a workshop hosted as part of [StatsCraft](http://www.statscraft.org.il) monitoring conference.

## License

Do whatever the fuck you like public license :-)