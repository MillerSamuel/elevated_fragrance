from flask_app import app
from flask_app.models.user import User
from flask_app.models.item import Item
from flask import render_template, session,flash,redirect,request
from flask_bcrypt import Bcrypt        
bcrypt = Bcrypt(app)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/newuser",methods=["post"])
def adduser():
    if User.validate_new(request.form):
        pw_hash=bcrypt.generate_password_hash(request.form["password"])
        data={
            "first_name":request.form["first_name"],
            "last_name":request.form["last_name"],
            "email":request.form["email"],
            "password":pw_hash,
            "confirm":request.form["confirm"],
        }
        User.add_new(data)
        logged_user=User.get_by_email(request.form)
        session['user_id'] = logged_user.id
        return redirect("/dashboard")
    return redirect("/")

@app.route('/login', methods=['POST'])
def login():
    if  User.validate_login(request.form):
        logged_user=User.get_by_email(request.form)
        session['user_id'] = logged_user.id
        return redirect("/dashboard")
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if session.get("user_id")==None:
        return redirect("/")
    items=Item.get_all()
    return render_template("dashboard.html",items=items)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/detail<int:item_id>")
def detail(item_id):
    data={
        "item_id":item_id
    }
    item=Item.get_one_id(data)
    return render_template("detail.html", item=item)

@app.route("/addcart<int:item_id>")
def addcart(item_id):
    data={
        "user_id":session["user_id"],
        "item_id":item_id
    }
    if User.add_cart(data)==False:
        return redirect("/dashboard")
    return redirect("/cart")

@app.route("/cart")
def cart():
    data={
        "user_id":session["user_id"]
    }
    user=User.get_cart(data)
    return render_template("cart.html",user=user)

@app.route("/find",methods=["post"])
def find():
    session["search"]=request.form["search"]
    if session["search"]=="":
        return redirect("/dashboard")
    return redirect("/search")

@app.route("/search")
def search():
    data={
        "search":session["search"]
    }
    items=Item.get_search(data)
    return render_template("dashboard.html",items=items)

@app.route("/remove<int:item_id>")
def remove(item_id):
    data={
        "item_id":item_id,
        "user_id":session["user_id"]
    }
    User.remove(data)
    return redirect("/cart")