"""
Passenger Ticket Booking System with Data Structures
1. Binary Search Tree (BST) for Passenger Database
2. Graph for City Transport Network
3. Min Heap for Ticket Priority
4. Linked List for Booking History
"""
import json
import uuid
from datetime import datetime, timedelta, time
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import heapq
from collections import deque

# ===================== DATA STRUCTURES =====================

# ---------- Binary Search Tree (BST) for Passengers ----------
class BSTNode:
    """Binary Search Tree Node for Passenger Storage"""
    def __init__(self, passenger_id: str, passenger_data: dict):
        self.passenger_id = passenger_id
        self.data = passenger_data
        self.left = None
        self.right = None

class PassengerBST:
    """Binary Search Tree for Efficient Passenger Search"""
    def __init__(self):
        self.root = None
    
    def insert(self, passenger_id: str, passenger_data: dict) -> None:
        """Insert passenger into BST"""
        if not self.root:
            self.root = BSTNode(passenger_id, passenger_data)
        else:
            self._insert_recursive(self.root, passenger_id, passenger_data)
    
    def _insert_recursive(self, node: BSTNode, passenger_id: str, passenger_data: dict) -> None:
        if passenger_id < node.passenger_id:
            if node.left:
                self._insert_recursive(node.left, passenger_id, passenger_data)
            else:
                node.left = BSTNode(passenger_id, passenger_data)
        else:
            if node.right:
                self._insert_recursive(node.right, passenger_id, passenger_data)
            else:
                node.right = BSTNode(passenger_id, passenger_data)
    
    def search(self, passenger_id: str) -> Optional[dict]:
        """Search passenger by ID using BST O(log n)"""
        return self._search_recursive(self.root, passenger_id)
    
    def _search_recursive(self, node: BSTNode, passenger_id: str) -> Optional[dict]:
        if not node:
            return None
        if passenger_id == node.passenger_id:
            return node.data
        elif passenger_id < node.passenger_id:
            return self._search_recursive(node.left, passenger_id)
        else:
            return self._search_recursive(node.right, passenger_id)
    
    def get_all_passengers(self) -> List[dict]:
        """Get all passengers using inorder traversal"""
        passengers = []
        self._inorder_traversal(self.root, passengers)
        return passengers
    
    def _inorder_traversal(self, node: BSTNode, result: List) -> None:
        if node:
            self._inorder_traversal(node.left, result)
            result.append({
                'passenger_id': node.passenger_id,
                **node.data
            })
            self._inorder_traversal(node.right, result)

# ---------- Graph for City Transport Network ----------
class GraphNode:
    """Graph Node representing a Bus Stop"""
    def __init__(self, stop_name: str, location: str, latitude: float = None, longitude: float = None):
        self.stop_name = stop_name
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.neighbors = {}  # {stop_name: {'distance': x, 'time': y}}

