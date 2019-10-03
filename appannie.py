import requests
import json, time
import datetime
from lxml import etree
from secrets import APPANNIE_USERNAME, APPANNIE_PASSWORD_HASHED, APPANNIE_USERNAME2, APPANNIE_PASSWORD_HASHED2, APPANNIE_USERNAME3, APPANNIE_PASSWORD_HASHED3, APPANNIE_USERNAME4, APPANNIE_PASSWORD_HASHED4, SCRAPED_DATA_PATH

class AppAnnie(object):
    def __init__(self, country_iso):

        self.session = requests.Session()
        self.logged_in = False
        self.country = country_iso.upper()
        self.date_as_string = datetime.datetime.today().strftime("%Y-%m-%d")
        self.feeds = ['Paid', 'Grossing', 'Free']
        self.login_url = 'https://www.appannie.com/account/login/'
        self.ajax_login_url = 'https://www.appannie.com/ajax/v2/user/login'
        self.charts_url = 'https://www.appannie.com/apps/ios/top-chart/?country={}' \
                          '&category=36&device=iphone&date={}&feed=Grossing&' \
                          'rank_sorting_type=rank&page_number=0&page_size=500&table_selections' \
                          '=&metrics=free_rank,' \
                          'paid_rank,price,category,all_avg,all_count,last_avg,last_count,' \
                          'first_release_date,last_updated_date,est_download,est_revenue' \
                          'wau&order_type=desc&order_by=grossing_rank'.format(self.country, self.date_as_string)

    def login(self, username=APPANNIE_USERNAME, password=APPANNIE_PASSWORD_HASHED):
        # print('\tLogging in...')

        self.session.headers.update({
            "authority": "www.appannie.com",
            "method": "GET",
            "path": "/account/login/",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        })

        login_res = self.session.get(self.login_url)
        csrf = self.session.cookies.get_dict()['csrftoken']
        tree = etree.HTML(login_res.text)

        data = {
            "csrfmiddlewaretoken": csrf,
            "next": "/dashboard/home/",
            "username": username,
            "password": password
        }

        self.session.headers.update({
            "method": "POST",
            "path": "/account/login/",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            "content-type": "application/x-www-form-urlencoded",
            "referer": "https://www.appannie.com/account/login",
            "origin": "https://www.appannie.com"
        })

        dashboard = self.session.post(self.ajax_login_url,
                                      data=data,
                                      allow_redirects=True)

        if dashboard.status_code == 200:
            self.logged_in = True
            print("Successfully Logged In.")
        else:
            self.logged_in = False


    def get_charts(self):
        """
            Rank, App Name, App ID, Image URL, and App Genre
        """

        if not self.logged_in:
            # self.login()
            if self.country in ['US', 'JP', 'CN', 'KR']:
                self.login()
            elif self.country in ['CA', 'GB', 'DE', 'AU', 'SE']:
                self.login(APPANNIE_USERNAME2, APPANNIE_PASSWORD_HASHED2)
            elif self.country in ['IT', 'FR', 'NZ', 'RU', 'SA']:
                self.login(APPANNIE_USERNAME3, APPANNIE_PASSWORD_HASHED3)
            elif self.country in ['CH', 'BR', 'IN', 'MX']:
                self.login(APPANNIE_USERNAME4, APPANNIE_PASSWORD_HASHED4)
            else:
                print("Bad country: {}".format(self.country))

        self.session.headers.update({
            'referer': self.charts_url,
            'x-requested-with': "XMLHttpRequest"
        })
        responses = []

        for feed in self.feeds:
            f_lower = feed.lower()
            price_idx = None
            app_genre_idx = None

            ordered_by_column = 'grossing_rank'
            if f_lower == 'paid':
                ordered_by_column = 'paid_rank'
            if f_lower == 'free':
                ordered_by_column = 'free_rank'

            url = "https://www.appannie.com/ajax/top-chart/table/?market=ios" \
                  "&country_code={}&category=36&date={}&" \
                  "rank_sorting_type=rank&page_size=500&order_by={}" \
                  "&order_type=desc&feed={}&device=iphone".format(
                self.country, self.date_as_string,
                ordered_by_column,
                feed)

            # print("\tTop {} for {}".format(feed, self.country))
            table_contents = self.session.get(url)
            if table_contents.status_code == 404:
                print ("404: {}".format(url))
                return

            completed_rows = []

            if table_contents:
                _json = table_contents.json()

                with open(SCRAPED_DATA_PATH+"json_payload_{}_{}.json".format(f_lower, self.country), "w") as f:
                    json.dump(_json, f, indent=4, sort_keys=True)

                columns = _json['table']['columns']
                for index, column in enumerate(columns):
                    if column[0][0] == 'Price':
                        price_idx = index
                    if column[0][0] == 'Category':
                        app_genre_idx = index

                rows = _json['table']['rows']

                for row in rows:
                    completed_row = dict()
                    completed_row['rank'] = row[0]
                    completed_row['company_name'] = row[1][0]['company_name']
                    completed_row['image_url'] = row[1][0]['icon']
                    completed_row['app_name'] = row[1][0]['name']
                    completed_row['app_id'] = row[1][0]['id']

                    if 'free' == feed.lower():
                        completed_row['price'] = 0
                    else:
                        completed_row['price'] = row[price_idx]

                    completed_row['app_genre'] = row[app_genre_idx]

                    completed_rows.append(completed_row)

            responses.append({
                'country': self.country,
                'apps': completed_rows,
                'type': feed
            })
        return responses


if __name__ == '__main__':

    country_list = ['us', 'jp', 'cn', 'kr', 'ca', 'gb', 'de', 'au', 'se', 'it', 'fr', 'nz', 'ru', 'sa', 'ch', 'br', 'in', 'mx']
    country_list = ['us']

    for country_iso in country_list:
        crawler = AppAnnie(country_iso)
        rows = crawler.get_charts()

        with open(SCRAPED_DATA_PATH+"combined_response_{}_{}.json".format(country_iso, crawler.date_as_string), "w") as f:
            json.dump(rows, f, indent=4, sort_keys=True)
        time.sleep(20)




    def save_feed_s3(self, data):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.S3_FEED_BUCKET_NAME)
        key = self.generate_s3_key()
        FeedArchive.objects.create(feed=self, key=key)
        k = Key(bucket)
        k.key = key
        k.set_contents_from_string(json.dumps(data))
        k.make_public()
        return
