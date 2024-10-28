import scrapy
import csv
import matplotlib.pyplot as plt
from scrapy.crawler import CrawlerProcess

class DivannewparsSpider(scrapy.Spider):
    name = "divannewpars"
    allowed_domains = ["divan.ru"]
    start_urls = ["https://www.divan.ru/category/divany-i-kresla"]

    custom_settings = {
        'FEED_FORMAT': 'csv',  # Формат файла для сырого вывода
        'FEED_URI': 'raw_prices.csv'  # Название файла для сырого вывода
    }

    def parse(self, response):
        divans = response.css('div._Ud0k')
        for divan in divans:
            yield {
                'name': divan.css('div.lsooF span::text').get(),
                'price': divan.css('div.pY3d2 span::text').get()
            }

def process_data(input_file, output_file):
    cleaned_data = []
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ['name', 'price']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            price_text = row['price'].replace(' ₽/мес.', '').replace(' ', '')
            try:
                price = int(price_text)  # Преобразуем цену в целое число
                row['price'] = price
                cleaned_data.append(price)
                writer.writerow(row)
            except ValueError:
                continue  # Пропускаем строки, где не удалось преобразовать цену

    return cleaned_data

def plot_histogram(data):
    average_price = sum(data) / len(data) if data else 0
    print(f"Средняя цена на диваны: {average_price:.2f} руб.")

    # Построение гистограммы
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=20, color='skyblue', edgecolor='black')
    plt.title('Гистограмма цен на диваны')
    plt.xlabel('Цена (руб)')
    plt.ylabel('Количество диванов')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

# Запуск процесса парсинга
process = CrawlerProcess()
process.crawl(DivannewparsSpider)
process.start()

# Обработка данных и построение гистограммы
input_file = 'raw_prices.csv'
output_file = 'cleaned_prices.csv'
cleaned_data = process_data(input_file, output_file)
plot_histogram(cleaned_data)
