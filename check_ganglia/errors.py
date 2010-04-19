class ApplicationError (Exception):
    '''Base class for all exceptions raised by check_gmond.'''
    pass
class UsageError (ApplicationError):
    '''Raised if mandatory arguments are not provided.'''
    pass
class NoSuchHost (ApplicationError):
    '''Raised if hostname looks fail.'''
    pass
class NoSuchMetric (ApplicationError):
    '''Raised if the given metric cannot be found.'''
    pass
class ConnectionError (ApplicationError):
    '''Raised if there are socket errors.'''
    pass


