from os import name
import urllib.request

def download_files_Italy(save_folder = './data/Italie/', saison='2021'):
    url = 'https://www.football-data.co.uk/mmz4281/{}/I1.csv'.format(saison)
    urllib.request.urlretrieve(url, save_folder + saison + '-Italie1.csv')
    url = 'https://www.football-data.co.uk/mmz4281/{}/I2.csv'.format(saison)
    urllib.request.urlretrieve(url, save_folder + saison + '-Italie2.csv')

def download_files_France(save_folder = './data/France/', saison='2021'):
    url = 'https://www.football-data.co.uk/mmz4281/{}/F1.csv'.format(saison)
    urllib.request.urlretrieve(url, save_folder + saison + '-France1.csv')
    url = 'https://www.football-data.co.uk/mmz4281/{}/F2.csv'.format(saison)
    urllib.request.urlretrieve(url, save_folder + saison + '-France2.csv')

def download_files_Spain(save_folder = './data/Espagne/', saison='2021'):
    url = 'https://www.football-data.co.uk/mmz4281/{}/SP1.csv'.format(saison)
    urllib.request.urlretrieve(url, save_folder + saison + '-Espagne1.csv')
    url = 'https://www.football-data.co.uk/mmz4281/2021/SP2.csv'.format(saison)
    urllib.request.urlretrieve(url, save_folder + saison + '-Espagne2.csv')

def download_files_Germany(save_folder = './data/Allemagne/', saison='2021'):
    url = 'https://www.football-data.co.uk/mmz4281/{}/D1.csv'.format(saison)
    urllib.request.urlretrieve(url, save_folder + saison + '-Allemagne1.csv')
    url = 'https://www.football-data.co.uk/mmz4281/{}/D2.csv'.format(saison)
    urllib.request.urlretrieve(url, save_folder + saison + '-Allemagne2.csv')

def download_files_England(save_folder = './data/Angleterre/', saison='2021'):
    url = 'https://www.football-data.co.uk/mmz4281/{}/E0.csv'.format(saison)
    urllib.request.urlretrieve(url, save_folder + saison + '-Angleterre1.csv')
    url = 'https://www.football-data.co.uk/mmz4281/{}/E1.csv'.format(saison)
    urllib.request.urlretrieve(url, save_folder + saison + '-Angleterre2.csv')


def download_files_from_website(saison='2021'):
    download_files_Italy(saison=saison)
    download_files_France(saison=saison)
    download_files_Spain(saison=saison)
    download_files_England(saison=saison)
    download_files_Germany(saison=saison)

if __name__ == "__main__":
    download_files_from_website(saison="2021")