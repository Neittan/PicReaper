import os
import requests
from bs4 import BeautifulSoup as bs
import csv


class UserParsingSettings:
    def __init__(self, game_name, category_name, start_page, end_page, dest_folder, db_path):
        self.game_name = game_name
        self.category_name = category_name
        self.start_page = start_page
        self.end_page = end_page if end_page else start_page
        self.dest_folder = dest_folder
        self.db_path = db_path
        self.download_dir = f"{self.dest_folder}/{self.game_name}/{self.category_name}/"
        self.base_category_page_url = self.__get_base_category_page_url()

    def __get_header(self):
        with open(self.db_path, "r") as f:
            return list(csv.reader(f))[0]

    def __get_game_row(self):
        with open(self.db_path, "r") as f:
            for row in csv.reader(f):
                if row[0] == self.game_name:
                    return row

    def __get_game_id(self):
        return self.__get_game_row()[1]

    def __get_category_id(self):
        return self.__get_game_row()[self.__get_header().index(self.category_name)]

    def __get_base_category_page_url(self):
        return f'https://www.nexusmods.com/Core/Libs/Common/' \
               f'Widgets/ImageList?RH_ImageList=categories%5B%5D:' \
               f'{self.__get_category_id()},user_id:0,nav:true,game_id:' \
               f'{self.__get_game_id()},time:0,category_id:' \
               f'{self.__get_category_id()},show_hidden:false,page_size:16,page:'


def get_images_pages_list_from_category_page(ups: UserParsingSettings, num: int):
    url = ups.base_category_page_url + str(num)
    r = requests.get(url)
    soup = bs(r.content, 'html.parser')
    nexus_pages_links = soup.find_all('li', class_="image-tile")
    images_pages_urls = []
    for page in nexus_pages_links:
        images_pages_urls.append(page.a['href'])
    return images_pages_urls


def download_image(url, ups: UserParsingSettings):
    r = requests.get(url)
    soup = bs(r.content, 'html.parser')
    img_data = soup.find('img', class_='aligncenter')
    img_id = url.split('/')[-1]
    img_name = img_data['title']
    img_download_url = img_data['src']
    filename = f"{img_id}_{img_name}.{img_download_url.split('.')[-1].rstrip('/')}"
    downloading_directory = f"{ups.dest_folder}/{ups.game_name}/{ups.category_name}/"
    if not os.path.exists(downloading_directory):
        os.makedirs(downloading_directory)
    full_file_path = os.path.abspath(downloading_directory + filename)
    img_content = requests.get(img_download_url).content
    if not os.path.exists(full_file_path):
        print(f'Downloading image: {filename}')
        with open(full_file_path, 'wb') as f:
            f.write(img_content)
    else:
        print(f'Image [{filename}] already exist')


def main():
    ups = UserParsingSettings("Fallout 4",  # Game name
                              "Aesthetic",  # Category name
                              1,  # Start page
                              1,  # End page
                              "D:/Pictures/NexusImages",  # Downloading directory
                              "Nexus_Games_DB.csv")  # Games DB path
    for i in range(ups.start_page, ups.end_page+1):
        img_pages_list = get_images_pages_list_from_category_page(ups, i)
        print("Page ", i)
        for img_page in img_pages_list:
            download_image(img_page, ups)


if __name__ == '__main__':
    main()