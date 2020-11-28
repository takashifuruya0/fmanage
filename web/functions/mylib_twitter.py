from requests_oauthlib import OAuth1Session
from django.conf import settings
import json
import logging
logger = logging.getLogger('django')


class Twitter:
    def __init__(self):
        self.twitter = OAuth1Session(
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET,
            settings.TWITTER_ACCESS_KEY,
            settings.TWITTER_ACCESS_SECRET
        )

    def getTweets(self, keyword, search_limit_count):
        url= 'https://api.twitter.com/1.1/search/tweets.json'
        params = {'q': keyword, 'count': search_limit_count, 'result_type': 'mixed'}
        try:
            r = self.twitter.get(url, params=params)
            if r.status_code == 200:
                return r.json()
            else:
                error_msg = 'Failed to getTweets. keyword:{}, search_limit_count:{}'.format(keyword, search_limit_count)
                raise Exception(error_msg)
        except Exception as e:
            logger.error(e)
            return False


"""
{
    'search_metadata': {
        'completed_in': 0.024,
        'count': 2,
        'max_id': 1308365790660317193,
        'max_id_str': '1308365790660317193',
        'next_results': '?max_id=1308066857866293250&q=%E4%BA%94%E6%B4%8B%E5%BB%BA%E8%A8%AD&count=2&include_entities=1&result_type=mixed',
        'query': '%E4%BA%94%E6%B4%8B%E5%BB%BA%E8%A8%AD',
        'refresh_url': '?since_id=1308365790660317193&q=%E4%BA%94%E6%B4%8B%E5%BB%BA%E8%A8%AD&result_type=mixed&include_entities=1',
        'since_id': 0,
        'since_id_str': '0'
    },
    'statuses': [
        {
            'contributors': None,
            'coordinates': None,
            'created_at': 'Tue Sep 22 11:21:27 +0000 2020',
            'entities': {
                'hashtags': [],
                'symbols': [],
                'urls': [],
                'user_mentions': []
            },
            'favorite_count': 0,
            'favorited': False,
            'geo': None,
            'id': 1308365790660317193,
            'id_str': '1308365790660317193',
            'in_reply_to_screen_name': None,
            'in_reply_to_status_id': None,
            'in_reply_to_status_id_str': None,
            'in_reply_to_user_id': None,
            'in_reply_to_user_id_str': None,
            'is_quote_status': False,
            'lang': 'ja',
            'metadata': {'iso_language_code': 'ja', 'result_type': 'recent'},
            'place': None,
            'retweet_count': 0,
            'retweeted': False,
            'source': '<a href="http://twitter.com/download/android" '
                     'rel="nofollow">Twitter for Android</a>',
            'text': '洋上風力買おうと思って、応用地質見つけてラッキーとかおもってて。レノバ、五洋建設、戸田建設と３時間以上悩んだ末。\n'
                       '\n'
                       '買わない。(ToT)\n'
                       '\n'
                       'でも、もうちょい悩む。その時間だけが楽しい。',
            'truncated': False,
            'user': {
                'contributors_enabled': False,
                'created_at': 'Sat Aug 16 16:50:59 +0000 2014',
                'default_profile': False,
                'default_profile_image': False,
                'description': '2020年から投資を始めました。好きな言葉は「再配当」「理論株価」「りそな銀行」です。',
                'entities': {'description': {'urls': []}},
                'favourites_count': 747,
                'follow_request_sent': False,
                'followers_count': 39,
                'following': False,
                'friends_count': 121,
                'geo_enabled': False,
                'has_extended_profile': True,
                'id': 2737597128,
                'id_str': '2737597128',
                'is_translation_enabled': False,
                'is_translator': False,
                'lang': None,
                'listed_count': 0,
                'location': '日本',
                'name': 'おーちゅあん',
                'notifications': False,
                'profile_background_color': '000000',
                'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png',
                'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png',
                'profile_background_tile': False,
                'profile_banner_url': 'https://pbs.twimg.com/profile_banners/2737597128/1520779392',
                'profile_image_url': 'http://pbs.twimg.com/profile_images/1299680529252405248/F8Q_Uqdu_normal.jpg',
                'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1299680529252405248/F8Q_Uqdu_normal.jpg',
                'profile_link_color': '9F7DBA',
                'profile_sidebar_border_color': '000000',
                'profile_sidebar_fill_color': '000000',
                'profile_text_color': '000000',
                'profile_use_background_image': False,
                'protected': False,
                'screen_name': '098musiba',
                'statuses_count': 301,
                'time_zone': None,
                'translator_type': 'none',
                'url': None,
                'utc_offset': None,
                'verified': False
            }
        },
        {
            'contributors': None,
            'coordinates': None,
            'created_at': 'Mon Sep 21 15:33:36 +0000 2020',
            'entities': {
                'hashtags': [],
                'symbols': [],
                'urls': [],
                'user_mentions': []
            },
            'favorite_count': 1,
            'favorited': False,
            'geo': None,
            'id': 1308066857866293251,
            'id_str': '1308066857866293251',
            'in_reply_to_screen_name': None,
            'in_reply_to_status_id': None,
            'in_reply_to_status_id_str': None,
            'in_reply_to_user_id': None,
            'in_reply_to_user_id_str': None,
            'is_quote_status': False,
            'lang': 'ja',
            'metadata': {'iso_language_code': 'ja', 'result_type': 'recent'},
            'place': None,
            'retweet_count': 0,
            'retweeted': False,
            'source': '<a href="http://twitter.com/download/android" '
                     'rel="nofollow">Twitter for Android</a>',
            'text': 'NHKBSで放送された「建築王国物語」で有明の体操競技場工事てわ清水建設の所長さんが施工で苦労した話をしてたのに、世界でも希な海上建築物である東京クルーズターミナル工事については、施工した海洋建築のエキスパートの五洋建設さんなどが出てこなかったのは残念。',
            'truncated': False,
            'user': {
                'contributors_enabled': False,
                'created_at': 'Wed Apr 21 05:24:55 +0000 2010',
                'default_profile': True,
                'default_profile_image': False,
                'description': '地方競馬をすご～く愛して。長～く愛して。',
                'entities': {
                    'description': {'urls': []},
                    'url': {
                        'urls': [
                            {
                                'display_url': 'twilog.org/toutouakiakimas',
                                'expanded_url': 'http://twilog.org/toutouakiakimas',
                                'indices': [0, 22],
                                'url': 'http://t.co/FMUdxkEVql'
                            }
                        ]
                    }
                },
                'favourites_count': 740,
                'follow_request_sent': False,
                'followers_count': 859,
                'following': False,
                'friends_count': 1674,
                'geo_enabled': True,
                'has_extended_profile': False,
                'id': 135395293,
                'id_str': '135395293',
                'is_translation_enabled': False,
                'is_translator': False,
                'lang': None,
                'listed_count': 16,
                'location': '千葉県',
                'name': '地方競馬に栄光あれ',
                'notifications': False,
                'profile_background_color': 'C0DEED',
                'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png',
                'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png',
                'profile_background_tile': False,
                'profile_image_url': 'http://pbs.twimg.com/profile_images/584669870836416512/QId49kRD_normal.jpg',
                'profile_image_url_https': 'https://pbs.twimg.com/profile_images/584669870836416512/QId49kRD_normal.jpg',
                'profile_link_color': '1DA1F2',
                'profile_sidebar_border_color': 'C0DEED',
                'profile_sidebar_fill_color': 'DDEEF6',
                'profile_text_color': '333333',
                'profile_use_background_image': True,
                'protected': False,
                'screen_name': 'toutouakiakimas',
                'statuses_count': 5868,
                'time_zone': None,
                'translator_type': 'none',
                'url': 'http://t.co/FMUdxkEVql',
                'utc_offset': None,
                'verified': False
            }
        }
    ]
}
"""