import csv
import sqlite3
from typing import Optional, List, Tuple
from models.account import Account
from models.flight import Flight
from models.order import Order
from models.passenger import Passenger
from datetime import datetime
from sqlite3 import Error

from models.ticket import Ticket


class TicketAlreadyPurchasedError(Exception):
    def __init__(self, message="The passenger has already bought this ticket"):
        self.message = message
        super().__init__(self.message)

class OrderNotFoundError(Exception):
    pass

class Database:
    def __init__(self):
        pass

    @staticmethod
    def create_tables():
        conn = None
        try:
            conn = sqlite3.connect('flight_booking.db')  # 这行代码会自动创建数据库文件
            print("SQLite connection established")
        except Error as e:
            print(e)
            return

        if conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL
                );
            ''')

            # 创建添加的乘客表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passengers(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    passenger_id TEXT,
                    user_id INTEGER,
                    passenger_name TEXT NOT NULL,
                    phone INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            ''')

            # 创建机票表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets(
                    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    passenger_id INTEGER,
                    flight_id INTEGER,
                    cabin_class TEXT NOT NULL,
                    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
                    FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
                    );
            ''')

            # 创建航班表，添加新的字段
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flight_id TEXT NOT NULL,
                    departure_city TEXT NOT NULL,
                    arrival_city TEXT NOT NULL,
                    departure_date TEXT NOT NULL,
                    arrival_date TEXT NOT NULL,
                    economy_seats INTEGER NOT NULL,
                    premium_seats INTEGER NOT NULL,
                    first_seats INTEGER NOT NULL,
                    economy_price REAL NOT NULL,
                    premium_price REAL NOT NULL,
                    first_price REAL NOT NULL,
                    company TEXT NOT NULL ,
                    model TEXT NOT NULL,
                    departure_airport TEXT NOT NULL,
                    arrival_airport TEXT NOT NULL,
                    is_full BOOLEAN NOT NULL DEFAULT 0
                );
            ''')

            # 创建机场数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS airports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    airport_code TEXT,
                    airport_name TEXT,
                    city_code TEXT,
                    city_name TEXT,
                    country_code TEXT,
                    country_name TEXT,
                    airport_longitude FLOAT,
                    airport_latitude FLOAT
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders(
                    order_id TEXXT PRIMARY KEY NOT NULL,
                    order_time TEXT NOT NULL,
                    price REAL NOT NULL,
                    user_id TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_tickets(
                    order_id TEXT NOT NULL,
                    ticket_id INTEGER NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(order_id),
                    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id),
                    PRIMARY KEY (order_id, ticket_id)           
                );
            ''')

            cursor.execute("SELECT COUNT(*) FROM airports")
            row_count = cursor.fetchone()[0]

            if row_count == 0:
                with open('assets/airports.csv', 'r', encoding='utf-8') as f:
                    for line in f:
                        data = line.strip().split(',')
                        cursor.execute('''
                            INSERT INTO airports (airport_code, airport_name, city_code, city_name, country_code, country_name, airport_longitude, airport_latitude)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (data[0], data[1], data[2], data[3], data[4], data[5], float(data[6]), float(data[7])))
                conn.commit()

                with open('assets/flights.csv', 'r', encoding='utf-8') as f:
                    for line in f:
                        data = line.strip().split(',')
                        cursor.execute('''
                            INSERT INTO flights (flight_id, departure_city, arrival_city, departure_date, arrival_date, economy_seats, premium_seats, first_seats, economy_price, premium_price, first_price, company, model, departure_airport, arrival_airport)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (data[0], data[1], data[2], data[3], data[4], int(data[5]), int(data[6]), int(data[7]), float(data[8]), float(data[9]), float(data[10]), data[11], data[12], data[13], data[14]))
                conn.commit()

            else:
                print("Failed to reload file")

            conn.commit()
            conn.close()

    @staticmethod
    def query_password(username: str) -> Optional[str]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        query = """
        SELECT password FROM users
        WHERE username = ?
        """

        cursor.execute(query, (username,))
        password = cursor.fetchone()

        conn.close()
        if password:
            return password[0]
        else:
            return None

    @staticmethod
    def add_user(username: str, password: str, name: str, id: str):
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        insert = """
            INSERT INTO users (username, password, name, user_id)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(insert, (username, password, name, id))

        conn.commit()
        conn.close()

    @staticmethod
    def query_userinfo(username: str) -> Optional[Account]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        query = """
        SELECT user_id, username, password, name FROM users
        WHERE username = ?
        """

        cursor.execute(query, (username,))
        user_data = cursor.fetchall()

        if user_data:
            user_id, username, password, name = user_data[0]
            query_passenger = """
                SELECT passenger_id, passenger_name, phone FROM passengers
                WHERE user_id = ?
            """

            cursor.execute(query_passenger, (user_id,))
            passenger_data = cursor.fetchall()

            passengers = []

            for passenger in passenger_data:
                passenger_id, passenger_name, phone= passenger

                passenger = Passenger(
                    id=passenger_id,
                    name=passenger_name,
                    phone=phone
                )
                passengers.append(passenger)
            account = Account(
                username=username,
                password=password,
                id=str(user_id),
                name = name,
                passengers=passengers
            )

            conn.close()
            return account
        else:
            return None

    @staticmethod
    def query_available_cities() -> List[str]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute("SELECT city_name FROM airports")
        cities = cursor.fetchall()
        return list(set(list(map(lambda x: x[0], cities))))

    @staticmethod
    def query_city_code(city_name: str) -> Optional[str]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        # 检查数据库中是否有该机场代码的数据
        cursor.execute("SELECT city_code FROM airports WHERE city_name = ?", (city_name,))
        result = cursor.fetchone()

        conn.close()
        if result:
            return result[0]
        else:
            return None
        

    @staticmethod
    def query_city_name(city_code: str) -> Optional[str]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute("SELECT city_name FROM airports WHERE city_code = ?", (city_code,))
        result = cursor.fetchone()

        conn.close()
        if result:
            return result[0]
        else:
            return None

    @staticmethod
    def query_airport_code(airport_name: str) -> Optional[str]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute("SELECT airport_code FROM airports WHERE airport_name = ?", (airport_name,))
        result = cursor.fetchone()

        conn.close()
        if result:
            return result[0]
        else:
            return None

    @staticmethod
    def query_airport_name(airport_code: str) -> Optional[str]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute("SELECT airport_name FROM airports WHERE airport_code = ?", (airport_code,))
        result = cursor.fetchone()

        conn.close()
        if result:
            return result[0]
        else:
            return None

    @staticmethod
    def query_airport_city(airport_code: str) -> Optional[str]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute("SELECT city_name FROM airports WHERE airport_code = ?", (airport_code,))
        result = cursor.fetchone()

        conn.close()
        if result:
            return result[0]
        else:
            return None

    @staticmethod
    def query_airport_location(airport_code: str) -> Tuple[float, float]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        query = """
                SELECT airport_longitude, airport_latitude FROM airports
                WHERE airport_code = ?
        """

        cursor.execute(query, (airport_code,))
        result = cursor.fetchall()

        return result[0]

    @staticmethod
    def query_airports_of_city(city_name: str) -> List[str]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute("SELECT airport_name FROM airports WHERE city_name = ?", (city_name,))
        result = cursor.fetchall()

        conn.close()
        if result:
            return [airport[0] for airport in result] # 提取每个元组的第一个元素，组成新的列表
        return []

    @staticmethod
    def query_country_code_of_city(city_code: str) -> Optional[str]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute("SELECT country_code FROM airports WHERE city_code = ?", (city_code,))
        result = cursor.fetchone()

        conn.close()
        if result:
            return result[0]
        else:
            return None

    @staticmethod
    def query_country_name(country_code: str) -> Optional[str]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute("SELECT country_name FROM airports WHERE country_code = ?", (country_code,))
        result = cursor.fetchone()

        conn.close()
        if result:
            return result[0]
        else:
            return None

    @staticmethod
    def query_country_code(country_name: str) -> Optional[str]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute("SELECT country_code FROM airports WHERE country_name = ?", country_name)
        result = cursor.fetchone()

        conn.close()
        if result:
            return result[0]
        else:
            return None

    @staticmethod
    def query_passengerinfo(passenger_id: str) -> Optional[Passenger]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        query_passenger = """
                SELECT passenger_id, passenger_name, phone FROM passengers
                WHERE passenger_id = ?
            """

        cursor.execute(query_passenger, (passenger_id,))
        passenger_data = cursor.fetchall()

        passengers = []

        for passenger in passenger_data:
            passenger_id, passenger_name, phone = passenger

            passenger = Passenger(
                id=passenger_id,
                name=passenger_name,
                phone=phone
            )
            passengers.append(passenger)

        if passengers:
            return passengers
        else:
            return None

    @staticmethod
    def query_flights_by_flt(flt: str) -> List[Flight]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        query_flights = """
                SELECT flight_id, departure_city, arrival_city, departure_date, arrival_date, economy_seats, premium_seats, first_seats
                ,economy_price, premium_price, first_price, company, model, departure_airport, arrival_airport, is_full
                FROM flights WHERE flight_id = ?
            """

        cursor.execute(query_flights, (flt,))
        flights_data = cursor.fetchall()

        flights = []
        for flight_data in flights_data:
            flight_id, dep_city, arr_city, dep_date, arr_date, eco_seats, pre_seats, fir_seats, eco_price, fir_price, pre_price,\
                com, mod, dep_airport, arr_airport, is_full = flight_data

            flight = Flight(
                flt=flight_id,
                company=com,
                model=mod,
                departure_city=dep_city,
                arrival_city=arr_city,
                departure_airport=dep_airport,
                arrival_airport=arr_airport,
                departure_time=dep_date,
                arrival_time=arr_date,
                remain={
                    "Economy": eco_seats,
                    "Premium": pre_seats,
                    "First": fir_seats
                },
                price={
                    "Economy": eco_price,
                    "Premium": pre_price,
                    "First": fir_price
                }
            )
            flights.append(flight)
        return flights

    @staticmethod
    def query_flights() -> List[Flight]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        query_flights = """
                SELECT flight_id, departure_city, arrival_city, departure_date, arrival_date, economy_seats, premium_seats, first_seats
                ,economy_price, premium_price, first_price, company, model, departure_airport, arrival_airport, is_full
                FROM flights
            """

        cursor.execute(query_flights)
        flights_data = cursor.fetchall()

        flights = []
        for flight_data in flights_data:
            flight_id, dep_city, arr_city, dep_date, arr_date, eco_seats, pre_seats, fir_seats, eco_price, fir_price, pre_price,\
                com, mod, dep_airport, arr_airport, is_full = flight_data

            flight = Flight(
                flt=flight_id,
                company=com,
                model=mod,
                departure_city=dep_city,
                arrival_city=arr_city,
                departure_airport=dep_airport,
                arrival_airport=arr_airport,
                departure_time=dep_date,
                arrival_time=arr_date,
                remain={
                    "Economy": eco_seats,
                    "Premium": pre_seats,
                    "First": fir_seats
                },
                price={
                    "Economy": eco_price,
                    "Premium": pre_price,
                    "First": fir_price
                }
            )
            flights.append(flight)

        conn.close()
        return flights

    @staticmethod
    def query_flights_by_datetime(time: datetime) -> List[Flight]:
        date = time.strftime('%Y-%m-%d')
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        query_flights = """
                SELECT flight_id, departure_city, arrival_city, departure_date, arrival_date, economy_seats, premium_seats, first_seats
                ,economy_price, premium_price, first_price, company, model, departure_airport, arrival_airport, is_full
                FROM flights WHERE departure_date = ?
            """

        cursor.execute(query_flights, (date,))
        flights_data = cursor.fetchall()

        flights = []
        for flight_data in flights_data:
            flight_id, dep_city, arr_city, dep_date, arr_date, eco_seats, pre_seats, fir_seats, eco_price, fir_price, pre_price,\
                com, mod, dep_airport, arr_airport, is_full = flight_data

            flight = Flight(
                flt=flight_id,
                company=com,
                model=mod,
                departure_city=dep_city,
                arrival_city=arr_city,
                departure_airport=dep_airport,
                arrival_airport=arr_airport,
                departure_time=dep_date,
                arrival_time=arr_date,
                remain={
                    "Economy": eco_seats,
                    "Premium": pre_seats,
                    "First": fir_seats
                },
                price={
                    "Economy": eco_price,
                    "Premium": pre_price,
                    "First": fir_price
                }
            )
            flights.append(flight)

        conn.close()
        return flights

    @staticmethod
    def query_flights_by_departure(city_code: str) -> List[Flight]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute('''SELECT city_name FROM airports WHERE city_code = ?''', (city_code,))
        result = cursor.fetchone()

        if not result:
            return []

        city_name = result[0]

        query_flights = """
                SELECT flight_id, departure_city, arrival_city, departure_date, arrival_date, economy_seats, premium_seats, first_seats
                ,economy_price, premium_price, first_price, company, model, departure_airport, arrival_airport, is_full
                FROM flights WHERE departure_city = ?
            """

        cursor.execute(query_flights, (city_name,))
        flights_data = cursor.fetchall()

        flights = []
        for flight_data in flights_data:
            flight_id, dep_city, arr_city, dep_date, arr_date, eco_seats, pre_seats, fir_seats, eco_price, fir_price, pre_price,\
                com, mod, dep_airport, arr_airport, is_full = flight_data

            flight = Flight(
                flt=flight_id,
                company=com,
                model=mod,
                departure_city=dep_city,
                arrival_city=arr_city,
                departure_airport=dep_airport,
                arrival_airport=arr_airport,
                departure_time=dep_date,
                arrival_time=arr_date,
                remain={
                    "Economy": eco_seats,
                    "Premium": pre_seats,
                    "First": fir_seats
                },
                price={
                    "Economy": eco_price,
                    "Premium": pre_price,
                    "First": fir_price
                }
            )
            flights.append(flight)

        conn.close()

        return flights

    @staticmethod
    def query_flights_by_arrival(city_code: str) -> List[Flight]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute('''SELECT city_name FROM airports WHERE city_code = ?''', (city_code,))
        result = cursor.fetchone()

        if not result:
            return []

        city_name = result[0]

        query_flights = """
                SELECT flight_id, departure_city, arrival_city, departure_date, arrival_date, economy_seats, premium_seats, first_seats
                ,economy_price, premium_price, first_price, company, model, departure_airport, arrival_airport, is_full
                FROM flights WHERE arrival_city = ?
            """

        cursor.execute(query_flights, (city_name,))
        flights_data = cursor.fetchall()

        flights = []
        for flight_data in flights_data:
            flight_id, dep_city, arr_city, dep_date, arr_date, eco_seats, pre_seats, fir_seats, eco_price, fir_price, pre_price,\
                com, mod, dep_airport, arr_airport, is_full = flight_data

            flight = Flight(
                flt=flight_id,
                company=com,
                model=mod,
                departure_city=dep_city,
                arrival_city=arr_city,
                departure_airport=dep_airport,
                arrival_airport=arr_airport,
                departure_time=dep_date,
                arrival_time=arr_date,
                remain={
                    "Economy": eco_seats,
                    "Premium": pre_seats,
                    "First": fir_seats
                },
                price={
                    "Economy": eco_price,
                    "Premium": pre_price,
                    "First": fir_price
                }
            )
            flights.append(flight)

        conn.close()

        return flights

    @staticmethod
    def add_flight(flight: Flight):
        conn = sqlite3.connect('flights.db')
        cursor = conn.cursor()

        flight_id = flight.flt
        company = flight.company
        model = flight.model
        departure_date = flight.departure_datetime.strftime('%Y-%m-%d %H:%M:%S')
        arrival_date = flight.arrival_datetime.strftime('%Y-%m-%d %H:%M:%S')
        departure_city = flight.departure_city
        arrival_city = flight.arrival_city
        departure_airport = flight.departure_airport
        arrival_airport = flight.arrival_airport
        economy_price = flight.price.get('Economy')
        first_price = flight.price.get('First')
        economy_seats = flight.remain.get('Economy')
        first_seats = flight.remain.get('First')
        premium_price = flight.price.get('Premium')
        premium_seats = flight.remain.get('Premium')
        is_full = (economy_seats == 0 and first_seats == 0)  # 判断是否满座

        # 插入数据到 flights 表
        cursor.execute('''
            INSERT INTO flights (
                flight_id, company, model, departure_date, arrival_date, 
                departure_city, arrival_city, departure_airport, arrival_airport, 
                economy_price, first_price, economy_seats, first_seats, premium_price, premium_seats, is_full
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            flight_id, company, model, departure_date, arrival_date,
            departure_city, arrival_city, departure_airport, arrival_airport,
            economy_price, first_price, economy_seats, first_seats,premium_price, premium_seats, is_full
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def add_passenger(user: Account, passenger: Passenger):
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO passengers (
                passenger_id, user_id, passenger_name, phone
            ) VALUES (?, ?, ?, ?)
        ''', (
            passenger.id,
            user.id,
            passenger.name,
            passenger.phone if passenger.phone else None
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def query_tickets(passenger: Passenger) -> List[Ticket]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute("SELECT passenger_id, flight_id, cabin_class FROM ticket WHERE passenger_id = ?", (passenger.id,))
        ticket_data = cursor.fetchall()

        tickets = []
        for tickets_data in ticket_data:
            passengers_id, flight_id, cabin_class = tickets_data

            passengers = []
            passenger = Passenger(
                id = passengers_id,
                name = passenger.name,
                phone = passenger.phone
            )
            passengers.append(passenger)

            query_flights = """
                SELECT flight_id, departure_city, arrival_city, departure_date, arrival_date, economy_seats, premium_seats, first_seats
                ,economy_price, premium_price, first_price, company, model, departure_airport, arrival_airport, is_full
                FROM flights WHERE flight_id = ?
            """

            cursor.execute(query_flights, (flight_id,))
            flights_data = cursor.fetchall()

            flights = []
            for flight_data in flights_data:
                flight_id, dep_city, arr_city, dep_date, arr_date, eco_seats, pre_seats, fir_seats, eco_price, fir_price, pre_price,\
                    com, mod, dep_airport, arr_airport, is_full = flight_data

                flight = Flight(
                    flt=flight_id,
                    company=com,
                    model=mod,
                    departure_city=dep_city,
                    arrival_city=arr_city,
                    departure_airport=dep_airport,
                    arrival_airport=arr_airport,
                    departure_time=dep_date,
                    arrival_time=arr_date,
                    remain={
                        "Economy": eco_seats,
                        "Premium": pre_seats,
                        "First": fir_seats
                    },
                    price={
                        "Economy": eco_price,
                        "Premium": pre_price,
                        "First": fir_price
                    }
                )
                flights.append(flight)

            ticket = Ticket(
                type = cabin_class,
                passenger = passengers,
                flight = flights
            )
            tickets.append(ticket)

        conn.close()

        return tickets

    @staticmethod
    def place_order(user: Account, order: Order):
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        try:
            # 插入订单数据到 orders 表
            order_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                    INSERT INTO orders (order_id, order_time, price, user_id)
                    VALUES (?, ?, ?, ?);
                ''', (order.id, order_time, order.price, user.id))

            # 获取订单中的每个机票并插入数据到 tickets 表
            tickets_id = []
            for ticket in order.tickets:
                # 检查该乘客是否已经购买过相同的票
                cursor.execute('''
                    SELECT 1 FROM tickets
                    WHERE passenger_id = ? AND flight_id = ?
                ''', (ticket.passenger.id, ticket.flight.flt))

                if cursor.fetchone():
                    raise TicketAlreadyPurchasedError(
                        f"passenger {ticket.passenger.name} has already bought ticket {ticket.flight.flt} "
                    )

                cursor.execute('''
                        INSERT INTO tickets (passenger_id, flight_id, cabin_class)
                        VALUES (?, ?, ?);
                    ''', (ticket.passenger.id, ticket.flight.flt, ticket.type))
                tickets_id.append(cursor.lastrowid)

            # 将订单和机票关联
            for ticket_id in tickets_id:
                cursor.execute('''
                    INSERT INTO order_tickets (order_id, ticket_id)
                    VALUES (?, ?);
                ''', (order.id, ticket_id))

            conn.commit()

        except TicketAlreadyPurchasedError as e:
            # 捕获自定义异常并回滚
            conn.rollback()
            print(f"Error: {e}")

        except Exception as e:
            # 其他异常时回滚
            conn.rollback()
            print(f"An error occurred: {e}")

        finally:
            # 关闭数据库连接
            conn.close()

    @staticmethod
    def refund_order(user: Account, order: Order):
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        try:
            # 检查订单是否存在并且属于当前用户
            cursor.execute('''
                   SELECT order_id FROM orders 
                   WHERE order_id = ? AND user_id = ?;
               ''', (order.id, user.id))
            existing_order = cursor.fetchone()

            if not existing_order:
                raise OrderNotFoundError(f"Order with ID {order.id} not found for user {user.username}.")

            for ticket in order.tickets:
                # 删除 tickets 表中的记录
                cursor.execute('''
                       DELETE FROM tickets 
                       WHERE passenger_id = ? AND flight_id = ?;
                   ''', (ticket.passenger.id, ticket.flight.flt))

            # 删除订单记录
            cursor.execute('''
                   DELETE FROM orders 
                   WHERE order_id = ?;
               ''', (order.id,))

            conn.commit()

        except OrderNotFoundError as e:
            # 捕获订单未找到的异常
            conn.rollback()
            print(f"Error: {e}")

        except Exception as e:
            # 其他异常时回滚
            conn.rollback()
            print(f"An error occurred: {e}")

        finally:
            # 关闭数据库连接
            conn.close()

    @staticmethod
    def upgrade_order(tickets: list[Ticket]):  # 处理票的列表
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        try:
            for ticket in tickets:
                cursor.execute('''
                    SELECT ticket_id, flight_id FROM tickets 
                    WHERE passenger_id = ? AND flight_id = ?;
                ''', (ticket.passenger.id, ticket.flight.flt))
                existing_ticket = cursor.fetchone()

                if not existing_ticket:
                    raise OrderNotFoundError(f"Ticket with passenger ID {ticket.passenger.id} not found.")
                
                tickets_id, flight_id = existing_ticket
                # 更新票的舱位为 Premium
                cursor.execute('''
                    UPDATE tickets 
                    SET cabin_class = 'Premium'
                    WHERE ticket_id = ?;
                ''', (tickets_id,))

                # 更新订单价格
                cursor.execute('''
                    SELECT premium_price FROM flights WHERE flight_id = ?;
                ''', (flight_id,))
                premium_price = cursor.fetchone()
                if premium_price:
                    cursor.execute('''
                        UPDATE orders
                        SET price = ?
                        WHERE order_id = (SELECT order_id FROM order_tickets WHERE ticket_id = ?);
                    ''', (premium_price[0], tickets_id))

            conn.commit()

        except OrderNotFoundError as e:
            conn.rollback()
            print(f"Error: {e}")

        except Exception as e:
            conn.rollback()
            print(f"An error occurred: {e}")

        finally:
            conn.close()


    @staticmethod
    def query_orders(user: Account) -> List[Order]:
        conn = sqlite3.connect('flight_booking.db')
        cursor = conn.cursor()

        cursor.execute('''
                SELECT order_id, order_time, price
                FROM orders WHERE user_id = ?; 
            ''', (user.id,))
        
        orders_data = cursor.fetchall()

        orders = []
        for order_data in orders_data:
            order_id, order_time, price = order_data

            cursor.execute('''
                SELECT ticket_id FROM order_tickets WHERE order_id = ?;
            ''', (order_id,))

            ticket_ids = cursor.fetchall()
            tickets = []
            for ticket_id in ticket_ids:
                cursor.execute('''
                    SELECT passenger_id, flight_id, cabin_class FROM tickets WHERE ticket_id = ?;
                ''', (ticket_id[0],))

                passenger_flight = cursor.fetchall()
                for passenger_id, flight_id, cabin_class in passenger_flight:
                    cursor.execute('''
                        SELECT passenger_name, phone FROM passengers WHERE passenger_id = ?;
                    ''', (passenger_id,))
                    passenger_data = cursor.fetchone()
                    passenger_name, phone = passenger_data

                    cursor.execute('''
                        SELECT flight_id, departure_city, arrival_city, departure_date, arrival_date, economy_seats, premium_seats, first_seats
                        ,economy_price, premium_price, first_price, company, model, departure_airport, arrival_airport, is_full
                        FROM flights WHERE flight_id = ?;
                    ''', (flight_id,))
                    flight_data = cursor.fetchone()
                    flight_id, dep_city, arr_city, dep_date, arr_date, eco_seats, pre_seats, fir_seats, eco_price, fir_price, pre_price,\
                        com, mod, dep_airport, arr_airport, is_full = flight_data

                    flight = Flight(
                        flt=flight_id,
                        company=com,
                        model=mod,
                        departure_city=dep_city,
                        arrival_city=arr_city,
                        departure_airport=dep_airport,
                        arrival_airport=arr_airport,
                        departure_time=dep_date,
                        arrival_time=arr_date,
                        remain={
                            "Economy": eco_seats,
                            "Premium": pre_seats,
                            "First": fir_seats
                        },
                        price={
                            "Economy": eco_price,
                            "Premium": pre_price,
                            "First": fir_price
                        }
                    )

                    passenger = Passenger(
                        id=str(passenger_id),
                        name=passenger_name,
                        phone=phone
                    )

                    ticket = Ticket(
                        type=cabin_class,
                        passenger=passenger,
                        flight=flight
                    )
                    tickets.append(ticket)
            
            order = Order(
                id=str(order_id),
                timestamp=order_time,
                price=price,
                tickets=tickets
            )
            orders.append(order)

        conn.close()
        return orders

        