class TransportGraph:
    """Graph representing City Transport Network"""
    def __init__(self):
        self.nodes = {}
        self.routes = {}
        self.fare_per_km = 10.0
        self.transfer_penalty = 5

    def add_stop(self, stop_name: str, location: str, **kwargs) -> None:
        """Add a bus stop to the graph"""
        if stop_name not in self.nodes:
            self.nodes[stop_name] = GraphNode(stop_name, location, **kwargs)

    def add_connection(
        self,
        stop1: str,
        stop2: str,
        distance: float,
        time_minutes: int,
        route_id: Optional[str] = None,
        fare: Optional[float] = None,
    ) -> None:
        """Add connection between two stops"""
        if stop1 in self.nodes and stop2 in self.nodes:
            edge_fare = fare if fare is not None else distance * self.fare_per_km
            self.nodes[stop1].neighbors[stop2] = {
                'distance': distance,
                'time': time_minutes,
                'route_id': route_id,
                'fare': edge_fare
            }
            self.nodes[stop2].neighbors[stop1] = {
                'distance': distance,
                'time': time_minutes,
                'route_id': route_id,
                'fare': edge_fare
            }

    def dijkstra_shortest_path(self, start: str, end: str, criteria: str = 'time') -> Dict:
        """Find shortest path using Dijkstra's Algorithm"""
        if start not in self.nodes or end not in self.nodes:
            return {'path': [], 'total': float('inf'), 'message': 'Invalid stops'}

        def edge_cost(info: Dict, previous_route: Optional[str]) -> float:
            if criteria == 'distance':
                return info['distance']
            if criteria == 'time':
                return info['time']
            if criteria == 'fare':
                return info.get('fare', info['distance'] * self.fare_per_km)
            if criteria == 'transfers':
                transfer = 0
                if previous_route and info.get('route_id') and info.get('route_id') != previous_route:
                    transfer = self.transfer_penalty
                return transfer + (info['distance'] * 0.001)
            return info['time']

        pq = [(0, start, None)]
        distances = {(start, None): 0.0}
        previous = {(start, None): None}
        visited = set()

        while pq:
            current_dist, current_stop, current_route = heapq.heappop(pq)

            state = (current_stop, current_route)
            if state in visited:
                continue

            visited.add(state)

            # If we reached destination
            if current_stop == end:
                break

            # Explore neighbors
            for neighbor, info in self.nodes[current_stop].neighbors.items():
                next_route = info.get('route_id')
                next_state = (neighbor, next_route)
                if next_state in visited:
                    continue
                new_dist = current_dist + edge_cost(info, current_route)
                if new_dist < distances.get(next_state, float('inf')):
                    distances[next_state] = new_dist
                    previous[next_state] = (current_stop, current_route)
                    heapq.heappush(pq, (new_dist, neighbor, next_route))

        end_states = [(state, dist) for state, dist in distances.items() if state[0] == end]
        if not end_states:
            return {'path': [], 'total': float('inf'), 'message': 'No path found'}

        best_state, best_cost = min(end_states, key=lambda item: item[1])

        path = []
        current = best_state
        while current:
            path.append(current[0])
            current = previous.get(current)
        path.reverse()

        total_distance = 0.0
        total_time = 0.0
        total_fare = 0.0
        transfers = 0
        last_route = None
        for idx in range(len(path) - 1):
            info = self.nodes[path[idx]].neighbors[path[idx + 1]]
            total_distance += info['distance']
            total_time += info['time']
            total_fare += info.get('fare', info['distance'] * self.fare_per_km)
            route_id = info.get('route_id')
            if last_route and route_id and route_id != last_route:
                transfers += 1
            if route_id:
                last_route = route_id

        return {
            'path': path,
            'total_time': total_time,
            'total_distance': total_distance,
            'total_fare': round(total_fare, 2),
            'transfers': transfers,
            'cost': best_cost,
            'stops': len(path) - 1
        }
    
    def bfs_nearest_stop(self, start: str, target_location: str) -> Dict:
        """Find nearest bus stop using BFS"""
        if start not in self.nodes:
            return {'nearest_stop': None, 'distance': float('inf')}
        
        visited = set()
        queue = deque([(start, 0, [start])])
        
        while queue:
            current_stop, distance, path = queue.popleft()
            
            if target_location.lower() in self.nodes[current_stop].location.lower():
                return {
                    'nearest_stop': current_stop,
                    'location': self.nodes[current_stop].location,
                    'distance': distance,
                    'path': path
                }
            
            visited.add(current_stop)
            
            for neighbor, info in self.nodes[current_stop].neighbors.items():
                if neighbor not in visited:
                    new_distance = distance + info['distance']
                    queue.append((neighbor, new_distance, path + [neighbor]))
        
        return {'nearest_stop': None, 'distance': float('inf')}
    
    def dfs_find_routes(self, start: str, max_depth: int = 3) -> List[List[str]]:
        """Find all routes using DFS up to max_depth"""
        def dfs(current: str, path: List, depth: int, result: List):
            if depth > max_depth:
                return
            
            if len(path) > 1:  # Avoid single stop routes
                result.append(path.copy())
            
            visited.add(current)
            
            for neighbor in self.nodes[current].neighbors:
                if neighbor not in visited:
                    dfs(neighbor, path + [neighbor], depth + 1, result)
            
            visited.remove(current)
        
        visited = set()
        all_routes = []
        dfs(start, [start], 0, all_routes)
        return all_routes
    
    def has_cycle(self) -> bool:
        """Detect cycles in the graph"""
        visited = set()
        
        def dfs_detect_cycle(stop: str, parent: str) -> bool:
            visited.add(stop)
            
            for neighbor in self.nodes[stop].neighbors:
                if neighbor not in visited:
                    if dfs_detect_cycle(neighbor, stop):
                        return True
                elif neighbor != parent:
                    return True
            
            return False
        
        for stop in self.nodes:
            if stop not in visited:
                if dfs_detect_cycle(stop, None):
                    return True
        
        return False

