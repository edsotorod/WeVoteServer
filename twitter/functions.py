# twitter/functions.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

import tweepy

import wevote_functions.admin
from config.base import get_environment_variable
from exception.models import handle_exception
from wevote_functions.functions import positive_value_exists

logger = wevote_functions.admin.get_logger(__name__)


WE_VOTE_SERVER_ROOT_URL = get_environment_variable("WE_VOTE_SERVER_ROOT_URL")

TWITTER_BEARER_TOKEN = get_environment_variable("TWITTER_BEARER_TOKEN")
TWITTER_CONSUMER_KEY = get_environment_variable("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = get_environment_variable("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = get_environment_variable("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = get_environment_variable("TWITTER_ACCESS_TOKEN_SECRET")

TWITTER_USER_NOT_FOUND_LOG_RESPONSES = [
    "{'code': 50, 'message': 'User not found.'}",
    "User not found."
]

TWITTER_USER_SUSPENDED_LOG_RESPONSES = [
    "{'code': 63, 'message': 'User has been suspended.'}",
    "User has been suspended."
]


def convert_twitter_user_object_data_to_we_vote_dict(twitter_user_data):
    twitter_dict = {
        'description': twitter_user_data['description']
        if 'description' in twitter_user_data else '',
        'entities': twitter_user_data['entities']
        if 'entities' in twitter_user_data else '',
        'id': twitter_user_data['id']
        if 'id' in twitter_user_data else '',
        'location': twitter_user_data['location']
        if 'location' in twitter_user_data else '',
        'name': twitter_user_data['name']
        if 'name' in twitter_user_data else '',
        'profile_image_url': twitter_user_data['profile_image_url']
        if 'profile_image_url' in twitter_user_data else '',
        'public_metrics': twitter_user_data['public_metrics']
        if 'public_metrics' in twitter_user_data else '',
        'username': twitter_user_data['username']
        if 'username' in twitter_user_data else '',
        'verified': twitter_user_data['verified']
        if 'verified' in twitter_user_data else '',
        'verified_type': twitter_user_data['verified_type']
        if 'verified_type' in twitter_user_data else '',
        'withheld': twitter_user_data['withheld']
        if 'withheld' in twitter_user_data else '',
    }
    return twitter_dict


def expand_twitter_entities(twitter_dict):
    expanded_url_count = 1
    if 'entities' in twitter_dict:
        # Support for 'expanded_url' and 'expanded_url2'
        if 'url' in twitter_dict['entities']:
            if 'urls' in twitter_dict['entities']['url']:
                if len(twitter_dict['entities']['url']['urls']) > 0:
                    for one_url_dict in twitter_dict['entities']['url']['urls']:
                        if 'expanded_url' in one_url_dict:
                            if expanded_url_count > 1:
                                expanded_url_name = \
                                    "expanded_url{expanded_url_count}".format(expanded_url_count=expanded_url_count)
                                # TODO: Make dynamic -- running into: 'User' object does not support item assignment
                                twitter_dict[expanded_url_name] = one_url_dict['expanded_url']
                            else:
                                twitter_dict['expanded_url'] = one_url_dict['expanded_url']
                            expanded_url_count += 1
    return twitter_dict


def expand_twitter_public_metrics(twitter_dict):
    if 'public_metrics' in twitter_dict:
        public_metrics = twitter_dict['public_metrics']
        if 'followers_count' in public_metrics:
            twitter_dict['followers_count'] = public_metrics['followers_count']
        if 'following_count' in public_metrics:
            twitter_dict['following_count'] = public_metrics['following_count']
    return twitter_dict


def retrieve_twitter_user_info(twitter_user_id=0, twitter_handle='', twitter_api_counter_manager=None):
    """
    :param twitter_user_id:
    :param twitter_handle:
    :param twitter_api_counter_manager:
    :return:
    """
    status = ""
    success = True
    twitter_user_not_found_in_twitter = False
    twitter_user_suspended_by_twitter = False
    write_to_server_logs = False

    # December 2021: Using the Twitter 1.1 API for OAuthHandler, since all other 2.0 apis that we need are not
    # yet available.
    # auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    # auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    #
    # api = tweepy.API(auth, timeout=10)
    logger.error("twitter/functions 111: session: client = tweepy.Client() twitter_handle: ", twitter_handle)
    client = tweepy.Client(
        bearer_token=TWITTER_BEARER_TOKEN,
        consumer_key=TWITTER_CONSUMER_KEY,
        consumer_secret=TWITTER_CONSUMER_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)
    # client = tweepy.Client(
    #     bearer_token=TWITTER_BEARER_TOKEN,
    # )

    # Strip out the twitter handles "False" or "None"
    if twitter_handle is False:
        twitter_handle = ''
    elif twitter_handle is None:
        twitter_handle = ''
    elif twitter_handle:
        twitter_handle_lower = twitter_handle.lower()
        if twitter_handle_lower == 'false' or twitter_handle_lower == 'none':
            twitter_handle = ''

    twitter_handle_found = False
    twitter_dict = {}
    from wevote_functions.functions import convert_to_int
    twitter_user_id = convert_to_int(twitter_user_id)
    try:
        if positive_value_exists(twitter_handle):
            # Use Twitter API call counter to track the number of queries we are doing each day
            if hasattr(twitter_api_counter_manager, 'create_counter_entry'):
                twitter_api_counter_manager.create_counter_entry('get_user')

            twitter_user = client.get_user(
                username=twitter_handle,
                user_fields=[
                    'description',
                    'entities',
                    'id',
                    'location',
                    'name',
                    'profile_image_url',
                    'public_metrics',
                    'username',
                    'verified',
                    'verified_type',
                    'withheld',
                ])
            # 'url', We only take in the url from the 'entities' data since 'url' is always a Twitter shortened url

            # [connection_status, created_at, description, entities, id, location, most_recent_tweet_id, name,
            #  pinned_tweet_id, profile_image_url, protected, public_metrics, receives_your_dm, subscription_type, url,
            #  username, verified, verified_type, withheld]
            try:
                twitter_dict = convert_twitter_user_object_data_to_we_vote_dict(twitter_user.data)
                twitter_user_id = getattr(twitter_user.data, 'id')  # Integer value. id_str would be the String value
                twitter_handle_found = True
            except Exception as e:
                status += 'TWITTER_DICT_DATA_NOT_FOUND-' + str(e) + " "
                twitter_dict = {}
                twitter_user_id = 0
                twitter_handle_found = False
            success = True
            # status += 'TWITTER_HANDLE_SUCCESS-' + str(twitter_handle) + " "
        elif positive_value_exists(twitter_user_id):
            # Use Twitter API call counter to track the number of queries we are doing each day
            if hasattr(twitter_api_counter_manager, 'create_counter_entry'):
                twitter_api_counter_manager.create_counter_entry('get_user')

            # twitter_user = api.get_user(user_id=twitter_user_id)
            twitter_user = client.get_user(id=twitter_user_id)
            try:
                twitter_dict = convert_twitter_user_object_data_to_we_vote_dict(twitter_user.data)
                twitter_user_id = getattr(twitter_user.data, 'id')  # Integer value. id_str would be the String value
                twitter_handle = getattr(twitter_user.data, 'username')
                twitter_handle_found = True
            except Exception as e:
                status += 'TWITTER_JSON_DATA_NOT_FOUND_FROM_ID-' + str(e) + " "
                twitter_dict = {}
                twitter_user_id = 0
            success = True
            # status += 'TWITTER_USER_ID_SUCCESS-' + str(twitter_user_id) + " "
            twitter_handle_found = True
        else:
            twitter_dict = {}
            success = False
            status += 'TWITTER_RETRIEVE_NOT_SUCCESSFUL-MISSING_VARIABLE '
            twitter_handle_found = False
    except tweepy.TooManyRequests as rate_limit_error:
        success = False
        status += 'TWITTER_RATE_LIMIT_ERROR: ' + str(rate_limit_error) + " "
        handle_exception(rate_limit_error, logger=logger, exception_message=status)
    except tweepy.errors.HTTPException as error_instance:
        if 'User not found.' in error_instance.api_messages:
            status += 'TWITTER_USER_NOT_FOUND_ON_TWITTER: ' + str(error_instance) + ' '
            twitter_user_not_found_in_twitter = True
        else:
            success = False
            status += 'TWITTER_HTTP_EXCEPTION: ' + str(error_instance) + ' '
            handle_exception(error_instance, logger=logger, exception_message=status)
    except tweepy.errors.TweepyException as error_instance:
        success = False
        status += "[TWEEPY_EXCEPTION_ERROR: "
        status += twitter_handle + " " if positive_value_exists(twitter_handle) else ""
        status += str(twitter_user_id) + " " if positive_value_exists(twitter_user_id) else " "
        if error_instance:
            status += str(error_instance) + " "
        if error_instance and hasattr(error_instance, 'args'):
            try:
                error_tuple = error_instance.args
                for error_dict in error_tuple:
                    for one_error in error_dict:
                        status += '[' + one_error['message'] + '] '
                        if one_error['message'] in TWITTER_USER_NOT_FOUND_LOG_RESPONSES:
                            twitter_user_not_found_in_twitter = True
                        elif one_error['message'] in TWITTER_USER_SUSPENDED_LOG_RESPONSES:
                            twitter_user_suspended_by_twitter = True
                        else:
                            write_to_server_logs = True
            except Exception as e:
                status += "PROBLEM_PARSING_TWEEPY_ERROR: " + str(e) + " "
                write_to_server_logs = True
        else:
            write_to_server_logs = True
        status += "]"
        if write_to_server_logs:
            handle_exception(error_instance, logger=logger, exception_message=status)
    except Exception as e:
        success = False
        status += "TWEEPY_EXCEPTION: " + str(e) + " "
        handle_exception(e, logger=logger, exception_message=status)

    twitter_dict = expand_twitter_entities(twitter_dict)
    twitter_dict = expand_twitter_public_metrics(twitter_dict)
    # profile_banner_url no longer provided by Twitter
    # try:
    #     if positive_value_exists(twitter_dict.get('profile_banner_url')):
    #         # Dec 2019, https://developer.twitter.com/en/docs/accounts-and-users/user-profile-images-and-banners
    #         banner = twitter_dict.get('profile_banner_url') + '/1500x500'
    #         twitter_dict['profile_banner_url'] = banner
    # except Exception as e:
    #     status += "FAILED_PROFILE_BANNER_URL: " + str(e) + " "

    results = {
        'status':                               status,
        'success':                              success,
        'twitter_handle':                       twitter_handle,
        'twitter_handle_found':                 twitter_handle_found,
        'twitter_dict':                         twitter_dict,
        'twitter_user_id':                      twitter_user_id,
        'twitter_user_not_found_in_twitter':    twitter_user_not_found_in_twitter,
        'twitter_user_suspended_by_twitter':    twitter_user_suspended_by_twitter,
    }
    return results


def retrieve_twitter_user_info_from_handles_list(
        twitter_handles_list=[],
        google_civic_api_counter_manager=None):
    retrieve_from_twitter = len(twitter_handles_list) > 0
    success = True
    status = ""
    twitter_response_dict_list = []
    twitter_response_object_list = []

    if retrieve_from_twitter:
        try:
            logger.error("twitter/functions.py 278: session: client = tweepy.Client()")
            client = tweepy.Client(
                bearer_token=TWITTER_BEARER_TOKEN,
                consumer_key=TWITTER_CONSUMER_KEY,
                consumer_secret=TWITTER_CONSUMER_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)

            # Use Twitter API call counter to track the number of queries we are doing each day
            if hasattr(google_civic_api_counter_manager, 'create_counter_entry'):
                google_civic_api_counter_manager.create_counter_entry('get_users')

            twitter_response = client.get_users(
                usernames=twitter_handles_list,
                user_fields=[
                    'description',
                    'entities',
                    'id',
                    'location',
                    'name',
                    'profile_image_url',
                    'public_metrics',
                    'username',
                    'verified',
                    'verified_type',
                    'withheld',
                ])
            if hasattr(twitter_response, 'data'):
                twitter_response_object_list = twitter_response.data
                for twitter_user in twitter_response_object_list:
                    twitter_dict = convert_twitter_user_object_data_to_we_vote_dict(twitter_user.data)
                    twitter_dict = expand_twitter_entities(twitter_dict)
                    twitter_dict = expand_twitter_public_metrics(twitter_dict)
                    twitter_response_dict_list.append(twitter_dict)
        except Exception as e:
            status += "PROBLEM_RETRIEVING_TWITTER_DETAILS: " + str(e) + " "
            success = False
    twitter_response_list_retrieved = len(twitter_response_dict_list) > 0
    results = {
        'success':                          success,
        'status':                           status,
        'twitter_response_list':            twitter_response_dict_list,
        'twitter_response_list_retrieved':  twitter_response_list_retrieved,
    }
    return results
