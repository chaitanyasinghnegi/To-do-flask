import mysql.connector
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# Replace these with your database credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql',
    'database': 'my_database',
}

def create_database_if_not_exists():
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS " + db_config['database'])
    except Exception as e:
        print(f"Error creating the database: {str(e)}")

def create_table_if_not_exists():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            task_name VARCHAR(255) NOT NULL,
            status BOOLEAN NOT NULL DEFAULT 0,
            date_added DATETIME,
            task_description TEXT
        )
        """
        cursor.execute(create_table_query)
    except Exception as e:
        print(f"Error creating the table: {str(e)}")

create_database_if_not_exists()
create_table_if_not_exists()
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

@app.route('/add_task', methods=['POST'])
def add_task():
    task_name = request.form['task_name']
    task_description = request.form['task_description'] if 'task_description' in request.form else None
    insert_query = "INSERT INTO tasks (task_name, status, date_added, task_description) VALUES (%s, %s, NOW(), %s)"
    cursor.execute(insert_query, (task_name, False, task_description))
    conn.commit()
    return redirect(url_for('show_tasks'))

@app.route('/')
def show_tasks():
    select_query = "SELECT id, task_name, status, date_added, task_description FROM tasks"
    cursor.execute(select_query)
    tasks = cursor.fetchall()
    return render_template('index.html', tasks=tasks)

@app.route('/update_task/<int:task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    if request.method == 'GET':
        # Fetch the task from the database and render the edit.html template
        select_query = "SELECT task_name, task_description FROM tasks WHERE id = %s"
        cursor.execute(select_query, (task_id,))
        task = cursor.fetchone()

        if task is None:
            # Handle the case where the task doesn't exist
            return "Task not found"

        return render_template('edit.html', task=task, task_id=task_id)
    elif request.method == 'POST':
        # Handle the form submission to update the task
        new_task_name = request.form['new_task_name']
        new_task_description = request.form['new_task_description']
        update_query = "UPDATE tasks SET task_name = %s, task_description = %s WHERE id = %s"
        cursor.execute(update_query, (new_task_name, new_task_description, task_id))
        conn.commit()
        return redirect(url_for('show_tasks'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    delete_query = "DELETE FROM tasks WHERE id = %s"
    cursor.execute(delete_query, (task_id,))
    conn.commit()
    return redirect(url_for('show_tasks'))

if __name__ == '__main__':
    app.run(debug=True)