# ---------- Min Heap for Ticket Priority ----------
class TicketPriorityQueue:
    """Min Heap for Managing Ticket Priority"""
    def __init__(self):
        self.heap = []
        self.ticket_map = {}  # ticket_id -> (priority, ticket_data)
    
    def push(self, ticket_id: str, ticket_data: dict, priority: int) -> None:
        """Add ticket to priority queue"""
        # Priority based on: 1. Emergency, 2. Time, 3. Distance
        heapq.heappush(self.heap, (priority, ticket_id))
        self.ticket_map[ticket_id] = ticket_data
    
    def pop(self) -> Optional[dict]:
        """Get highest priority ticket"""
        if not self.heap:
            return None
        
        priority, ticket_id = heapq.heappop(self.heap)
        ticket_data = self.ticket_map.pop(ticket_id, None)
        
        return {
            'ticket_id': ticket_id,
            'priority': priority,
            'data': ticket_data
        }
    
    def peek(self) -> Optional[dict]:
        """Peek highest priority ticket without removing"""
        if not self.heap:
            return None
        
        priority, ticket_id = self.heap[0]
        ticket_data = self.ticket_map.get(ticket_id)
        
        return {
            'ticket_id': ticket_id,
            'priority': priority,
            'data': ticket_data
        }
    
    def update_priority(self, ticket_id: str, new_priority: int) -> bool:
        """Update priority of existing ticket"""
        if ticket_id not in self.ticket_map:
            return False
        
        # Remove old entry
        for i, (priority, t_id) in enumerate(self.heap):
            if t_id == ticket_id:
                self.heap[i] = self.heap[-1]
                self.heap.pop()
                heapq.heapify(self.heap)
                break
        
        # Add with new priority
        heapq.heappush(self.heap, (new_priority, ticket_id))
        return True
    
    def size(self) -> int:
        return len(self.heap)

# ---------- Linked List for Booking History ----------
class HistoryNode:
    """Node for Booking History Linked List"""
    def __init__(self, booking_data: dict):
        self.data = booking_data
        self.next = None
        self.prev = None

class BookingHistory:
    """Doubly Linked List for Booking History"""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def add_booking(self, booking_data: dict) -> None:
        """Add booking to history"""
        new_node = HistoryNode(booking_data)
        
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        
        self.size += 1
    
    def get_recent_bookings(self, count: int = 10) -> List[dict]:
        """Get most recent bookings"""
        bookings = []
        current = self.head
        
        while current and len(bookings) < count:
            bookings.append(current.data)
            current = current.next
        
        return bookings
    
    def get_all_bookings(self) -> List[dict]:
        """Get all bookings in chronological order"""
        bookings = []
        current = self.head
        
        while current:
            bookings.append(current.data)
            current = current.next
        
        return bookings
    
    def search_by_ticket(self, ticket_id: str) -> Optional[dict]:
        """Search booking by ticket ID"""
        current = self.head
        
        while current:
            if current.data.get('ticket_id') == ticket_id:
                return current.data
            current = current.next
        
        return None
    
    def search_by_date(self, date: str) -> List[dict]:
        """Search bookings by date"""
        bookings = []
        current = self.head
        
        while current:
            if current.data.get('booking_date') == date:
                bookings.append(current.data)
            current = current.next
        
        return bookings

# ===================== DATA CLASSES =====================
@dataclass
class Ticket:
    """Ticket Data Class"""
    ticket_id: str
    passenger_id: str
    passenger_name: str
    passenger_contact: str
    bus_number: str
    route_id: str
    route_name: str
    from_stop: str
    to_stop: str
    departure_time: str
    arrival_time: str
    travel_date: str
    seat_number: int
    fare: float
    booking_time: str
    status: str = "confirmed"
    qr_code: str = None
    payment_status: str = "pending"
    
    def to_dict(self):
        return asdict(self)

@dataclass
class BusSchedule:
    """Bus Schedule Data Class"""
    bus_number: str
    route_id: str
    departure_time: str
    arrival_time: str
    capacity: int
    available_seats: int
    status: str  # on-time, delayed, cancelled
    driver_name: str
    driver_contact: str

