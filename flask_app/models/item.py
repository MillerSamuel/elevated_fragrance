from flask_app.config.mysqlconnection import MySQLConnection, connectToMySQL
from flask_app import app


class Item:
    def __init__(self,data):
        self.id=data["id"]
        self.name=data["name"]
        self.img=data["img"]
        self.tags=data["tags"]
        self.price=data["price"]
        self.user_id=data["user_id"]


    @classmethod
    def get_all(cls):
        query = "SELECT * FROM items;"
        results = connectToMySQL('elevated_fragrence').query_db(query)
        items = []
        for item in results:
            items.append( cls(item) )
        return items

    @classmethod
    def get_one_id(cls,data):
        query="SELECT * FROM items WHERE id= %(item_id)s"
        results = connectToMySQL('elevated_fragrence').query_db(query,data)
        return cls(results[0])

    @classmethod
    def get_search(cls,data):
        query="SELECT * FROM items WHERE name LIKE  %(search)s"
        print(data["search"])
        print ("%(search)s")
        results = connectToMySQL('elevated_fragrence').query_db(query,data)
        items = []
        for item in results:
            items.append( cls(item) )
        return items

