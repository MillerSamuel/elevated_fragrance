from pickle import FALSE
from flask_app.config.mysqlconnection import MySQLConnection, connectToMySQL
from flask import flash, redirect
from flask_app.models.item import Item
from flask_app import app
from flask_bcrypt import Bcrypt
import re
bcrypt = Bcrypt(app)

email_regex=re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class User:
    def __init__(self,data):
        self.id=data["id"]
        self.first_name=data["first_name"]
        self.last_name=data["last_name"]
        self.email=data["email"]
        self.password=data["password"]
        self.created_at=data["created_at"]
        self.updated_at=data["updated_at"]
        self.items=[]


    @classmethod
    def add_new(cls,data):
        query="INSERT INTO users (first_name, last_name,email,password,created_at,updated_at) VALUES(%(first_name)s,%(last_name)s,%(email)s,%(password)s,NOW(),NOW())"
        return connectToMySQL("elevated_fragrence").query_db(query,data)

    @classmethod
    def get_by_email(cls,data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL("elevated_fragrence").query_db(query,data)
        # Didn't find a matching user
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def get_by_id(cls,data):
        query = "SELECT * FROM users WHERE id = %(user_id)s;"
        result = connectToMySQL("elevated_fragrence").query_db(query,data)
        # Didn't find a matching user
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def get_cart(cls,data):
        query="SELECT * FROM items LEFT JOIN cart ON cart.item_id=items.id LEFT JOIN users ON cart.user_id=users.id WHERE users.id= %(user_id)s "
        results = connectToMySQL("elevated_fragrence").query_db(query,data)
        if results==():
            return False
        user=cls(results[0])
        for row_from_db in results:
            item_data={
                "id":row_from_db["id"],
                "name":row_from_db["name"],
                "img":row_from_db["img"],
                "tags":row_from_db["tags"],
                "price":row_from_db["price"],
                "user_id":row_from_db["user_id"],
            }
            user.items.append(Item(item_data))
        return user
    
    @classmethod
    def add_cart(cls,data):
        user=User.get_cart(data)
        if user==False:
            query="INSERT INTO cart (user_id, item_id) VALUES(%(user_id)s,%(item_id)s)"
            flash("*Added to Cart*")
            return connectToMySQL("elevated_fragrence").query_db(query,data)
        for one_item in user.items:
            if one_item.id==data["item_id"]:
                flash ("*Already In Cart*")
                return False
        query="INSERT INTO cart (user_id, item_id) VALUES(%(user_id)s,%(item_id)s)"
        flash("*Added to Cart*")
        return connectToMySQL("elevated_fragrence").query_db(query,data)

    @classmethod
    def remove(cls,data):
        query="DELETE FROM cart WHERE user_id=%(user_id)s and item_id= %(item_id)s"
        return connectToMySQL("elevated_fragrence").query_db(query,data)



    @staticmethod
    def validate_new(data):
        is_valid=True
        if len(data["first_name"])<3:
            is_valid=False
            flash("*First name must be atleast 3 characters*")
        if len(data["last_name"])<3:
            is_valid=False
            flash("*Last name must be atleast 3 characters*")
        if len(data["email"])<3:
            is_valid=False
            flash("*Email must be atleast 3 characters*")
        if not email_regex.match(data["email"]):
            is_valid=False
            flash("*Please enter a valid email*")
        if User.get_by_email(data):
            is_valid=False
            flash("*Email already in use*")
        
        if len(data["password"])<8:
            is_valid=False
            flash("*Password must be atleast 8 characters*")
        if data["password"]!=data["confirm"]:
            is_valid=False
            flash("*Password did not match confirmation*")
        return is_valid

    @staticmethod
    def validate_login(data):
        user_in_db = User.get_by_email(data)
        is_valid=True
    # user is not registered in the db
        if not user_in_db:
            flash("Invalid Email/Password")
            is_valid=False
        elif not bcrypt.check_password_hash(user_in_db.password, data['password']):
        # if we get False after checking the password
            flash("Invalid Email/Password")
            is_valid=False
        return is_valid