
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI(
    title="PWAC",
    description="Personal Website Access Controller",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to SQLite database
def get_connection():
    return sqlite3.connect("pwac.db")


# Create database table
def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS website_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT UNIQUE NOT NULL,
            is_blocked BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# Create database when application starts
create_database()


# Data format for adding a website
class WebsiteRule(BaseModel):
    domain: str


@app.get("/")
def home():
    return {
        "project": "PWAC",
        "message": "Welcome to Personal Website Access Controller",
        "status": "Running successfully"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# Add a website rule
@app.post("/rules")
def add_rule(rule: WebsiteRule):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO website_rules (domain) VALUES (?)",
            (rule.domain.lower(),)
        )
        connection.commit()

        return {
            "message": "Website rule added successfully",
            "domain": rule.domain
        }

    except sqlite3.IntegrityError:
        return {"message": "This website already exists"}

    finally:
        connection.close()


# View all website rules
@app.get("/rules")
def get_rules():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM website_rules")
    rules = cursor.fetchall()

    connection.close()

    return {"website_rules": rules}

# Delete a website rule
@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM website_rules WHERE id = ?",
        (rule_id,)
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        return {"message": "Website rule not found"}

    connection.close()

    return {"message": "Website rule deleted successfully"}

# Activate or deactivate a website rule
@app.patch("/rules/{rule_id}")
def update_rule(rule_id: int, is_blocked: bool):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE website_rules SET is_blocked = ? WHERE id = ?",
        (is_blocked, rule_id)
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        return {"message": "Website rule not found"}

    connection.close()

    return {
        "message": "Website rule updated successfully",
        "rule_id": rule_id,
        "is_blocked": is_blocked
    }
