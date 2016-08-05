class AmazonException(Exception):
    """
    Base Class for Amazon API Exceptions.
    """
    pass


class ASINNotFound(AmazonException):
    pass


class LookupException(AmazonException):
    pass


class SearchException(AmazonException):
    pass


class NoMorePages(SearchException):
    pass


class SimilarityLookupException(AmazonException):
    pass


class BrowseNodeLookupException(AmazonException):
    pass
