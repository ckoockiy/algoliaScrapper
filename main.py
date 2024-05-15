import requests


class Quada:
    """
        A class to handle requests and headers for interacting with the Quada Tradewing website.

        Attributes:
        headers (dict): HTTP headers used for requests to the Quada Tradewing website.
        params (dict): Query parameters for the API request.
        json_data (dict): JSON payload for the API request.
        _headersAlgolia (dict): HTTP headers used for requests to the Algolia API.
    """

    def __init__(self):
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,es;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://quada.tradewing.com',
            'referer': 'https://quada.tradewing.com/members/companies',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'tenant_domain': 'quada.tradewing.com',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        }

        self.params = {
            'opname': 'UseOrganizationDirectory_GetOrganizationSearchKeys',
        }

        self.json_data = {
            'operationName': 'UseOrganizationDirectory_GetOrganizationSearchKeys',
            'variables': {
                'input': {
                    'filter': {
                        'isMember': True,
                    },
                },
            },
            'query': 'query UseOrganizationDirectory_GetOrganizationSearchKeys($input: GetOrganizationsSearchKeysInput!) {\n  getOrganizationsSearchKeys(input: $input) {\n    applicationId\n    searchApiKey\n    indexData {\n      indexName\n      searchableAttributesField\n      viewableAttributesField\n      __typename\n    }\n    __typename\n  }\n}\n',
        }

        self._headersAlgolia = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'x-algolia-api-key': None,
            'x-algolia-application-id': 'TG4ZN1LT5Z',
            'content-type': 'application/x-www-form-urlencoded',
            'Origin': 'https://quada.tradewing.com',
            'Connection': 'keep-alive',
            'Referer': 'https://quada.tradewing.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        }

    def get_apikey(self):
        """
            Sends a POST request to the specified URL to obtain an API key.
            Updates the self._headersAlgolia dictionary with the obtained API key.

            Returns:
                True if the API key is successfully obtained, False otherwise.
        """
        try:
            response = requests.post('https://quada.tradewing.com/graphql2',
                                     params=self.params, headers=self.headers, json=self.json_data)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            data = response.json()
            apikey = (
                data.get("data", {})
                .get("getOrganizationsSearchKeys", {})
                .get("searchApiKey", "")
            )
            if apikey:
                self._headersAlgolia['x-algolia-api-key'] = apikey
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return False

    def get_companies(self, page_number):
        """
            Retrieves a list of companies from the Algolia API.

            Args:
                page_number (int): The page number to retrieve companies from.

            Returns:
                None
        """
        try:
            data = '{"requests":[{"indexName":"organizations","params":"highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=8&facetFilters=%5B%5D&query=&page=&facets=%5BguestMemberDirectorySearchable.firstName%5D&tagFilters="}]}'.replace(
                "&page=", "&page="+str(page_number))

            response = requests.post(
                'https://tg4zn1lt5z-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.5.1)%3B%20Browser%3B%20JS%20Helper%20(3.8.2)%3B%20react%20(18.2.0)%3B%20react-instantsearch%20(6.26.0)',
                headers=self._headersAlgolia,
                data=data,
            )
            response.raise_for_status()  # Raise an exception for non-2xx status codes

            desired_fields = [
                "company-name",
                "company-email",
                "company-primaryPhone",
                "company-addressLine0",
                "company-addressLocality",
                "company-addressAdministrativeArea",
                "company-addressRegionCode"
            ]
            data_json = response.json()
            companies = data_json["results"][0]['hits']
            for company in companies:
                extracted_data = {
                    key: company["loggedInMemberDirectorySearchable"][key] for key in desired_fields}
                extracted_data["objectID"] = company["objectID"]
                print(extracted_data, end="\n")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    quada = Quada()
    apikey = quada.get_apikey()

    if apikey:
        page_number = 0
        quada.get_companies(page_number=page_number)
