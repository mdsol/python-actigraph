Actigraph client
================

A client for the [Actigraph](http://www.actigraphcorp.com/ "Actigraph") Study and Subject API

Usage
=====

You will need a secret and access keypair provided by Actigraph.

The client manages all the request signing.

The return from all getXXX calls from the client is a [request](http://docs.python-requests.org/en/latest/ "Request")
object.

The Actigraph system returns results as JSON so the .json() method of the resulting request object is the most
interesting.

Example:

    >>> from actigraph import ActigraphClient
    >>> ac = ActigraphClient("https://studyadmin-api.actigraphcorp.com", "access_key", "secret_key")
    >>> result = ac.getAllStudies()
    >>> result.json()
    [{u'DateCreated': u'2014-05-28T21:12:36Z', u'Id': 21, u'Name': u'Demo Study'}]
    >>> result.status_code
    200
    >>> result.request.url
    https://studyadmin-api.actigraphcorp.com/v1/studies


Installation / Requirements
===========================

Suggested:

```
    bash
    $ pip install actigraph
```

or

```bash
$ pip install git+git://github.com/mdsol/python-actigraph#egg=actigraph
```
