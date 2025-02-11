import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Create the database and tables if they don't exist
def create_database():
    conn = sqlite3.connect('employee_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Employees (
            ID INTEGER PRIMARY KEY,
            Name TEXT,
            Department TEXT,
            Salary INTEGER,
            Hire_Date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Departments (
            ID INTEGER PRIMARY KEY,
            Name TEXT,
            Manager TEXT
        )
    ''')

    # Insert initial data (if the tables are empty)
    cursor.execute("SELECT COUNT(*) FROM Employees")
    employee_count = cursor.fetchone()[0]
    if employee_count == 0:
      cursor.executemany("INSERT INTO Employees (ID, Name, Department, Salary, Hire_Date) VALUES (?, ?, ?, ?, ?)", [
          (1, 'Alice', 'Sales', 50000, '2021-01-15'),
          (2, 'Bob', 'Engineering', 70000, '2020-06-10'),
          (3, 'Charlie', 'Marketing', 60000, '2022-03-20')
      ])

    cursor.execute("SELECT COUNT(*) FROM Departments")
    department_count = cursor.fetchone()[0]
    if department_count == 0:
      cursor.executemany("INSERT INTO Departments (ID, Name, Manager) VALUES (?, ?, ?)", [
          (1, 'Sales', 'Alice'),
          (2, 'Engineering', 'Bob'),
          (3, 'Marketing', 'Charlie')
      ])
    
    conn.commit()
    conn.close()

create_database()  # Call this to ensure the database exists

@app.route('/ask', methods=['POST'])
def ask():
    try:
        query = request.json.get('query')
        if not query:
            return jsonify({'response': 'Please provide a query.'}), 400

        conn = sqlite3.connect('employee_data.db')
        cursor = conn.cursor()

        # Basic query parsing and execution (can be expanded)
        if "show me all employees in the" in query.lower():
            department = query.lower().split("in the ")[1].replace(" department", "").strip()
            cursor.execute("SELECT Name, Salary, Hire_Date FROM Employees WHERE Department=?", (department,))
            results = cursor.fetchall()
            if results:
                response = "Employees in the {} department:\n".format(department)
                for row in results:
                    response += f"- Name: {row[0]}, Salary: {row[1]}, Hire Date: {row[2]}\n"
            else:
                response = f"No employees found in the {department} department."

        elif "who is the manager of the" in query.lower():
            department = query.lower().split("of the ")[1].replace(" department", "").strip()
            cursor.execute("SELECT Manager FROM Departments WHERE Name=?", (department,))
            result = cursor.fetchone()
            if result:
                response = f"The manager of the {department} department is {result[0]}."
            else:
                response = f"Department '{department}' not found."

        elif "list all employees hired after" in query.lower():
            date = query.lower().split("after ")[1].strip()
            cursor.execute("SELECT Name, Hire_Date FROM Employees WHERE Hire_Date > ?", (date,))
            results = cursor.fetchall()
            if results:
              response = "Employees hired after {}:\n".format(date)
              for row in results:
                  response += f"- Name: {row[0]}, Hire Date: {row[1]}\n"
            else:
              response = f"No employees found hired after {date}."

        elif "what is the total salary expense for the" in query.lower():
            department = query.lower().split("for the ")[1].replace(" department", "").strip()
            cursor.execute("SELECT SUM(Salary) FROM Employees WHERE Department=?", (department,))
            result = cursor.fetchone()[0]
            if result:
                response = f"Total salary expense for the {department} department: {result}."
            else:
                response = f"No employees found in the {department} department."

        else:
            response = "I don't understand your query.  I can currently handle queries like:\n" \
                       "- Show me all employees in the [department] department.\n" \
                       "- Who is the manager of the [department] department?\n" \
                       "- List all employees hired after [date].\n" \
                       "- What is the total salary expense for the [department] department?"


        conn.close()
        return jsonify({'response': response}), 200

    except Exception as e:
        return jsonify({'response': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # host='0.0.0.0' for deployment
