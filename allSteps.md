Here is a step-by-step guide to creating a basic Python project with a simple Flask-based UI that interacts with an SQLite database, performing GET and POST operations.

### Step 1: Set Up Project Directory

First, create a directory for your project. You can name it anything you like. Here’s an example:

```bash
mkdir my_flask_app
cd my_flask_app
```

### Step 2: Install Flask

Create a virtual environment and install Flask inside it to keep your project dependencies organized.

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Flask and mysql
pip install Flask

pip install mysql-connector-python

```

### Step 3: Create `app.py` (Main Python File)

In your project directory, create a new Python file called `app.py`.

```bash
touch app.py
```

Inside `app.py`, paste the following code:

```python
from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# MySQL Database connection parameters
db_config = {
    'user': 'your_username',      # Update with your MySQL username
    'password': 'your_password',  # Update with your MySQL password
    'host': 'localhost',
    'database': 'your_database'   # Ensure this database exists in MySQL
}

# Initialize the MySQL Database
def init_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create a table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# Route to show data and form
@app.route('/',methods=['GET'])
def index():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    return render_template('index.html', users=rows)

# Route to add data
@app.route('/add', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
    conn.commit()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    app.run(debug=True)
```

### Step 4: Create `templates/index.html`

Create a `templates` folder in your project directory. This folder will store your HTML files.

```bash
mkdir templates
```

Now, inside the `templates` folder, create a file named `index.html`.

```bash
touch templates/index.html
```

Open `index.html` and paste the following HTML code:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask App</title>
</head>
<body>
    <h1>User List</h1>

    <!-- User Form -->
    <form action="/add" method="POST">
        <label for="name">Name:</label>
        <input type="text" name="name" required><br>
        <label for="email">Email:</label>
        <input type="email" name="email" required><br>
        <button type="submit">Add User</button>
    </form>

    <!-- Display Users -->
    <h2>Users:</h2>
    <ul>
        {% for user in users %}
        <li>{{ user[1] }} - {{ user[2] }}</li>
        {% endfor %}
    </ul>
</body>
</html>
```

### Step 5: Run the Flask App

Once you have the `app.py` and `index.html` files in place, you can run the Flask app.

1. Ensure that you're still in your project directory.
2. Run the app using the following command:

```bash
python app.py
```

You should see output similar to this:

```bash
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

### Step 6: Access the App in the Browser

1. Open your web browser.
2. Go to `http://127.0.0.1:5000/`.
3. You should see a form where you can enter a **name** and **email** and a list displaying users.
4. Submit the form, and the user will be added to the SQLite database and displayed on the page.

### Step 7: Optional Styling (Create `static/style.css`)

If you want to add some simple styling to the page, you can create a `static` folder and add a `style.css` file.

```bash
mkdir static
touch static/style.css
```

Inside `style.css`, you can add basic styling like this:

```css
body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    padding: 20px;
}

form {
    margin-bottom: 20px;
}

input {
    padding: 8px;
    margin: 5px;
}

button {
    padding: 10px;
    background-color: #28a745;
    color: white;
    border: none;
    cursor: pointer;
}

button:hover {
    background-color: #218838;
}
```

To include this stylesheet in your HTML, update the `<head>` section of `index.html` like so:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
```

### Step 8: View Database (Optional)

The SQLite database `database.db` will be created in your project directory. You can open this file using an SQLite viewer, such as DB Browser for SQLite, to view the stored data.

### Step 9: Shut Down the App

To stop the Flask app, go back to your terminal and press `CTRL + C`.

---

### Summary of Steps:
1. **Set up the project directory.**
2. **Install Flask and create a virtual environment.**
3. **Create `app.py` (main Python app).**
4. **Create `templates/index.html` (HTML file for UI).**
5. **Run the Flask app and open it in a browser.**
6. **Optional: Add a `style.css` file for styling.**
7. **Optional: View the SQLite database using a tool like DB Browser.**

This is a basic Flask app setup for performing simple GET and POST operations with a database.