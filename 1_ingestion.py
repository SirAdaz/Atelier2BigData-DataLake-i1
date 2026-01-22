"""Script d'ingestion : Simule l'arrivée de nouveaux fichiers dans Bronze"""
import json
import os
import random
from datetime import datetime, timedelta

from faker import Faker

from utils import Sale, Review


def remove_files_from_dir(dir_name: str):
    dir_path = os.path.join(os.getcwd(), dir_name)
    if not os.path.exists(dir_path):
        print("Error : No such file or directory : "+ dir_path)
        return
    for file in os.listdir(dir_path):
        os.remove(os.path.join(dir_path, file))
    print("folder cleaned")

def create_sale(nb_file: int, nb_product: int, date, faker):
    # product_id, prix, date, client
    product_id = nb_file * 1000 + nb_product
    price = random.randint(1, 99999)/ 100 # gives us a random decimal value between 0.00 and 999.99 (included)
    return Sale(product_id, price, date, faker.name())

def create_sales_data(nb_files: int, faker) -> list[int]:
    """
    Creates multiple random sales across multiple files
    :param nb_files: the number of files that should be created
    :return: the list of all the product ids
    """
    product_ids = []

    for f in range(nb_files):
        date_of_file = (datetime.now() - timedelta(days=f)).strftime("%m-%d-%Y")
        nb_sales = random.randint(3,10)
        with open("./bronze/sales_data_"+date_of_file+".csv","w") as file:
            file.write("product_id,price,date,client\n")

            for p in range(nb_sales):
                sale = create_sale(f,p,date_of_file, faker)

                file.write(sale.to_csv_line())
                product_ids.append(sale.product_id)

    return product_ids

def create_review(product_id: int, faker):
    grade = random.randint(1,5)
    comment = faker.catch_phrase()
    return Review(grade, comment, product_id)

def create_review_data(product_ids: list[int], nb_files: int, faker):
    for f in range(nb_files):
        date_of_file = (datetime.now() - timedelta(days=f)).strftime("%m-%d-%Y")
        nb_reviews = random.randint(3,10)

        with open("./bronze/review_data_"+date_of_file+".json","w") as file:

            reviews = []
            for r in range(nb_reviews):
                p_id = random.choice(product_ids)
                review = create_review(p_id, faker)
                reviews.append(review.to_json())

            json.dump(reviews, file, ensure_ascii=False, indent=4)

def create_data():
    faker = Faker()
    os.makedirs("bronze", exist_ok=True)
    nb_files = random.randint(2,15)

    products_ids = create_sales_data(nb_files, faker)
    create_review_data(products_ids, nb_files, faker)
    print("data generated")

remove_files_from_dir("bronze")
create_data()
