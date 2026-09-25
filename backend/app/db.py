import psycopg2


connection = psycopg2.connect(
    host="localhost",
    database="career_skill_gap",
    user="postgres",
    password="VEDANT"
)


print("PostgreSQL connected successfully!")


# Check which database FastAPI is connected to
cursor = connection.cursor()

cursor.execute("""
    SELECT current_database(), current_user, inet_server_addr(), inet_server_port();
""")

print("DATABASE TEST:", cursor.fetchone())

cursor.close()