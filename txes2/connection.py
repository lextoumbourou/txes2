from zope.interface import verify

from . import connection_http
from . import interfaces


def connect(
    servers=None, timeout=None, retry_time=10, connection=None, *args, **kwargs
):
    """Construct an ElasticSearch connection."""
    if not connection:
        connection = connection_http.HTTPConnection()

    verify.verifyObject(interfaces.IConnection, connection)
    connection.connect(
        servers=servers, timeout=timeout,
        retry_time=retry_time, *args, **kwargs)
    return connection
