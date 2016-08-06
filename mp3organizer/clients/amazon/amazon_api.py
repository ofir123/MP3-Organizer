import time
import urllib.request
import urllib.parse
import hmac
import gzip
from base64 import b64encode
from hashlib import sha256
from itertools import islice

from lxml import objectify, etree
import logbook

from .amazon_exceptions import NoMorePages, SearchException, LookupException, ASINNotFound

REGION = 'com'
SERVICE_DOMAIN = 'ecs.amazonaws.com'
VERSION = '2013-08-01'
DEFAULT_TIMEOUT = 20

logger = logbook.Logger('AmazonClient')


class AmazonAPI(object):
    """
    An API for querying the Amazon Web Service.
    """

    def __init__(self, access_key, secret_key, associate_tag, timeout=DEFAULT_TIMEOUT):
        """
        Initialize the Amazon API Proxy.

        :param access_key: The AWS authentication key.
        :param secret_key: The AWS authentication secret.
        :param associate_tag: The AWS associate tag.
        :param timeout: The timeout (in seconds) for the request.
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.timeout = timeout

    def _call(self, operation, **kwargs):
        """
        Send a request for the Amazon Web Service, and parse the result.

        :param operation: The operation to perform.
        :param kwargs: Every given parameter is sent with the request.
        :return: The response text.
        """
        kwargs['Timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        kwargs['Operation'] = operation
        kwargs['AWSAccessKeyId'] = self.access_key
        kwargs['AssociateTag'] = self.associate_tag
        kwargs['Service'] = 'AWSECommerceService'
        kwargs['Version'] = VERSION

        quoted_strings = '&'.join('{}={}'.format(k, urllib.parse.quote(
            str(kwargs[k]).encode('UTF-8'), safe='~')) for k in sorted(kwargs.keys()))
        data = 'GET\n{}\n/onca/xml\n{}'.format(SERVICE_DOMAIN, quoted_strings)

        digest = hmac.new(self.secret_key.encode('UTF-8'), data.encode('UTF-8'), sha256).digest()
        signature = urllib.parse.quote(b64encode(digest))

        api_string = 'http://{}/onca/xml?{}&Signature={}'.format(SERVICE_DOMAIN, quoted_strings, signature)
        logger.debug('Connecting to: {}'.format(api_string))
        api_request = urllib.request.Request(api_string, headers={'Accept-Encoding': 'gzip'})

        response = urllib.request.urlopen(api_request, timeout=self.timeout)

        if 'gzip' in response.info().get('Content-Encoding'):
            response_text = gzip.decompress(response.read())
        else:
            response_text = response.read()
        return response_text

    def _query(self, response_group='Large', **kwargs):
        """
        Search products in Amazon according to the given keywords.

        :param response_group: The amount of information to ask for.
        :return: An lxml root element.
        """
        response = self._call('ItemSearch', ResponseGroup=response_group, **kwargs)
        root = objectify.fromstring(response)
        if root.Items.Request.IsValid == 'False':
            code = root.Items.Request.Errors.Error.Code
            msg = root.Items.Request.Errors.Error.Message
            if code == 'AWS.ParameterOutOfRange':
                raise NoMorePages(msg)
            else:
                raise SearchException('Amazon Search Error: "{}", "{}"'.format(code, msg))
        return root

    def get_item(self, item_id, response_group='Large', **kwargs):
        """
        Find a specific Amazon product, according to the given item ID.

        :param item_id: The item ID to look for.
        :param response_group: The amount of information to ask for.
        :return: An instance of :class:`~.AmazonProduct` if one item was returned,
        or a list of  :class:`~.AmazonProduct` instances if multiple items where returned.
        """
        response = self._call('ItemLookup', ItemId=item_id, ResponseGroup=response_group, **kwargs)
        root = objectify.fromstring(response)
        if root.Items.Request.IsValid == 'False':
            code = root.Items.Request.Errors.Error.Code
            msg = root.Items.Request.Errors.Error.Message
            raise LookupException('Amazon Product Lookup Error: "{}", "{}"'.format(code, msg))
        if not hasattr(root.Items, 'Item'):
            raise ASINNotFound('ASIN(s) not found: "{}"'.format(etree.tostring(root, pretty_print=True)))
        if len(root.Items.Item) > 1:
            return [AmazonProduct(item, self) for item in root.Items.Item]
        else:
            return AmazonProduct(root.Items.Item, self)

    def search_items(self, **kwargs):
        """
        Search the Amazon databases for an item.

        :return: An :class:`~.AmazonSearch` iterable.
        """
        return AmazonSearch(self, **kwargs)

    def search_items_limited(self, limit, **kwargs):
        """
        Search and return first N results.

        :param limit: The number of results to return.
        :return: A list of :class:`~.AmazonProduct`.
        """
        items = AmazonSearch(self, **kwargs)
        return list(islice(items, limit))


class AmazonSearch(object):
    """
    A class providing an iterable over amazon search results.
    """

    def __init__(self, api, **kwargs):
        """
        Initialize a search.

        :param api: An instance of :class:`~.AmazonAPI`.
        """
        self.kwargs = kwargs
        self.current_page = 1
        self.api = api

    def __iter__(self):
        """
        A generator which iterates over all paginated results.

        :return: Yields a :class:`~.AmazonProduct` for each result item.
        """
        for page in self.iterate_pages():
            for item in getattr(page.Items, 'Item', []):
                yield AmazonProduct(item, self.api)

    def iterate_pages(self):
        """
        A generator which iterates over all pages.
        Keep in mind that Amazon limits the number of pages it makes available.

        :return: Yields lxml root elements.
        """
        try:
            while True:
                yield self.api._query(ItemPage=self.current_page, **self.kwargs)
                self.current_page += 1
        except NoMorePages:
            pass


class AmazonProduct(object):
    """
    A wrapper class for an Amazon product.
    """

    def __init__(self, item, api):
        """
        Initialize an Amazon Product Proxy.

        :param item: The item to work with.
        """
        self.item = item
        self.api = api
        self.parent = None
        self.region = REGION

    def to_string(self):
        """
        Convert product XML to string.

        :return: A string representation of the item XML.
        """
        return etree.tostring(self.item, pretty_print=True)

    def _safe_get_element(self, path, root=None):
        """
        Get a child element of root (multiple levels deep).
        Will fail silently if any descendant does not exist.

        :param root: The root element to work with.
        :param path: The element's path.
        :return: The request element or None.
        """
        elements = path.split('.')
        parent = root if root is not None else self.item
        for element in elements[:-1]:
            parent = getattr(parent, element, None)
            if parent is None:
                return None
        return getattr(parent, elements[-1], None)

    def _safe_get_element_text(self, path, root=None):
        """
        Get the element as a string.

        :param root: The root element to work with.
        :param path: The element's path.
        :return: The request element as a string or None.
        """
        element = self._safe_get_element(path, root)
        if element:
            return element.text
        else:
            return None

    def _safe_get_element_date(self, path, root=None):
        """
        Get the element as a date.

        :param root: The root element to work with.
        :param path: The element's path.
        :return: The request element as a datetime.date or None.
        """
        value = self._safe_get_element_text(path=path, root=root)
        if value is not None:
            try:
                value = time.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                value = None

        return value

    @property
    def price_and_currency(self):
        """
        Return price according to the following process:
        * If product has a sale return Sales Price, otherwise,
        * Return Price, otherwise,
        * Return lowest offer price, otherwise,
        * Return None.

        :return: A tuple containing the price (in float) and the ISO currency code.
        """
        price = self._safe_get_element_text(
            'Offers.Offer.OfferListing.SalePrice.Amount')
        if price:
            currency = self._safe_get_element_text(
                'Offers.Offer.OfferListing.SalePrice.CurrencyCode')
        else:
            price = self._safe_get_element_text(
                'Offers.Offer.OfferListing.Price.Amount')
            if price:
                currency = self._safe_get_element_text(
                    'Offers.Offer.OfferListing.Price.CurrencyCode')
            else:
                price = self._safe_get_element_text(
                    'OfferSummary.LowestNewPrice.Amount')
                currency = self._safe_get_element_text(
                    'OfferSummary.LowestNewPrice.CurrencyCode')
        if price:
            return float(price) / 100, currency
        else:
            return None, None

    @property
    def asin(self):
        """
        The Amazon ID.
        """
        return self._safe_get_element_text('ASIN')

    @property
    def authors(self):
        """
        The list of authors.
        """
        result = []
        authors = self._safe_get_element('ItemAttributes.Author') or []
        for author in authors:
            result.append(author.text)
        return result

    @property
    def publisher(self):
        """
        The product's publisher.
        """
        return self._safe_get_element_text('ItemAttributes.Publisher')

    @property
    def label(self):
        """
        The product's label.
        """
        return self._safe_get_element_text('ItemAttributes.Label')

    @property
    def manufacturer(self):
        """
        The product's manufacturer.
        """
        return self._safe_get_element_text('ItemAttributes.Manufacturer')

    @property
    def brand(self):
        """
        The product's brand.
        """
        return self._safe_get_element_text('ItemAttributes.Brand')

    @property
    def isbn(self):
        """
        The product's ISBN.
        """
        return self._safe_get_element_text('ItemAttributes.ISBN')

    @property
    def eisbn(self):
        """
        The product's ISBN, if it's an EBOOK.
        """
        return self._safe_get_element_text('ItemAttributes.EISBN')

    @property
    def binding(self):
        """
        The product's binding.
        """
        return self._safe_get_element_text('ItemAttributes.Binding')

    @property
    def pages(self):
        """
        The product's pages.
        """
        return self._safe_get_element_text('ItemAttributes.NumberOfPages')

    @property
    def publication_date(self):
        """
        The product's publication date.
        """
        return self._safe_get_element_date('ItemAttributes.PublicationDate')

    @property
    def release_date(self):
        """
        The product's release date.
        """
        return self._safe_get_element_date('ItemAttributes.ReleaseDate')

    @property
    def edition(self):
        """
        The product's edition.
        """
        return self._safe_get_element_text('ItemAttributes.Edition')

    @property
    def large_image_url(self):
        """
        The product's large image URL.
        """
        return self._safe_get_element_text('LargeImage.URL')

    @property
    def medium_image_url(self):
        """
        The product's medium image URL.
        """
        return self._safe_get_element_text('MediumImage.URL')

    @property
    def small_image_url(self):
        """
        The product's small image URL.
        """
        return self._safe_get_element_text('SmallImage.URL')

    @property
    def tiny_image_url(self):
        """
        The product's tiny image URL.
        """
        return self._safe_get_element_text('TinyImage.URL')

    @property
    def reviews(self):
        """
        The URL for customer reviews.

        :return: A tuple of: has_reviews (bool), reviews url (string).
        """
        i_frame = self._safe_get_element_text('CustomerReviews.IFrameURL')
        has_reviews = self._safe_get_element_text('CustomerReviews.HasReviews')
        if has_reviews and has_reviews == 'true':
            has_reviews = True
        else:
            has_reviews = False
        return has_reviews, i_frame

    @property
    def ean(self):
        """
        The product's EAN.
        """
        ean = self._safe_get_element_text('ItemAttributes.EAN')
        if ean is None:
            ean_list = self._safe_get_element_text('ItemAttributes.EANList')
            if ean_list:
                ean = self._safe_get_element_text(
                    'EANListElement', root=ean_list[0])
        return ean

    @property
    def upc(self):
        """
        The product's UPC.
        """
        upc = self._safe_get_element_text('ItemAttributes.UPC')
        if upc is None:
            upc_list = self._safe_get_element_text('ItemAttributes.UPCList')
            if upc_list:
                upc = self._safe_get_element_text(
                    'UPCListElement', root=upc_list[0])
        return upc

    @property
    def sku(self):
        """
        The product's SKU.
        """
        return self._safe_get_element_text('ItemAttributes.SKU')

    @property
    def mpn(self):
        """
        The product's MPN.
        """
        return self._safe_get_element_text('ItemAttributes.MPN')

    @property
    def model(self):
        """
        The product's model name.
        """
        return self._safe_get_element_text('ItemAttributes.Model')

    @property
    def part_number(self):
        """
        The product's part number.
        """
        return self._safe_get_element_text('ItemAttributes.PartNumber')

    @property
    def title(self):
        """
        The product's title.
        """
        return self._safe_get_element_text('ItemAttributes.Title')

    @property
    def editorial_review(self):
        """
        The product's editorial review text.
        """
        return self._safe_get_element_text('EditorialReviews.EditorialReview.Content')

    @property
    def features(self):
        """
        A list of feature descriptions.

        :return: Returns a list of 'ItemAttributes.Feature' elements (strings).
        """
        result = []
        features = self._safe_get_element('ItemAttributes.Feature') or []
        for feature in features:
            result.append(feature.text)
        return result

    @property
    def list_price(self):
        """
        The product's list price.

        :return: A tuple containing the price (in float) and the ISO currency code.
        """
        price = self._safe_get_element_text('ItemAttributes.ListPrice.Amount')
        currency = self._safe_get_element_text('ItemAttributes.ListPrice.CurrencyCode')
        if price:
            return price / 100, currency
        else:
            return None, None

    def get_attribute(self, name):
        """
        Get an attribute (child elements of 'ItemAttributes') value.

        :param name: The attribute name.
        :return: The attribute value or None if not found.
        """
        return self._safe_get_element_text('ItemAttributes.{}'.format(name))

    def get_attribute_details(self, name):
        """
        Gets XML attributes of the product attribute. These usually contain
        details about the product attributes such as units.

        :param name: The attribute name.
        :return: A name/value dictionary of the details.
        """
        return self._safe_get_element('ItemAttributes.{}'.format(name)).attrib

    def get_attributes(self, name_list):
        """
        Get a list of attributes as a name/value dictionary.

        :param name_list: A list of attribute names.
        :return: A name/value dictionary (both names and values are strings).
        """
        properties = {}
        for name in name_list:
            value = self.get_attribute(name)
            if value is not None:
                properties[name] = value
        return properties

    @property
    def parent_asin(self):
        """
        The product's parent ASIN, if it has a parent.
        """
        return self._safe_get_element('ParentASIN')

    def get_parent(self):
        """
        Fetch parent product if it exists.
        Use `parent_asin` to check if a parent exist before fetching.

        :return: An instance of :class:`~.AmazonProduct` representing the parent product.
        """
        if not self.parent:
            parent = self._safe_get_element('ParentASIN')
            if parent:
                self.parent = self.api.lookup(item_id=parent)
        return self.parent
