from zope.interface import verify

from txes import connection_http
from txes import interfaces


def connect(
    servers=None, timeout=None, retryTime=10, connection=None, *args, **kwargs
):
    """Construct an ElasticSearch connection."""
    if not connection:
        connection = connection_http.HTTPConnection()

    verify.verifyObject(interfaces.IConnection, connection)
    connection.connect(
        servers=servers, timeout=timeout, retryTime=retryTime, *args, **kwargs)
    return connection
