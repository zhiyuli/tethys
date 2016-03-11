"""
********************************************************************************
* Name: arcgis.py
* Author: Nathan Swain and Michael Souffront
* Created On: March 10, 2016
* Copyright: (c) Aquaveo 2016
* License: BSD 2-Clause
********************************************************************************
"""

from social.backends.oauth import BaseOAuth2


class ArcGISOAuth2(BaseOAuth2):
    """
    ArcGISOAuth2 OAuth2 authentication backend.
    """
    name = 'arcgis'
    AUTHORIZATION_URL = 'https://www.arcgis.com/sharing/rest/oauth2/authorize/'
    ACCESS_TOKEN_URL = 'https://www.arcgis.com/sharing/rest/oauth2/token/'
    ACCESS_TOKEN_METHOD = 'POST'
    # RESPONSE_TYPE = 'token'
    # SCOPE_SEPARATOR = ','
    # ID_KEY = 'username'
    # EXTRA_DATA = [
    #     ('email', 'email'),
    #     ('username', 'id'),
    #     ('expires_in', 'expires_in'),
    #     ('token_type', 'token_type'),
    #     ('refresh_token', 'refresh_token'),
    #     ('scope', 'scope'),
    #     ('token_dict', 'token_dict'),
    # ]

    # def extra_data(self, user, uid, response, details=None, *args, **kwargs):
    #     data = super(HydroShareOAuth2, self).extra_data(user, uid, response,
    #                                                     details,
    #                                                     *args, **kwargs)
    #     # Calculate 'expires_at'
    #     t = time.time()
    #     expires_in = response.get('expires_in', '') or \
    #                  kwargs.get('expires_in')
    #     # Reconstitute token dictionary for client convenience
    #     token_dict = {
    #         'access_token': data['access_token'],
    #         'token_type': data['token_type'],
    #         'expires_in': expires_in,
    #         'refresh_token': data['refresh_token'],
    #         'scope': data['scope']
    #         }
    #     data['token_dict'] = token_dict
    #
    #     return data

    def get_user_details(self, response):
        """
        Return user details from HydroShare account.
        """
        print(response.get('username'))
        print(response.get('email'))
        return {'username': response.get('username'),
                'email': response.get('email')}

    # def user_data(self, access_token, *args, **kwargs):
    #     """
    #     Loads user data from service.
    #     """
    #     url = 'https://www.hydroshare.org/hsapi/userInfo/'
    #     try:
    #         return self.get_json(url, params={'access_token': access_token})
    #     except ValueError:
    #         return None