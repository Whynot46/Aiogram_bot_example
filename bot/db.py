import aiosqlite
from bot.config import Config


db_connection = None


# Инициализация соединения с базой данных
async def init_db():
    global db_connection
    db_connection = await aiosqlite.connect(Config.DB_URL)


# Закрытие соединения с базой данных
async def close_db():
    global db_connection
    if db_connection:
        await db_connection.close()
        

# Получить ФИО пользователя по user_id
async def get_fullname(user_id : int) -> str:
    global db_connection
    cursor = await db_connection.execute('''SELECT firstname, middlename, lastname FROM users WHERE user_id = ?''', (user_id,))
    result = await cursor.fetchone()
    if result:
        return f"{result[2]} {result[0]} {result[1]}"
    else:
        return None


# Проверка, зарегистрирован ли пользователь по user_id
async def is_old(user_id):
    global db_connection
    cursor = await db_connection.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = await cursor.fetchone()
    return bool(result)


#Проверка, активен ли пользователь
async def is_user_active(user_id : int):
    global db_connection
    cursor = await db_connection.execute("SELECT 1 FROM users WHERE user_id = ? AND is_active = 1", (user_id,))
    result = await cursor.fetchone()
    return bool(result)


#Получить id всех пользователей   
async def get_all_user_id() -> list:
    global db_connection
    cursor = await db_connection.execute('SELECT user_id FROM users')
    rows = await cursor.fetchall()
    return [row[0] for row in rows]


#Обновить статусы всех пользователей    
async def update_all_user_status(user_data : dict):
    global db_connection
    if not user_data:
        return

    for employee in user_data:
        full_name = employee["ФИО сотрудника"]
        status = employee["Статус"]

        lastname, firstname, middlename = full_name.split(" ")
        is_active = status == "Активный"

        # Проверяем, существует ли пользователь с таким ФИО
        cursor = await db_connection.execute(
            "SELECT user_id FROM users WHERE firstname = ? AND middlename = ? AND lastname = ?",
            (firstname, middlename, lastname)
        )
        existing_user = await cursor.fetchone()

        if existing_user:
            await db_connection.execute(
                "UPDATE users SET is_active = ? WHERE user_id = ?",
                (is_active, existing_user[0]))
        else:
            await db_connection.execute(
                "INSERT INTO users (firstname, middlename, lastname, is_active) VALUES (?, ?, ?, ?)",
                (firstname, middlename, lastname, is_active))

    await db_connection.commit()