import csv
import time
from urllib import parse

import requests
from utils import get_soup


class CarInfo:

    model = ''
    price = ''
    # tbd

    def __init__(self, brand):
        self.brand = brand


class Brand:
    def __init__(self, name, logo, id):
        self.name, self.logo, self.id = name, logo, id


class CarModel:
    brand_name = ''
    def __init__(self, name, dealer_price, id, car_ids):
        self.name = name
        self.id = id
        self.price = dealer_price
        self.car_ids = car_ids


class ModelDetail:
    brand = ''
    name = ''
    official_price = ''
    dealer_price = ''
    series_type = ''
    car_year = ''
    engine_description = ''
    energy_elect_max_power = ''
    market_time = ''
    max_torque = ''
    car_body_struct = ''
    gearbox_description = ''
    max_speed = ''
    acceleration_time = ''
    driver_form = ''





# beautifulSoup docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
class CarInfoGeter:


    def get_brands(self):
        u = 'https://www.dongchedi.com/auto/library/x-x-x-x-x-x-x-x-x-x-x'
        soup, err = get_soup(u)
        if err is not None:
            return [], err

        # print('[Debug] soup = ', soup.prettify())

        def has_brand_claas_prefix(class_name):
            return class_name.startswith('jsx-2929075810 brand')

        brands = []
        for brand_item in soup.find(class_='jsx-2929075810 brands').find_all(class_=has_brand_claas_prefix):
            # print('[Debug]print item=', brand_item.find('span').get_text(), brand_item.find('img')['src'])
            brand_name = brand_item.find('span').get_text()
            brand_logo = brand_item.find('img')['src']
            id = brand_item['class'][-1].strip('brand-')

            if brand_name is None or brand_logo is None:
                continue
            if len(brand_name) > 10 or len(brand_logo) > 100:
                continue
            brand = Brand(brand_name, brand_logo, id)
            # print("[Debug] brand=", brand.__dict__)
            brands.append(brand)
        return brands, None

    # curl -X POST  https://www.dongchedi.com/motor/brand/m/v6/select/series/\?offset=0\&limit=100\&is_refresh=1\&city_name=深圳\&brand=2 -H 'Content-Type:application/x-www-form-urlencoded' -H 'referer:https://www.dongchedi.com/auto/library/x-x-x-x-x-x-x-x-x-x-x\?key\=brand\&param\=2\&text\=奥迪'
    def get_models(self, brand):
        u = 'https://www.dongchedi.com/motor/brand/m/v6/select/series/?offset=0&limit=300' \
            '&is_refresh=1&city_name=深圳&brand=%s' % brand.id
        referer_header = 'https://www.dongchedi.com/auto/library/x-x-x-x-x-x-x-x-x-x-x?key=brand&param=2&text=%s' \
                         % parse.quote(brand.name)
        headers = {
            'referer': referer_header,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        resp = requests.post(u, headers=headers)
        if resp.status_code != 200:
            return None, 'invalid status_code=%d' % resp.status_code

        # print("[Debug] resp=", resp.json())

        models = []
        for item in resp.json()['data']['series']:
            model = CarModel(item['outter_name'], item['dealer_price'], item['id'], item['car_ids'])
            model.brand_name = brand.name
            models.append(
                model
            )
            # print("[Debug] model=%s", model.__dict__)
        return models, None

    # curl https://www.dongchedi.com/motor/car_page/v4/get_entity_json/\?car_id_list\=40343%2C51399\&city_name\=%E6%B7%B1%E5%9C%B3\&version_code\=444
    def get_model_detail(self, model):
        u = 'https://www.dongchedi.com/motor/car_page/v4/get_entity_json/?car_id_list=%s&city_name=深圳&version_code=444' \
            % (','.join([ str(x) for x in model.car_ids]))
        resp = requests.get(u)
        if resp.status_code != 200:
            return None, 'invalid status_code=%d' % resp.status_code


        model_details = []
        for item in resp.json()['data']['car_info']:
            # print("[Debug] item=", item)
            detail = ModelDetail()

            detail.brand_name = model.brand_name
            detail.series_name = item['series_name']
            detail.car_name = item['car_name']
            detail.car_year = item['car_year']
            detail.official_price = item.get('official_price')
            detail.dealer_price = item['dealer_price']
            detail.series_type = item['series_type']

            detail.engine_description = item['info']['engine_description']['value']
            detail.energy_elect_max_power = item['info']['energy_elect_max_power']['value']
            detail.market_time = item['info']['market_time']['value']
            detail.max_torque = item['info']['max_torque']['value']
            detail.car_body_struct = item['info']['car_body_struct']['value']
            detail.gearbox_description = item['info']['gearbox_description']['value']
            detail.max_speed = item['info']['max_speed']['value']
            detail.acceleration_time = item['info']['acceleration_time']['value']
            detail.driver_form = item['info']['driver_form']['value']


            print("[Debug] model detail=", detail.__dict__)
            model_details.append(detail)
        return model_details, None


    def all_car_infos(self):
        brands, err = self.get_brands()
        if err is not None:
            return 'get brands failed, err=%s' % err

        print('[Info] get brands success, len=', len(brands))

        for brand in brands:
            with open('./data/%s.csv'%brand.name, 'w', newline='') as csvfile:
                fieldnames = ['brand_name', 'series_name', 'car_name', 'official_price', 'dealer_price', 'series_type',
                              'car_year', 'engine_description',
                              'energy_elect_max_power', 'market_time', 'max_torque', 'car_body_struct',
                              'gearbox_description', 'max_speed', 'acceleration_time', 'driver_form']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                models, err = self.get_models(brand)
                if err is not None:
                    print('[Error] get models failed, brand=%s, err=%s' % (brand.name, err))
                    continue
                print('[Info] get models, brand=%s,len=', brand.name, len(models))

                for model in models:
                    model_details, err = self.get_model_detail(model)
                    if err is not None:
                        print('[Error] get model detail failed, model_name=%s, err=%s' %( model.name, err))
                        continue
                    print('[Info] get model detail success, model_name=%s, len of result=%d' % (model.name, len(model_details)))

                    for detail in model_details:
                        writer.writerow(detail.__dict__)
                    time.sleep(0.05)

        return None


def test_cases():
    geter = CarInfoGeter()

    # get brands
    print("[Test] >>>> get_brands <<<<")
    brands, err = geter.get_brands()
    if err is not None:
        print('get brands failed, err=', err)
        exit(1)
    print('brands len=', len(brands))

    # get model by brands
    print("[Test] >>>> get_models <<<<")
    models, err = geter.get_models(Brand('', ''))
    if err is not None:
        print('get models failed, err=', err)
        exit(1)
    print('models len=', len(models))

    print("[Test] >>> get_model_detail <<<")
    for model in models:
        if model.name == '奥迪RS 7':
            model_details, err = geter.get_model_detail(model)
            if err is not None:
                print('get model detail failed, err=', err)
                exit(1)
            print('get model success, len of result=', len(model_details))


def product():
    geter = CarInfoGeter()
    err = geter.all_car_infos()
    if err is not None:
        print("[Error] failed, err=", err)
        exit(1)
    print("success")

if __name__ == '__main__':

    test_cases()

    # product()
