from flask import Flask, redirect, url_for, render_template, request, flash, session, jsonify
from extensions import db
from users import add_user, verify_user, update_password
from models import User, Order, OrderItem, Address,Subscriber
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import uuid
import os



app = Flask(__name__)
# app.secret_key = "sneha123"
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "fallback-secret"
) 

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///users.db"   # local fallback
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
with app.app_context():
    db.create_all()

# admin = Admin(app, name="Nakhrali Admin", template_mode="bootstrap4")
admin = Admin(app, name="Nakhrali Admin")


class SecureModelView(ModelView):
    def is_accessible(self):
        return session.get("is_admin")

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login"))
admin.add_view(SecureModelView(User, db.session))
admin.add_view(SecureModelView(Order, db.session))
admin.add_view(SecureModelView(OrderItem, db.session))
admin.add_view(SecureModelView(Address, db.session))
admin.add_view(SecureModelView(Subscriber, db.session))



# ---------------- ROUTES ----------------
@app.route("/")
def welcome():
    return render_template("index.html")

@app.route("/auth")
def auth():
    return render_template("auth.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = verify_user(email, password)

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]

            # 🔐 STEP 4: ADMIN FLAG SET
            if email == "admin@gmail.com":   # change to your admin email
                session["is_admin"] = True
            else:
                session["is_admin"] = False

            return redirect(url_for("home"))

        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        location = request.form["location"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        dob = request.form["dob"]
        gender = request.form["gender"]

        if password != confirm_password:
            error = "Passwords do not match"
            return render_template("register.html", error=error)

        if add_user(name, email, phone, location, password, dob, gender):
            return redirect(url_for("login"))

        error = "User already exists"

    return render_template("register.html", error=error)

# ---------------- HOME ----------------
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("home.html", username=session.get("username"))

@app.route("/logout")
def logout():
    session.clear()          # 🔐 sab session data clear
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))


# ---------------- STATIC PAGES ----------------
@app.route("/wishlist")
def wishlist_page():
    return render_template("wishlist.html")

@app.route("/cart")
def cart_page():
    return render_template("cart.html")

@app.route("/checkout")
def checkout():
    return render_template("checkout.html")

@app.route("/order-success")
def order_success():
    return render_template("order-success.html")

@app.route("/location")
def location():
    return render_template("location.html")

@app.route("/home/customer-service")
def customer_service():
    return render_template("customer-service.html")


@app.route("/search")
def search():
    query = request.args.get("q", "").lower()

    if not query:
        return redirect("/home/sarees")

    filtered_products = [
        p for p in sarees_data
        if query in p["name"].lower()
    ]

    return render_template(
        "sarees.html",
        products=filtered_products,
        search_query=query
    )

# ---------------- PROFILE ----------------
@app.route("/profile", defaults={"section": "profile"}, methods=["GET", "POST"])
@app.route("/profile/<section>", methods=["GET", "POST"])
def profile(section):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        return redirect(url_for("login"))

    # Change password
    if section == "change-password" and request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]

        if not check_password_hash(user.password, current_password):
            flash("❌ Current password incorrect", "error")
        else:
            update_password(user.id, new_password)
            flash("✅ Password updated. Login again.", "success")
            session.clear()
            return redirect(url_for("login"))

    return render_template(
        "profile.html",
        user=user,
        section=section,
        orders=user.orders
    )

# ---------------- ADDRESS ----------------
@app.route("/add_address", methods=["POST"])
def add_address():
    if "user_id" not in session:
        return redirect("/login")

    addr = Address(
        user_id=session["user_id"],
        address=request.form["address"],
        city=request.form["city"],
        state=request.form["state"],
        pincode=request.form["pincode"]
    )

    db.session.add(addr)
    db.session.commit()

    flash("✅ Address added successfully!", "success")
    return redirect("/profile/address")

@app.route("/delete_address/<int:address_id>")
def delete_address(address_id):
    if "user_id" not in session:
        return redirect("/login")

    addr = Address.query.get(address_id)
    if addr:
        db.session.delete(addr)
        db.session.commit()

    flash("🗑️ Address deleted", "info")
    return redirect("/profile/address")
from flask import jsonify, request

