from . import connection_http


def connect(
    servers=None, timeout=None, retry_time=10, connection=None, *args, **kwargs
):
    """Construct an ElasticSearch connection."""
    if not connection:
        connection = connection_http.HTTPConnection()

    connection.connect(
        servers=servers, timeout=timeout,
        retry_time=retry_time, *args, **kwargs)

    return connection
