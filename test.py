import streamlit as st
import mysql.connector
import pandas as pd




def connect_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='915781',
        database='blood_bank'
    )
    return conn


def create_user_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            age INT,
            blood_group VARCHAR(10),
            email VARCHAR(255),
            address TEXT
        );
    """)
    conn.commit()
    conn.close()


def create_blood_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            blood_group VARCHAR(10),
            amount_ml INT,
            FOREIGN KEY (user_id) REFERENCES user_details(id)
        );
    """)
    conn.commit()
    conn.close()


def insert_user_details(name, age, blood_group, email, address):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_details (name, age, blood_group, email, address)
        VALUES (%s, %s, %s, %s, %s);
    """, (name, age, blood_group, email, address))
    conn.commit()
    conn.close()

def insert_blood_details(user_id, blood_group, amount_ml):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO blood_details (user_id, blood_group, amount_ml)
        VALUES (%s, %s, %s);
    """, (user_id, blood_group, amount_ml))
    conn.commit()
    conn.close()


def fetch_user_details():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_details")
    users = cursor.fetchall()
    conn.close()
    return users


def fetch_blood_details():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT blood_group, SUM(amount_ml) FROM blood_details GROUP BY blood_group")
    blood_data = cursor.fetchall()
    conn.close()
    return blood_data


def fetch_donated_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_details.name, user_details.age, user_details.blood_group, blood_details.amount_ml
        FROM user_details
        INNER JOIN blood_details ON user_details.id = blood_details.user_id;
    """)
    donated_users = cursor.fetchall()
    conn.close()
    return donated_users


users_needing_blood_details = []


def fetch_user_details_excluding_donors():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM user_details
        WHERE id NOT IN (SELECT user_id FROM blood_details);
    """)
    users = cursor.fetchall()
    conn.close()
    return users

def fetch_user_by_id(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_details WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def main():
    st.title("Blood Bank Application")
    create_user_table()
    create_blood_table()
    
    global users_needing_blood_details
    if not users_needing_blood_details:
        users_needing_blood_details = [user[0] for user in fetch_user_details_excluding_donors()]


    selection = st.sidebar.radio("Navigation", ["User", "Admin", "Blood Panel", "Donated Users"])
    
    if selection == "User":
        st.header("User Registration")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1, max_value=150)
        blood_group = st.selectbox("Blood Group", ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'])
        email = st.text_input("Email")
        address = st.text_area("Address")
        if st.button("Submit"):
            insert_user_details(name, age, blood_group, email, address)
            st.success("User details submitted successfully!")

    elif selection == "Admin":
        st.header("Admin Panel")
        password = st.text_input("Enter Admin Password", type="password")
        
        if password == "admin1234":
           
            for user_id in users_needing_blood_details[:]:
                user = fetch_user_by_id(user_id)
                st.subheader("User Details")
                st.write(f"User ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, Blood Group: {user[3]}, Email: {user[4]}, Address: {user[5]}")
                
                blood_group_admin = st.selectbox(f"Enter Blood Group for User {user[0]}", ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'])
                amount_ml = st.number_input(f"Enter Amount of Blood Donated (ml) for User {user[0]}", min_value=1)
                
                if st.button(f"Submit Blood Details for User {user[0]}"):
                    insert_blood_details(user[0], blood_group_admin, amount_ml)
                    st.success("Blood details submitted successfully!")
                    
                  
                    users_needing_blood_details.remove(user_id)



    elif selection == "Blood Panel":
        st.header("Blood Panel")
        blood_data = fetch_blood_details()
        for data in blood_data:
            st.write(f"{data[0]} category has {data[1]} ml of blood available")

    elif selection == "Donated Users":
        st.header("Donated Users")
        donated_users = fetch_donated_users()
        if donated_users:
            st.table(pd.DataFrame(donated_users, columns=["Name", "Age", "Blood Group", "Amount of Blood (ml)"]))
        else:
            st.write("No users have donated blood yet.")

if __name__ == "__main__":
    main()
