import os
import mysql.connector
from flask import Flask, render_template, request, redirect, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename 
from datetime import timedelta
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
# socketio = SocketIO(app, cors_allowed_origins="*")


# UPLOAD_FOLDER = 'uploads/'  # Folder to store uploaded images
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
CORS(app, resources={r"/uploads/": {"origins": "*"}})

# MySQL Database connection parameters
db_config = {
    'user': 'root',      # Update with your MySQL username
    'password': 'your_password',  # Update with your MySQL password
    'host': 'localhost',
    'database': 'sys'   # Ensure this database exists in MySQL
}

# CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)
# # Initialize the MySQL Database
# def init_db():
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor()

#     # Create a table if it does not exist
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS user (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             name VARCHAR(255) NOT NULL,
#             email VARCHAR(255) NOT NULL
#         );
#     ''')
#     conn.commit()
#     conn.close()

######## Route to add user data
@app.route('/api/signup/community', methods=['POST'])
def signup_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    address = data.get('address')
    acc_type = data.get('role')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO admin (username, email, password, phone_number, address, acc_type) VALUES (%s, %s, %s, %s, %s, %s)",
            (username, email, password, phone_number, address, acc_type))
        conn.commit()
        user_id=cursor.lastrowid
        if acc_type == 'resto':
            resto_in(user_id, username, email, phone_number, address)
        elif acc_type == 'contributor':
            contributor_in(user_id, username, email, phone_number, address)
        elif acc_type == 'customer':
            customer_in(user_id, username, email, phone_number, address)
        return jsonify({"message": "User registered successfully!"}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    
    finally:
        cursor.close()
        conn.close()
    return redirect('/')
    
def resto_in(user_id, username, email, phone_number, address):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO restaurant_owner (user_id, username, email, phone_number, address) VALUES (%s, %s, %s, %s, %s)", (user_id, username, email, phone_number, address))
    conn.commit()

def contributor_in(user_id, username, email, phone_number, address):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contributor (user_id, username, email, phone_number, address) VALUES (%s, %s, %s, %s, %s)", (user_id, username, email, phone_number, address))
    conn.commit()

def customer_in(user_id, username, email, phone_number, address):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customer (user_id, username, email, phone_number, address) VALUES (%s, %s, %s, %s, %s)", (user_id, username, email, phone_number, address))
    conn.commit()


####Route to fetch user data
@app.route('/api/community', methods=['GET'])
def get_community():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM admin")
        rows = cursor.fetchall()
        return jsonify(rows)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        conn.close()

###api for login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()

    if user:
        return jsonify({"message": "Login successful", "user": user}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


##Route to store restaurants data
@app.route('/api/restaurants', methods=['POST'])
def add_restaurant():
    filename = None  

    if 'restaurant_logo' in request.files:
        file = request.files['restaurant_logo']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    resto_id = request.form.get('resto_id') 
    restaurant_name = request.form.get('restaurant_name')
    cuisine_type = request.form.get('cuisine_type')
    opening_time = request.form.get('opening_time')
    closing_time = request.form.get('closing_time')
    phone_number = request.form.get('phone_number')
    address = request.form.get('address')
    rating = request.form.get('rating', '0')  # Default to '0' if not provided
    status = request.form.get('status', 'open')  # Default to 'open' if not provided
    average_rating = request.form.get('average_rating', '0')  # Default to '0'
    total_ratings_count = request.form.get('total_ratings_count', '0')  # Default to '0'
    print("fileName",filename)
    restaurant_logo = f'http://127.0.0.1:5000/uploads/{filename}'
    print("restaurant_logo 22",restaurant_logo)

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:

        # Insert the restaurant details into the database
        cursor.execute('''
            INSERT INTO restaurant (resto_id, restaurant_name, cuisine_type, opening_time, closing_time, rating, status, restaurant_logo, phone_number, address, average_rating, total_ratings_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (resto_id, restaurant_name, cuisine_type, opening_time, closing_time, rating, status, filename, phone_number, address, average_rating, total_ratings_count))

        conn.commit()

        return jsonify({'message': 'Upload successful', 'filename': filename}), 200
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Database error', 'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

## Route to delete restaurant by its id
@app.route('/api/deleteRestaurant/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM restaurant WHERE restaurant_id = %s', (restaurant_id,))
        conn.commit()

        if cursor.rowcount > 0:
            return jsonify({"message": f"Restaurant with ID {restaurant_id} deleted successfully"}), 200
        else:
            return jsonify({"message": f"No restaurant found with ID {restaurant_id}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


###Route to fetch data from restaurant_owner based on user_id
@app.route('/api/resto/<int:user_id>', methods=['GET'])
def get_resto_by_id(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM restaurant_owner WHERE user_id = %s", (user_id,))
        owner = cursor.fetchone()

        if owner:
            return jsonify(owner), 200
        else:
            return jsonify({"message": "Owner not found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()


###Route to fetch all restaurants based on resto_id
@app.route('/api/restaurantDetails/<int:resto_id>', methods=['GET'])
def get_allresto_by_id(resto_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True,buffered=True)
        cursor.execute("SELECT * FROM restaurant WHERE resto_id = %s", (resto_id,))
        restoDetails = cursor.fetchall()

        for restaurant in restoDetails:
            for key, value in restaurant.items():
                if isinstance(value, timedelta):
                    restaurant[key] = str(value)

        if  restoDetails:           
            return jsonify(restoDetails), 200
        else:
            return jsonify({"message": "restoDetails not found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()


###Route to fetch all restaurants for user
@app.route('/api/allRestaurantDetails', methods=['GET'])
def get_all_restos():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True,buffered=True)
        cursor.execute("SELECT * FROM restaurant")
        allRestoDetails = cursor.fetchall()
        for restaurant in allRestoDetails:
            for key, value in restaurant.items():
                if isinstance(value, timedelta):
                    restaurant[key] = str(value)

        if  allRestoDetails:           
            return jsonify(allRestoDetails), 200
        else:
            return jsonify({"message": "Restaurant Details not found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()


# Convert any timedelta objects in the restaurant data
def serialize(obj):
    if isinstance(obj, timedelta):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")    


###Route to fetch a particular restaurants based on restarant_id
@app.route('/api/restaurant/<int:restaurant_id>', methods=['GET'])
def get_restarant_by_id(restaurant_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True,buffered=True)
        cursor.execute("SELECT * FROM restaurant WHERE restaurant_id = %s", (restaurant_id,))
        restarantDetails = cursor.fetchall()

        for restaurant in restarantDetails:
            for key, value in restaurant.items():
                if isinstance(value, timedelta):
                    restaurant[key] = str(value)

        if  restarantDetails:           
            return jsonify(restarantDetails), 200
        else:
            return jsonify({"message": "Restarant details not found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()


###Route to fetch all Contributor details for user
@app.route('/api/allContributorDetails', methods=['GET'])
def get_all_contributors():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True,buffered=True)
        cursor.execute("SELECT * FROM contributor")
        allContributorDetails = cursor.fetchall()
        
        for contributor in allContributorDetails:
            for key, value in contributor.items():
                if isinstance(value, timedelta):
                    contributor[key] = str(value)

        if  allContributorDetails:           
            return jsonify(allContributorDetails), 200
        else:
            return jsonify({"message": "Contributor Details not found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# Determine whether the source is a restaurant or contributor
@app.route('/api/addFood', methods=['POST'])
def adding_food_details():
    filename = None
    if 'food_image' in request.files:
        file = request.files['food_image']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    food_name = request.form.get('food_name') 
    food_description = request.form.get('food_description')
    quantity_available = request.form.get('quantity_available')
    food_type = request.form.get('food_type')
    leftover_status = request.form.get('leftover_status')
    expiry_time = request.form.get('expiry_time')
    average_rating = request.form.get('average_rating', '0') 
    total_ratings_count = request.form.get('total_ratings_count', '0')

    if filename:
        food_image = f'http://127.0.0.1:5000/uploads/{filename}'
    else:
        food_image = None
    print("food_image", food_image)

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        if request.form.get('restaurant_id'):
            source_id = request.form.get('restaurant_id')
            query = """INSERT INTO food (food_name, food_description, quantity_available, food_type, leftover_status, 
                        food_image, restaurant_id, expiry_time, average_rating, total_ratings_count) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (food_name, food_description, quantity_available, food_type, leftover_status, 
                                food_image, source_id, expiry_time, average_rating, total_ratings_count))
        elif request.form.get('contributor_id'):
            source_id = request.form.get('contributor_id')
            query = """INSERT INTO food (food_name, food_description, quantity_available, food_type, leftover_status, 
                        food_image, contributor_id, expiry_time, average_rating, total_ratings_count) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (food_name, food_description, quantity_available, food_type, leftover_status, 
                                food_image, source_id, expiry_time, average_rating, total_ratings_count))
        else:
            return jsonify({"error": "Either restaurant_id or contributor_id must be provided"}), 400

        conn.commit()
        return jsonify({"message": "Food Item added successfully"}), 201
    
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    
    finally:
        cursor.close()
        conn.close()


@app.route('/api/getFoodDetails', methods=['GET'])
def get_all_food_details():
    restaurant_id = request.args.get('restaurant_id')
    contributor_id = request.args.get('contributor_id')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    try:
        if restaurant_id:
            query = """SELECT * FROM food WHERE restaurant_id = %s"""
            cursor.execute(query, (restaurant_id,))
        elif contributor_id:
            query = """SELECT * FROM food WHERE contributor_id = %s"""
            cursor.execute(query, (contributor_id,))
        else:
            return jsonify({"error": "Please provide either restaurant_id or contributor_id"}), 400

        food_details = cursor.fetchall()
        return jsonify(food_details), 200

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()


# ###Route to fetch all food items list based on restaurant_id
@app.route('/api/foodList', methods=['GET'])
def get_food_by_iddd():
    restaurant_id = request.args.get('restaurant_id')
    contributor_id = request.args.get('contributor_id')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True,buffered=True)
    try:
        if restaurant_id:
            query = """SELECT * FROM food WHERE restaurant_id = %s"""
            cursor.execute(query, (restaurant_id,))
        elif contributor_id:
            query = """SELECT * FROM food WHERE contributor_id = %s"""
            cursor.execute(query, (contributor_id,))
        foodList = cursor.fetchall()

        for food in foodList:
            for key, value in food.items():
                if isinstance(value, timedelta):
                    food[key] = str(value)

        if  foodList:           
            return jsonify(foodList), 200
        else:
            return jsonify({"message": "Food List not found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/getFoodItems', methods=['GET'])
def get_food_items():
    restaurant_id = request.args.get('restaurant_id')
    contributor_id = request.args.get('contributor_id')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    try:
        if restaurant_id:
            query = """SELECT * FROM food WHERE restaurant_id = %s"""
            cursor.execute(query, (restaurant_id,))
        elif contributor_id:
            query = """SELECT * FROM food WHERE contributor_id = %s"""
            cursor.execute(query, (contributor_id,))
        else:
            return jsonify({"error": "restaurant_id or contributor_id is required"}), 400

        food_items = cursor.fetchall()

        if food_items:
            return jsonify(food_items), 200
        else:
            return jsonify({"message": "No food items found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()



@app.route('/api/updateFood/<int:food_id>', methods=['PUT', 'OPTIONS'])
def update_food(food_id):
    if request.method == 'OPTIONS':
        return '', 200
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        filename = None

        if 'food_image' in request.files:
            file = request.files['food_image']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        food_name = request.form.get('food_name') 
        food_description = request.form.get('food_description')
        quantity_available = request.form.get('quantity_available')
        food_type = request.form.get('food_type')
        leftover_status = request.form.get('leftover_status')
        expiry_time = request.form.get('expiry_time')

        food_image = f'http://127.0.0.1:5000/uploads/{filename}' if filename else request.form.get('food_image')

        # Check which ID is provided (restaurant_id or contributor_id)
        restaurant_id = request.form.get('restaurant_id')
        contributor_id = request.form.get('contributor_id')
        
        # Build the query
        query = """UPDATE food
                   SET food_name = %s, food_description = %s, quantity_available = %s, food_type = %s, leftover_status = %s, 
                       food_image = %s, expiry_time = %s, updated_at = NOW()"""
        
        params = [food_name, food_description, quantity_available, food_type, leftover_status, food_image, expiry_time]

        # Conditionally update either restaurant_id or contributor_id
        if restaurant_id:
            query += ", restaurant_id = %s"
            params.append(restaurant_id)
        elif contributor_id:
            query += ", contributor_id = %s"
            params.append(contributor_id)

        # Add the WHERE clause to update the correct food item
        query += " WHERE food_id = %s;"
        params.append(food_id)
        
        # Execute the query
        cursor.execute(query, params)
        conn.commit()

        # Check if any rows were affected
        if cursor.rowcount == 0:
            return jsonify({'message': 'Food item not found!'}), 404
        return jsonify({'message': 'Food Details updated!'}), 200

    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


## Route to delete food item by its id
@app.route('/api/deleteFood/<int:food_id>', methods=['DELETE'])
def delete_foodItem(food_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Delete query, ensuring it targets the correct food_id in food table
        cursor.execute('DELETE FROM food WHERE food_id = %s', (food_id,))
        conn.commit()

        if cursor.rowcount > 0:
            return jsonify({"message": f"Food item deleted successfully"}), 200
        else:
            return jsonify({"message": f"No food item found with ID"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


#Route to fetch 
@app.route('/api/contributor/<int:user_id>', methods=['GET'])
def get_contributor_by_id(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True,buffered=True)
        cursor.execute("SELECT * FROM contributor WHERE user_id = %s", (user_id,))
        owner = cursor.fetchall()

        if owner:
            return jsonify(owner), 200
        else:
            return jsonify({"message": "Contributor not found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()


###Route to fetch data from customer based on user_id
@app.route('/api/customer/<int:cust_id>', methods=['GET'])
def get_user_by_id(cust_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customer WHERE user_id = %s", (cust_id,))
        customer = cursor.fetchone()

        if customer:
            return jsonify(customer), 200
        else:
            return jsonify({"message": "Customer not found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()


##Route to place order by customer
@app.route('/api/placeOrder', methods=['POST', 'OPTIONS'])
def place_order():
    if request.method == 'OPTIONS':
        return 'Options', 200

    data = request.json
    customer_id = data.get('customer_id')
    cart_items = data.get('cartItems')

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    try:
        # Step 1: Insert into order_details
        cursor.execute("INSERT INTO order_details (customer_id) VALUES (%s)", (customer_id,))
        order_id = cursor.lastrowid  # Get the newly created order ID
        print("New order created with order_id:", order_id)

        # Step 2: Loop through each food item and insert into order_food_item
        for item in cart_items:
            food_id = item['food_id']
            quantity_ordered = item['order_quantity']

            try:
                print("Processing food_id:", food_id)
                print("Requested quantity:", quantity_ordered)

                cursor.execute("SELECT quantity_available FROM food WHERE food_id = %s FOR UPDATE", (food_id,))
                result = cursor.fetchone()

                if result is None:
                    return jsonify({"error": f"Food item with id {food_id} not found"}), 404

                quantity_available = result['quantity_available']
                print("Available quantity:", quantity_available)

                if quantity_ordered > quantity_available:
                    return jsonify({"error": f"Not enough quantity for food_id {food_id}"}), 400

                # Insert the food item into order_food_item table
                cursor.execute("INSERT INTO order_food_item (order_id, food_id, quantity_ordered) VALUES (%s, %s, %s)", (order_id, food_id, quantity_ordered))

                # Update the quantity_available in food_detail
                cursor.execute("UPDATE food SET quantity_available = quantity_available - %s WHERE food_id = %s", (quantity_ordered, food_id))

                # If quantity_available reaches 0, mark as Not Available
                cursor.execute("UPDATE food SET leftover_status = 'Not Available' WHERE food_id = %s AND quantity_available = 0", (food_id,))

            except Exception as e:
                print(f"An error occurred while processing food_id {food_id}: {str(e)}")
                connection.rollback()
                return jsonify({"error": "An error occurred while placing the order."}), 500

        connection.commit() 
        socketio.emit('new_order', {'order_data': data})

        return jsonify({"message": "Order placed successfully"}), 200

    except Exception as e:
        connection.rollback()
        print("An error occurred while placing the order:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    # init_db()  # Initialize the database when the app starts
    app.run(debug=True)
