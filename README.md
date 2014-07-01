# Actigraph client

An Actigraph Authorizer for the [requests](http://docs.python-requests.org/en/latest/ "Requests") python HTTP library
including a client that wraps the calls for the [Actigraph](http://www.actigraphcorp.com/ "Actigraph") Study and Subject API.

## Usage

You will need a secret and access keypair provided by Actigraph.

The ActigraphAuth authorized manages all the request signing and can be used with the requests library:

    >>> import requests
    >>> from actigraph import ActigraphAuth
    >>> auth = ActigraphAuth("https://studyadmin-api.actigraphcorp.com", "access_key", "secret_key")
    >>> requests.get("https://studyadmin-api.actigraphcorp.com/v1/studies", auth=auth, verify=False)
    <Response [200]>

Note that verify=False is required for SSL because the (valid) root cert used to sign the Actigraph certificate is not in
requests' cache of root certs.

You can also use the ActigraphClient class which is a wrapper around the Actigraph URL's:

    >>> from actigraph import ActigraphClient
    >>> ac = ActigraphClient("https://studyadmin-api.actigraphcorp.com", "access_key", "secret_key")
    >>> result = ac.get_all_studies()
    >>> result.json()
    [{u'DateCreated': u'2014-05-28T21:12:36Z', u'Id': 21, u'Name': u'Demo Study'}]
    >>> result.status_code
    200
    >>> result.request.url
    https://studyadmin-api.actigraphcorp.com/v1/studies

The return from all getXXX calls from the client is a [request](http://docs.python-requests.org/en/latest/ "Request")
object.

The Actigraph system returns results as JSON so the .json() method of the resulting request object is the most
interesting.


## Installation 

Suggested:

```
    bash
    $ pip install actigraph
```

or

```bash
$ pip install git+git://github.com/mdsol/python-actigraph#egg=actigraph
```

## Dependencies

* requests