@app.route("/place-order", methods=["POST"])
def place_order():

    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    data = request.get_json(force=True)
    print("RECEIVED DATA 👉", data)   # 🔍 DEBUG

    cart = data.get("cart")
    total = data.get("total")

    if not cart or not total:
        return jsonify({"success": False, "error": "Missing cart or total"}), 400

    user_id = session["user_id"]

    order = Order(
        order_id="NKH" + uuid.uuid4().hex[:8].upper(),
        user_id=user_id,
        total_amount=total,
        payment_method="COD"
    )

    db.session.add(order)
    db.session.commit()

    for item in cart:
        order_item = OrderItem(
            order_id=order.id,
            product_name=item["name"],
            price=item["price"],
            quantity=item["quantity"]
        )
        db.session.add(order_item)

    db.session.commit()

    print("✅ ORDER SAVED, RETURNING JSON")

    return jsonify({"success": True,
                    "order_id": order.order_id,
                    "total": order.total_amount,
                    "payment_method": "Cash on Delivery"})

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    users = get_all_users()
    return render_template("dashboard.html", users=users)

# ---------------- SUBSCRIBE ----------------
@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")

    if not email:
        flash("Please enter a valid email", "error")
        return redirect(url_for("home"))

    try:
        new_subscriber = Subscriber(email=email)
        db.session.add(new_subscriber)
        db.session.commit()
        flash("🎉 You have successfully subscribed to Nakhrali!", "success")

    except IntegrityError:
        db.session.rollback()
        flash("⚠️ This email is already subscribed", "warning")

    except Exception as e:
        db.session.rollback()
        flash("❌ Something went wrong. Please try again.", "error")

    return redirect(url_for("home"))


# ---------------- PRODUCTS ----------------
sarees_data = [
    {"id": 1, "name": "MulMul Cotton Saree", "price": 700, "rating": 5,
     "image1": "images/cotton-saree1.jpg", "image2": "images/cotton-saree2.jpg"},

    {"id": 2, "name": "Silk Saree", "price": 1200, "rating": 4,
     "image1": "images/silk.jpg", "image2": "images/silk2.jpg"},

     {"id": 3, "name": "Modal Silk Saree", "price": 1700, "rating": 5,
     "image1": "images/modal-silk.jpg", "image2": "images/modal-silk2.jpg"},

     {"id": 4, "name": "Maheshwari Cotton Silk Saree", "price": 2700, "rating": 4,
     "image1": "images/maheshwari.jpg", "image2": "images/maheshwari.jpg"},

     {"id": 5, "name": "Silk Saree", "price": 700, "rating": 5,
     "image1": "images/silk-saree2.jpg", "image2": "images/silk-saree2.jpg"},

     {"id": 6, "name": "Banarasi Saree", "price": 2780, "rating": 5,
     "image1": "images/banarasi.jpg", "image2": "images/banarasi2.jpg"},

     {"id": 7, "name": "Bandhani Saree", "price": 3700, "rating": 3,
     "image1": "images/bandhani.jpg", "image2": "images/bandhani2.jpg"},

     {"id": 8, "name": "Jaipuri Saree", "price": 850, "rating": 4,
     "image1": "images/jaipuri.jpg", "image2": "images/jaipuri.jpg"},
]
suits_data = [
    {
        "id": 1,
        "name": "Cotton Printed Suit Set",
        "price": 1500,
        "rating": 5,
        "image1": "images/suit1.jpg",
        "image2": "images/suit1.jpg"
    },
    {
        "id": 2,
        "name": "Silk Embroidered Suit Set",
        "price": 2200,
        "rating": 4,
        "image1": "images/suit2.jpg",
        "image2": "images/suit2.jpg"
    },
    {
        "id": 3,
        "name": "Chanderi Suit Set",
        "price": 1800,
        "rating": 5,
        "image1": "images/suit3.jpg",
        "image2": "images/suit3.jpg"
    }
]
@app.route("/home/suits")
def suits():
    return render_template("suits.html", products=suits_data)


@app.route("/home/sarees")
def sarees():
    return render_template("sarees.html", products=sarees_data)

@app.route("/saree/<int:product_id>")
def saree_detail(product_id):
    product = next((p for p in sarees_data if p["id"] == product_id), None)
    return render_template("saree_detail.html", product=product) if product else ("Not Found", 404)

# ---------------- INIT ----------------
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
