class Sale():
    def __init__(self, product_id, price, date, client):
        self.product_id = product_id
        self.price = price
        self.date = date
        self.client = client

    def to_csv_line(self):
        return str(self.product_id) +", "+ str(self.price) +", "+ str(self.date) +", "+ str(self.client) +"\n"

class Review():
    def __init__(self, grade, comment, product_id):
        self.grade = grade
        self.comment = comment
        self.product_id = product_id

    def to_json(self):
        return {"grade" : self.grade, "comment" : self.comment, "product_id" : self.product_id}