# Stolen from pyes convert_errors and exceptions


class NoServerAvailable(Exception):
    pass


class InvalidQuery(Exception):
    pass


class InvalidParameterQuery(InvalidQuery):
    pass


class QueryError(Exception):
    pass


class QueryParameterError(Exception):
    pass


class ScriptFieldsError(Exception):
    pass


class ElasticSearchException(Exception):
    """
    Base class of exceptions raised as a result of parsing an error return
    from ElasticSearch.

    An exception of this class will be raised if no more specific subclass
    is appropriate.
    """
    def __init__(self, error, status=None, additional_info=None):
        super(ElasticSearchException, self).__init__(error)
        self.status = status
        self.additional_info = additional_info


class NotFoundException(ElasticSearchException):
    pass


class AlreadyExistsException(ElasticSearchException):
    pass


class RequestException(ElasticSearchException):
    pass


class ConflictException(ElasticSearchException):
    pass


class AuthenticationException(ElasticSearchException):
    pass


class AuthorizationException(ElasticSearchException):
    pass


exception_patterns_trailing = {
    '] missing': NotFoundException,
    '] Already exists': AlreadyExistsException,
}


# generic mappings from status_code to python exceptions
HTTP_EXCEPTIONS = {
    400: RequestException,
    401: AuthenticationException,
    403: AuthorizationException,
    404: NotFoundException,
    409: ConflictException,
}


def raise_exceptions(status, result):
    """
    Raise an exception if the result is an error ( status > 400 )
    """
    status = int(status)

    if status < 400:
        return

    if status == 404 and isinstance(result, dict):
        raise NotFoundException("Item not found", status, result)

    if not isinstance(result, dict) or "error" not in result:
        raise ElasticSearchException("Unknown exception type",
                                     status, result)
    error_message = result
    additional_info = None

    try:
        additional_info = result
        error_message = additional_info.get('error', error_message)
        if isinstance(error_message, dict) and 'type' in error_message:
            error_message = error_message['type']
    except (ValueError, TypeError, AttributeError):
        pass

    raise HTTP_EXCEPTIONS.get(
        status, ElasticSearchException)(
            error_message, status, additional_info)
