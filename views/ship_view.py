import sqlite3
import json


def update_ship(id, ship_data):
    with sqlite3.connect("./shipping.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            UPDATE Ship
                SET
                    name = ?,
                    hauler_id = ?
            WHERE id = ?
            """,
            (ship_data["name"], ship_data["hauler_id"], id),
        )

        rows_affected = db_cursor.rowcount

    return True if rows_affected > 0 else False


def delete_ship(pk):
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute(
            """
        DELETE FROM Ship WHERE id = ?
        """,
            (pk,),
        )
        number_of_rows_deleted = db_cursor.rowcount

    return True if number_of_rows_deleted > 0 else False


def list_ships(url):
    # Open a connection to the database
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Check if _expand parameter exists
        if "_expand" in url["query_params"]:
            # Perform a join with the Hauler table if _expand parameter is present
            db_cursor.execute(
                """
                SELECT
                    s.id AS ship_id,
                    s.name AS ship_name,
                    s.hauler_id,
                    h.name AS hauler_name,
                    h.dock_id AS dock_id
                FROM Ship s
                JOIN Hauler h ON s.hauler_id = h.id
                """
            )
            query_results = db_cursor.fetchall()

            # Convert rows to dictionaries and include hauler details
            ships = []
            for row in query_results:
                hauler = {
                    "id": row["hauler_id"],
                    "name": row["hauler_name"],
                    "dock_id": row["dock_id"],
                }
                ship = {
                    "id": row["ship_id"],
                    "name": row["ship_name"],
                    "hauler_id": row["hauler_id"],
                    "hauler": hauler,
                }
                ships.append(ship)
        else:
            # Original logic if _expand is not present
            db_cursor.execute(
                """
                SELECT
                    s.id,
                    s.name,
                    s.hauler_id
                FROM Ship s
                """
            )
            query_results = db_cursor.fetchall()

            # Use list comprehension to convert rows to dictionaries
            ships = [dict(row) for row in query_results]

        # Serialize Python list to JSON string
        serialized_ships = json.dumps(ships)

    # Optional: Print URL dictionary to see what is being passed
    print("URL Dictionary:", url)

    return serialized_ships


def retrieve_ship(pk):
    # Open a connection to the database
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute(
            """
        SELECT
            s.id,
            s.name,
            s.hauler_id
        FROM Ship s
        WHERE s.id = ?
        """,
            (pk,),
        )
        query_results = db_cursor.fetchone()

        # Serialize Python list to JSON encoded string
        dictionary_version_of_object = dict(query_results)
        serialized_ship = json.dumps(dictionary_version_of_object)

    return serialized_ship


def create_ship(ship):
    # Create a new ship in the database
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db = conn.cursor()
        try:
            db.execute(
                """
                INSERT INTO Ship (name, hauler_id)
                VALUES (?, ?)
            """,
                (ship["name"], ship["hauler_id"]),
            )

            conn.commit()  # Commit the transaction

            ship["id"] = db.lastrowid
            return ship
        except sqlite3.Error as e:
            print(f"Database Error: {e}")  # Optional for debugging
            return None