# ===================== MAIN BOOKING SYSTEM =====================
class PassengerBookingSystem:
    """Main Booking System for Passengers"""
    def __init__(self, buses_file: str = 'data/buses.json', routes_file: str = 'data/routes.json'):
        self.buses_file = buses_file
        self.routes_file = routes_file
        
        # Initialize data structures
        self.passenger_bst = PassengerBST()
        self.transport_graph = TransportGraph()
        self.ticket_queue = TicketPriorityQueue()
        self.booking_history = BookingHistory()
        
        # Load data
        self.buses = self._load_json(buses_file)
        self.routes = self._load_json(routes_file)
        
        # Ticket counter
        self.ticket_counter = 1000
        
        # Initialize graph from routes
        self._build_transport_graph()
        
        # Load existing tickets
        self.tickets = self._load_tickets()
        
        # Booked seats tracking
        self.booked_seats = {}  # {bus_number_date: set(seat_numbers)}
    
    def _load_json(self, filename: str) -> Dict:
        """Load JSON file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def _save_json(self, data: Dict, filename: str) -> bool:
        """Save data to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving to {filename}: {e}")
            return False
    
    def _load_tickets(self) -> Dict:
        """Load tickets from file"""
        try:
            with open('data/tickets.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'tickets': [], 'next_id': 1000}
    
    def _save_tickets(self) -> bool:
        """Save tickets to file"""
        try:
            with open('data/tickets.json', 'w') as f:
                json.dump(self.tickets, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving tickets: {e}")
            return False
    
    def _build_transport_graph(self) -> None:
        """Build transport graph from routes data"""
        if 'routes' not in self.routes:
            return

        for route in self.routes['routes']:
            stops = route.get('stops', [])
            route_id = route.get('route_id', '')
            route_name = route.get('route_name', '')
            
            # Add stops to graph
            for stop in stops:
                stop_name = stop.get('stop_name', '')
                location = stop.get('location', '')
                lat = stop.get('latitude')
                lon = stop.get('longitude')
                
                self.transport_graph.add_stop(
                    stop_name=stop_name,
                    location=location,
                    latitude=lat,
                    longitude=lon
                )
            
            # Add connections between consecutive stops
            for i in range(len(stops) - 1):
                stop1 = stops[i].get('stop_name', '')
                stop2 = stops[i + 1].get('stop_name', '')
                wait_time = stops[i].get('wait_time', 5)
                distance = stops[i + 1].get('distance_from_previous', 5.0)
                try:
                    distance = float(distance)
                except (TypeError, ValueError):
                    distance = 5.0

                travel_minutes = int(distance * 2) + int(wait_time)
                fare = distance * 10

                # Add connection with travel time (estimated 5 minutes between stops + wait time)
                self.transport_graph.add_connection(
                    stop1=stop1,
                    stop2=stop2,
                    distance=distance,
                    time_minutes=travel_minutes,
                    route_id=route_id,
                    fare=fare
                )
    
    # ===================== PASSENGER MANAGEMENT =====================
    def register_passenger(self, passenger_data: Dict) -> Dict:
        """Register new passenger in BST"""
        passenger_id = str(uuid.uuid4())[:8]
        
        passenger_record = {
            'passenger_id': passenger_id,
            'full_name': passenger_data.get('full_name', ''),
            'email': passenger_data.get('email', ''),
            'phone': passenger_data.get('phone', ''),
            'address': passenger_data.get('address', ''),
            'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_bookings': 0,
            'total_spent': 0.0
        }
        
        # Insert into BST
        self.passenger_bst.insert(passenger_id, passenger_record)
        
        return {
            'success': True,
            'passenger_id': passenger_id,
            'message': 'Passenger registered successfully'
        }
    
    def search_passenger(self, passenger_id: str) -> Optional[Dict]:
        """Search passenger using BST O(log n)"""
        return self.passenger_bst.search(passenger_id)
    
    def get_passenger_travel_history(self, passenger_id: str) -> List[Dict]:
        """Get passenger's travel history"""
        # Search through booking history
        history = []
        all_bookings = self.booking_history.get_all_bookings()
        
        for booking in all_bookings:
            if booking.get('passenger_id') == passenger_id:
                history.append(booking)
        
        return history
    
    def update_passenger_stats(self, passenger_id: str, fare: float) -> None:
        """Update passenger statistics after booking"""
        passenger = self.passenger_bst.search(passenger_id)
        
        if passenger:
            passenger['total_bookings'] += 1
            passenger['total_spent'] += fare
    
    # ===================== TICKET BOOKING =====================
    def get_available_buses(self, from_stop: str, to_stop: str, date: str) -> List[Dict]:
        """Get available buses for a route on specific date"""
        available_buses = []
        
        if 'buses' not in self.buses:
            return available_buses
        
        current_time = datetime.now()
        travel_datetime = datetime.strptime(f"{date} 00:00", "%Y-%m-%d %H:%M")
        
        for bus in self.buses['buses']:
            # Check if bus is active and has route
            if bus.get('status') != 'active':
                continue
            
            route_name = bus.get('route_name', '')
            if not route_name:
                continue
            
            # Find route details
            route = None
            for r in self.routes.get('routes', []):
                if r.get('route_name') == route_name:
                    route = r
                    break
            
            if not route:
                continue
            
            # Check if route has both stops
            stops = [s['stop_name'] for s in route.get('stops', [])]
            if from_stop not in stops or to_stop not in stops:
                continue
            
            # Check if from_stop comes before to_stop
            from_idx = stops.index(from_stop)
            to_idx = stops.index(to_stop)
            
            if from_idx >= to_idx:
                continue
            
            # Calculate available seats
            bus_key = f"{bus['bus_number']}_{date}"
            booked_seats = self.booked_seats.get(bus_key, set())
            available_seats = bus.get('capacity', 50) - len(booked_seats)
            
            schedule = self._get_service_window(route, date)
            if not schedule:
                continue

            reference_time = current_time.time() if travel_datetime.date() == current_time.date() else None
            departure_time = self._calculate_departure_time(route, from_stop, date, reference_time=reference_time)
            if not departure_time:
                continue
            arrival_time = self._calculate_arrival_time(route, from_stop, to_stop, departure_time)
            
            bus_info = {
                'bus_number': bus['bus_number'],
                'plate_number': bus['plate_number'],
                'driver_name': bus['driver_name'],
                'driver_contact': bus.get('driver_contact', ''),
                'capacity': bus['capacity'],
                'available_seats': available_seats,
                'type': bus.get('type', 'regular'),
                'route_name': route_name,
                'route_id': route.get('route_id', ''),
                'from_stop': from_stop,
                'to_stop': to_stop,
                'departure_time': departure_time,
                'arrival_time': arrival_time,
                'estimated_travel_time': self._calculate_travel_time(route, from_idx, to_idx),
                'fare': self._calculate_fare(from_idx, to_idx, bus.get('type', 'regular'))
            }
            
            available_buses.append(bus_info)
        
        # Sort by departure time
        available_buses.sort(key=lambda x: x['departure_time'])
        
        return available_buses
    
    def _calculate_arrival_time(self, route: Dict, from_stop: str, to_stop: str, departure: str) -> str:
        """Calculate arrival time using timetable or fallbacks."""
        stops = route.get('stops', [])
        stop_names = [s.get('stop_name') for s in stops]
        if from_stop in stop_names and to_stop in stop_names:
            from_idx = stop_names.index(from_stop)
            to_idx = stop_names.index(to_stop)

            travel_minutes = self._calculate_travel_minutes(stops, from_idx, to_idx)
            departure_time = datetime.strptime(departure, "%H:%M")
            arrival_time = departure_time + timedelta(minutes=travel_minutes)
            return arrival_time.strftime("%H:%M")

        return "09:00"
    
    def _calculate_travel_time(self, route: Dict, from_idx: int, to_idx: int) -> str:
        """Calculate travel time between stops"""
        travel_minutes = self._calculate_travel_minutes(route.get('stops', []), from_idx, to_idx)
        hours = travel_minutes // 60
        minutes = travel_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def _calculate_travel_minutes(self, stops: List[Dict], from_idx: int, to_idx: int) -> int:
        """Calculate travel minutes between two stop indexes."""
        if to_idx <= from_idx:
            return 0

        travel_minutes = 0
        for idx in range(from_idx, to_idx):
            travel_minutes += 10
            travel_minutes += int(stops[idx + 1].get('wait_time', 0) or 0)
        return travel_minutes

    def _get_service_window(self, route: Dict, travel_date: str) -> Optional[Dict]:
        """Get service window for a route on a given date."""
        default_calendar = {
            "weekday": {"start_time": "06:00", "end_time": "22:00", "headway_minutes": 15},
            "weekend": {"start_time": "08:00", "end_time": "20:00", "headway_minutes": 20},
        }
        service_calendar = route.get('service_calendar') or {}
        service_calendar = {
            "weekday": {**default_calendar["weekday"], **service_calendar.get("weekday", {})},
            "weekend": {**default_calendar["weekend"], **service_calendar.get("weekend", {})},
        }

        try:
            travel_day = datetime.strptime(travel_date, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            travel_day = datetime.now().date()

        day_key = "weekend" if travel_day.weekday() >= 5 else "weekday"
        schedule = service_calendar.get(day_key, {})
        start_time = schedule.get("start_time", default_calendar[day_key]["start_time"])
        end_time = schedule.get("end_time", default_calendar[day_key]["end_time"])
        headway_minutes = schedule.get("headway_minutes", route.get("headway_minutes", default_calendar[day_key]["headway_minutes"]))

        try:
            headway_minutes = int(headway_minutes)
        except (TypeError, ValueError):
            headway_minutes = default_calendar[day_key]["headway_minutes"]

        return {
            "day_key": day_key,
            "start_time": start_time,
            "end_time": end_time,
            "headway_minutes": headway_minutes,
        }

    def _calculate_departure_time(
        self,
        route: Dict,
        from_stop: str,
        travel_date: str,
        reference_time: Optional[time] = None,
    ) -> Optional[str]:
        """Calculate next departure time from a stop using route timetable."""
        service = self._get_service_window(route, travel_date)
        if not service:
            return None

        stops = route.get('stops', [])
        stop_names = [s.get('stop_name') for s in stops]
        if from_stop not in stop_names:
            return None

        start_time = datetime.strptime(service["start_time"], "%H:%M")
        stop_idx = stop_names.index(from_stop)
        stop = stops[stop_idx]

        base_departure = None
        if stop.get('departure_time'):
            base_departure = datetime.strptime(stop['departure_time'], "%H:%M")
        elif stop.get('arrival_time'):
            base_departure = datetime.strptime(stop['arrival_time'], "%H:%M")

        if not base_departure:
            offset_minutes = 0
            for idx in range(stop_idx):
                offset_minutes += 10
                offset_minutes += int(stops[idx].get('wait_time', 0) or 0)
            base_departure = start_time + timedelta(minutes=offset_minutes)

        if reference_time is None:
            return base_departure.strftime("%H:%M")

        headway = stop.get('headway_minutes', service["headway_minutes"])
        try:
            headway = int(headway)
        except (TypeError, ValueError):
            headway = service["headway_minutes"]

        end_time = datetime.strptime(service["end_time"], "%H:%M")
        reference_dt = datetime.combine(datetime.today(), reference_time)
        base_dt = datetime.combine(reference_dt.date(), base_departure.time())
        end_dt = datetime.combine(reference_dt.date(), end_time.time())

        if reference_dt <= base_dt:
            return base_dt.strftime("%H:%M")

        if headway <= 0:
            return None

        diff_minutes = int((reference_dt - base_dt).total_seconds() / 60)
        intervals = (diff_minutes + headway - 1) // headway
        next_departure = base_dt + timedelta(minutes=intervals * headway)

        if next_departure > end_dt:
            return None

        return next_departure.strftime("%H:%M")
    
    def _calculate_fare(self, from_idx: int, to_idx: int, bus_type: str) -> float:
        """Calculate fare based on distance and bus type"""
        distance = to_idx - from_idx
        base_fare = 50
        
        # Distance-based fare
        fare = base_fare + (distance * 10)
        
        # Bus type multiplier
        if bus_type == 'air_conditioned':
            fare *= 1.5
        elif bus_type == 'luxury':
            fare *= 2.0
        
        return round(fare, 2)
    
    def book_ticket(self, booking_data: Dict) -> Dict:
        """Book a new ticket"""
        # Generate ticket ID
        ticket_id = f"TKT{self.ticket_counter:06d}"
        self.ticket_counter += 1
        
        # Get bus details
        bus_number = booking_data.get('bus_number')
        travel_date = booking_data.get('travel_date')
        from_stop = booking_data.get('from_stop')
        to_stop = booking_data.get('to_stop')
        
        # Find bus
        bus = None
        for b in self.buses.get('buses', []):
            if b['bus_number'] == bus_number:
                bus = b
                break
        
        if not bus:
            return {'success': False, 'message': 'Bus not found'}
        
        # Get route
        route = None
        for r in self.routes.get('routes', []):
            if r.get('route_name') == bus.get('route_name'):
                route = r
                break
        
        if not route:
            return {'success': False, 'message': 'Route not found'}
        
        # Calculate fare
        stops = [s['stop_name'] for s in route.get('stops', [])]
        from_idx = stops.index(from_stop) if from_stop in stops else 0
        to_idx = stops.index(to_stop) if to_stop in stops else len(stops)-1
        fare = self._calculate_fare(from_idx, to_idx, bus.get('type', 'regular'))
        
        # Assign seat
        bus_key = f"{bus_number}_{travel_date}"
        if bus_key not in self.booked_seats:
            self.booked_seats[bus_key] = set()
        
        seat_number = 1
        while seat_number <= bus['capacity']:
            if seat_number not in self.booked_seats[bus_key]:
                self.booked_seats[bus_key].add(seat_number)
                break
            seat_number += 1
        
        if seat_number > bus['capacity']:
            return {'success': False, 'message': 'No seats available'}
        
        # Calculate timings
        departure_time = self._calculate_departure_time(route, from_stop, travel_date)
        if not departure_time:
            return {'success': False, 'message': 'No scheduled departures available for the selected date'}
        arrival_time = self._calculate_arrival_time(route, from_stop, to_stop, departure_time)
        
        # Create ticket
        ticket = Ticket(
            ticket_id=ticket_id,
            passenger_id=booking_data.get('passenger_id', ''),
            passenger_name=booking_data.get('passenger_name', ''),
            passenger_contact=booking_data.get('passenger_contact', ''),
            bus_number=bus_number,
            route_id=route.get('route_id', ''),
            route_name=route.get('route_name', ''),
            from_stop=from_stop,
            to_stop=to_stop,
            departure_time=departure_time,
            arrival_time=arrival_time,
            travel_date=travel_date,
            seat_number=seat_number,
            fare=fare,
            booking_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            qr_code=self._generate_qr_code(ticket_id),
            payment_status='paid'
        )
        
        # Add to tickets data
        ticket_dict = ticket.to_dict()
        
        if 'tickets' not in self.tickets:
            self.tickets['tickets'] = []
        
        self.tickets['tickets'].append(ticket_dict)
        self.tickets['next_id'] = self.ticket_counter
        
        # Add to booking history (Linked List)
        self.booking_history.add_booking(ticket_dict)
        
        # Add to priority queue (emergency tickets get higher priority)
        priority = 100 if booking_data.get('emergency', False) else 10
        self.ticket_queue.push(ticket_id, ticket_dict, priority)
        
        # Update passenger statistics
        self.update_passenger_stats(booking_data.get('passenger_id', ''), fare)
        
        # Update bus passenger count
        self._update_bus_passenger_count(bus_number, 1)
        
        # Save data
        self._save_tickets()
        
        # Generate downloadable ticket
        download_path = self._generate_ticket_download(ticket)
        
        return {
            'success': True,
            'ticket_id': ticket_id,
            'ticket': ticket_dict,
            'download_url': download_path,
            'message': 'Ticket booked successfully'
        }
    
    def _update_bus_passenger_count(self, bus_number: str, change: int) -> None:
        """Update passenger count for a bus"""
        if 'buses' in self.buses:
            for bus in self.buses['buses']:
                if bus['bus_number'] == bus_number:
                    bus['current_passengers'] = bus.get('current_passengers', 0) + change
                    bus['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    break
            
            # Save updated buses
            self._save_json(self.buses, self.buses_file)
    
    def _generate_qr_code(self, ticket_id: str) -> str:
        """Generate QR code data (simulated)"""
        return f"BUS:{ticket_id}:{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def _generate_ticket_download(self, ticket: Ticket) -> str:
        """Generate downloadable ticket file"""
        filename = f"tickets/ticket_{ticket.ticket_id}.txt"
        
        # Create tickets directory if not exists
        import os
        os.makedirs('tickets', exist_ok=True)
        
        ticket_content = f"""
========================================
        BUS TICKET
========================================
Ticket ID: {ticket.ticket_id}
Booking Date: {ticket.booking_time}
Status: {ticket.status}
----------------------------------------
PASSENGER INFORMATION
Name: {ticket.passenger_name}
Contact: {ticket.passenger_contact}
----------------------------------------
JOURNEY DETAILS
From: {ticket.from_stop}
To: {ticket.to_stop}
Date: {ticket.travel_date}
----------------------------------------
BUS DETAILS
Bus Number: {ticket.bus_number}
Route: {ticket.route_name}
Seat Number: {ticket.seat_number}
----------------------------------------
TIMINGS
Departure: {ticket.departure_time}
Arrival: {ticket.arrival_time}
----------------------------------------
FARE: Rs. {ticket.fare}
Payment Status: {ticket.payment_status}
----------------------------------------
QR Code: {ticket.qr_code}
========================================
Important:
1. Please arrive at the stop 10 minutes before departure
2. Keep this ticket for verification
3. Contact 0800-12345 for assistance
========================================
"""
        
        with open(filename, 'w') as f:
            f.write(ticket_content)
        
        return filename
    
    # ===================== ROUTE PLANNING =====================
    def find_shortest_route(self, from_stop: str, to_stop: str, criteria: str = 'time') -> Dict:
        """Find shortest route using Dijkstra's algorithm"""
        return self.transport_graph.dijkstra_shortest_path(from_stop, to_stop, criteria)
    
    def find_nearest_stop(self, location: str) -> Dict:
        """Find nearest bus stop to a location"""
        # Use BFS to find nearest stop with matching location
        if not self.transport_graph.nodes:
            return {'nearest_stop': None, 'distance': float('inf')}
        
        # Start from first node
        start_node = list(self.transport_graph.nodes.keys())[0]
        return self.transport_graph.bfs_nearest_stop(start_node, location)
    
    def find_all_routes(self, start_stop: str, max_depth: int = 3) -> List[List[str]]:
        """Find all possible routes from a stop using DFS"""
        return self.transport_graph.dfs_find_routes(start_stop, max_depth)
    
    def check_route_cycle(self) -> bool:
        """Check if transport network has cycles"""
        return self.transport_graph.has_cycle()
    
    # ===================== TICKET MANAGEMENT =====================
    def cancel_ticket(self, ticket_id: str) -> Dict:
        """Cancel a booked ticket"""
        ticket_found = False
        
        for i, ticket in enumerate(self.tickets.get('tickets', [])):
            if ticket['ticket_id'] == ticket_id:
                # Update status
                ticket['status'] = 'cancelled'
                ticket['cancellation_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Free up seat
                bus_key = f"{ticket['bus_number']}_{ticket['travel_date']}"
                if bus_key in self.booked_seats and ticket['seat_number'] in self.booked_seats[bus_key]:
                    self.booked_seats[bus_key].remove(ticket['seat_number'])
                
                # Update bus passenger count
                self._update_bus_passenger_count(ticket['bus_number'], -1)
                
                # Update priority queue
                self.ticket_queue.update_priority(ticket_id, 0)  # Lowest priority for cancelled
                
                ticket_found = True
                break
        
        if ticket_found:
            self._save_tickets()
            return {'success': True, 'message': 'Ticket cancelled successfully'}
        
        return {'success': False, 'message': 'Ticket not found'}
    
    def get_ticket_details(self, ticket_id: str) -> Optional[Dict]:
        """Get details of a specific ticket"""
        for ticket in self.tickets.get('tickets', []):
            if ticket['ticket_id'] == ticket_id:
                return ticket
        
        return None
    
    def get_passenger_tickets(self, passenger_id: str) -> List[Dict]:
        """Get all tickets for a passenger"""
        passenger_tickets = []
        
        for ticket in self.tickets.get('tickets', []):
            if ticket.get('passenger_id') == passenger_id:
                passenger_tickets.append(ticket)
        
        return passenger_tickets
    
    def get_priority_ticket(self) -> Optional[Dict]:
        """Get highest priority ticket"""
        return self.ticket_queue.peek()
    
    # ===================== STATISTICS =====================
    def get_system_statistics(self) -> Dict:
        """Get system statistics"""
        total_tickets = len(self.tickets.get('tickets', []))
        active_tickets = len([t for t in self.tickets.get('tickets', []) if t.get('status') == 'confirmed'])
        cancelled_tickets = len([t for t in self.tickets.get('tickets', []) if t.get('status') == 'cancelled'])
        
        total_revenue = sum(t.get('fare', 0) for t in self.tickets.get('tickets', []) 
                          if t.get('status') == 'confirmed' and t.get('payment_status') == 'paid')
        
        total_passengers = len(self.passenger_bst.get_all_passengers())
        
        return {
            'total_tickets': total_tickets,
            'active_tickets': active_tickets,
            'cancelled_tickets': cancelled_tickets,
            'total_revenue': round(total_revenue, 2),
            'total_passengers': total_passengers,
            'priority_queue_size': self.ticket_queue.size(),
            'booking_history_size': self.booking_history.size,
            'transport_nodes': len(self.transport_graph.nodes),
            'average_fare': round(total_revenue / active_tickets, 2) if active_tickets > 0 else 0
        }
