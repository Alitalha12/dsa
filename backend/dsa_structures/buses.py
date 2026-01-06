# data_structures/buses.py
import json
from datetime import datetime, time, timedelta
import os
import heapq
from typing import List, Dict, Optional

class BusNode:
    def __init__(self, bus_data: Dict):
        self.bus_data = bus_data
        self.next = None
        self.prev = None

class DoublyLinkedListBus:
    """Doubly Linked List for Bus Management"""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def add_bus(self, bus_data: Dict) -> BusNode:
        """Add bus to the end of the list"""
        new_node = BusNode(bus_data)
        
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        
        self.size += 1
        return new_node
    
    def remove_bus(self, bus_id: int) -> bool:
        """Remove bus by ID"""
        current = self.head
        
        while current:
            if current.bus_data['id'] == bus_id:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                
                self.size -= 1
                return True
            
            current = current.next
        
        return False
    
    def find_bus(self, bus_id: int) -> Optional[BusNode]:
        """Find bus by ID"""
        current = self.head
        
        while current:
            if current.bus_data['id'] == bus_id:
                return current
            current = current.next
        
        return None
    
    def update_bus(self, bus_id: int, updated_data: Dict) -> bool:
        """Update bus information"""
        bus_node = self.find_bus(bus_id)
        
        if bus_node:
            bus_node.bus_data.update(updated_data)
            bus_node.bus_data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
        
        return False
    
    def get_all_buses(self) -> List[Dict]:
        """Get all buses as list"""
        buses = []
        current = self.head
        
        while current:
            buses.append(current.bus_data)
            current = current.next
        
        return buses
    
    def filter_by_status(self, status: str) -> List[Dict]:
        """Filter buses by status"""
        buses = []
        current = self.head
        
        while current:
            if current.bus_data.get('status') == status:
                buses.append(current.bus_data)
            current = current.next
        
        return buses
    
    def filter_by_route(self, route_id: int) -> List[Dict]:
        """Filter buses by route"""
        buses = []
        current = self.head
        
        while current:
            if current.bus_data.get('route_id') == route_id:
                buses.append(current.bus_data)
            current = current.next
        
        return buses

class MinHeapBusArrival:
    """Min Heap for Earliest Arriving Buses"""
    def __init__(self):
        self.heap = []
    
    def push(self, bus: Dict):
        """Add bus to min heap based on arrival time"""
        arrival_time = self._parse_time(bus['next_arrival'])
        heapq.heappush(self.heap, (arrival_time, bus))
    
    def pop(self) -> Optional[Dict]:
        """Get earliest arriving bus"""
        if self.heap:
            return heapq.heappop(self.heap)[1]
        return None
    
    def peek(self) -> Optional[Dict]:
        """Peek earliest arriving bus without removing"""
        if self.heap:
            return self.heap[0][1]
        return None
    
    def update_arrival(self, bus_id: int, new_arrival: str):
        """Update bus arrival time"""
        new_heap = []
        for arrival, bus in self.heap:
            if bus['id'] == bus_id:
                bus['next_arrival'] = new_arrival
                arrival = self._parse_time(new_arrival)
            heapq.heappush(new_heap, (arrival, bus))
        
        self.heap = new_heap
    
    def rebuild_heap(self, buses: List[Dict]):
        """Rebuild heap with new bus list"""
        self.heap = []
        for bus in buses:
            self.push(bus)
    
    def _parse_time(self, time_str: str) -> time:
        """Parse time string to time object"""
        return datetime.strptime(time_str, "%H:%M").time()
    
    def get_all_buses_sorted(self) -> List[Dict]:
        """Get all buses sorted by arrival time"""
        sorted_buses = []
        temp_heap = self.heap.copy()
        
        while temp_heap:
            sorted_buses.append(heapq.heappop(temp_heap)[1])
        
        return sorted_buses

class MaxHeapBusPriority:
    """Max Heap for Peak Hour Priority"""
    def __init__(self):
        self.heap = []
    
    def push(self, bus: Dict):
        """Add bus to max heap based on priority score"""
        priority_score = self._calculate_priority_score(bus)
        heapq.heappush(self.heap, (-priority_score, bus))
    
    def pop(self) -> Optional[Dict]:
        """Get highest priority bus"""
        if self.heap:
            return heapq.heappop(self.heap)[1]
        return None
    
    def peek(self) -> Optional[Dict]:
        """Peek highest priority bus without removing"""
        if self.heap:
            return self.heap[0][1]
        return None
    
    def _calculate_priority_score(self, bus: Dict) -> float:
        """Calculate priority score for bus"""
        score = 0
        
        # Arrival time factor
        arrival_time = datetime.strptime(bus['next_arrival'], "%H:%M").time()
        
        # Peak hours weight
        if (time(7, 0) <= arrival_time <= time(9, 0)) or \
           (time(17, 0) <= arrival_time <= time(19, 0)):
            score += 50
        
        # Route demand factor
        score += bus.get('route_demand', 0)
        
        # Bus capacity factor (higher capacity = higher priority)
        score += bus.get('capacity', 50) / 10
        
        # Current load factor
        load_percentage = (bus.get('current_passengers', 0) / bus.get('capacity', 50)) * 100
        if load_percentage > 80:
            score += 30
        elif load_percentage > 60:
            score += 20
        
        return score
    
    def rebuild_heap(self, buses: List[Dict]):
        """Rebuild heap with new bus list"""
        self.heap = []
        for bus in buses:
            self.push(bus)
    
    def get_priority_queue(self) -> List[Dict]:
        """Get all buses sorted by priority"""
        sorted_buses = []
        temp_heap = self.heap.copy()
        
        while temp_heap:
            _, bus = heapq.heappop(temp_heap)
            sorted_buses.append(bus)
        
        return sorted_buses

class BusGraph:
    """Graph for Bus Network"""
    def __init__(self):
        self.graph = {}
    
    def add_bus_route(self, bus_id: int, stops: List[str]):
        """Add bus route to graph"""
        self.graph[bus_id] = {
            'stops': stops,
            'connections': []
        }
    
    def connect_buses(self, bus1_id: int, bus2_id: int, connection_point: str):
        """Connect two buses at a common stop"""
        if bus1_id in self.graph and bus2_id in self.graph:
            if connection_point in self.graph[bus1_id]['stops'] and \
               connection_point in self.graph[bus2_id]['stops']:
                self.graph[bus1_id]['connections'].append({
                    'bus_id': bus2_id,
                    'connection_point': connection_point
                })
                self.graph[bus2_id]['connections'].append({
                    'bus_id': bus1_id,
                    'connection_point': connection_point
                })
    
    def get_connecting_buses(self, bus_id: int) -> List[Dict]:
        """Get all buses connected to a given bus"""
        if bus_id in self.graph:
            return self.graph[bus_id]['connections']
        return []
    
    def find_transfer_points(self, start_bus: int, end_bus: int) -> List[str]:
        """Find possible transfer points between two buses"""
        transfer_points = []
        
        if start_bus in self.graph and end_bus in self.graph:
            start_stops = set(self.graph[start_bus]['stops'])
            end_stops = set(self.graph[end_bus]['stops'])
            transfer_points = list(start_stops.intersection(end_stops))
        
        return transfer_points

class BusManager:
    """Main Bus Management System"""
    def __init__(self, data_file: str = 'data/buses.json', routes_file: str = 'data/routes.json'):
        self.data_file = data_file
        self.routes_file = routes_file
        self.routes_index = {"by_id": {}, "by_name": {}}
        self.bus_list = DoublyLinkedListBus()
        self.min_heap_arrival = MinHeapBusArrival()
        self.max_heap_priority = MaxHeapBusPriority()
        self.bus_graph = BusGraph()
        self.load_routes()
        self.load_data()

    def load_routes(self):
        if not os.path.exists(self.routes_file):
            return
        try:
            with open(self.routes_file, 'r') as f:
                data = json.load(f)
            for route in data.get('routes', []):
                route_id = route.get('route_id')
                route_name = route.get('route_name')
                if route_id:
                    self.routes_index["by_id"][str(route_id)] = route
                if route_name:
                    self.routes_index["by_name"][route_name] = route
        except Exception as e:
            print(f"Error loading routes: {e}")

    def _find_route_for_bus(self, bus):
        route_id = bus.get('route_id')
        route_name = bus.get('route_name')
        if route_id and str(route_id) in self.routes_index["by_id"]:
            return self.routes_index["by_id"][str(route_id)]
        if route_name and route_name in self.routes_index["by_name"]:
            return self.routes_index["by_name"][route_name]
        return None

    def _compute_next_arrival(self, route):
        service = route.get('service_calendar', {})
        schedule = service.get('weekday', {'start_time': '06:00', 'end_time': '22:00', 'headway_minutes': 15})
        start_time = schedule.get('start_time', '06:00')
        headway = schedule.get('headway_minutes', 15)
        try:
            headway = int(headway)
        except (TypeError, ValueError):
            headway = 15
        current_time = datetime.now().time()
        base = datetime.strptime(start_time, "%H:%M").time()
        base_dt = datetime.combine(datetime.today(), base)
        current_dt = datetime.combine(datetime.today(), current_time)
        if current_dt <= base_dt:
            return base_dt.time().strftime("%H:%M")
        diff = int((current_dt - base_dt).total_seconds() / 60)
        intervals = (diff + headway - 1) // headway
        next_dt = base_dt + timedelta(minutes=intervals * headway)
        return next_dt.time().strftime("%H:%M")

    def _normalize_bus_fields(self, bus):
        bus.setdefault('current_stop_index', 0)
        bus.setdefault('speed_kmph', 35)
        bus.setdefault('current_lat', None)
        bus.setdefault('current_lng', None)
        bus.setdefault('current_passengers', 0)
        if bus.get('next_arrival') in (None, "", "auto"):
            route = self._find_route_for_bus(bus)
            if route:
                bus['next_arrival'] = self._compute_next_arrival(route)
            else:
                bus['next_arrival'] = '08:00'
    
    def load_data(self):
        """Load bus data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                buses = json.load(f)
                for bus in buses:
                    self._normalize_bus_fields(bus)
                    self.bus_list.add_bus(bus)
                    self.min_heap_arrival.push(bus)
                    self.max_heap_priority.push(bus)
        except FileNotFoundError:
            # Create empty file if not exists
            self.save_data()
    
    def save_data(self):
        """Save bus data to JSON file"""
        buses = self.bus_list.get_all_buses()
        with open(self.data_file, 'w') as f:
            json.dump(buses, f, indent=4)
    
    def add_bus(self, bus_data: Dict) -> Dict:
        """Add new bus to system"""
        # Generate new ID
        existing_buses = self.bus_list.get_all_buses()
        new_id = max([bus['id'] for bus in existing_buses], default=0) + 1
        
        bus_data['id'] = new_id
        bus_data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bus_data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self._normalize_bus_fields(bus_data)

        # Add to data structures
        self.bus_list.add_bus(bus_data)
        self.min_heap_arrival.push(bus_data)
        self.max_heap_priority.push(bus_data)
        
        # Save to file
        self.save_data()
        
        return bus_data
    
    def update_bus(self, bus_id: int, updated_data: Dict) -> bool:
        """Update existing bus"""
        if updated_data.get('next_arrival') == 'auto':
            bus_node = self.bus_list.find_bus(bus_id)
            if bus_node:
                route = self._find_route_for_bus(bus_node.bus_data)
                if route:
                    updated_data['next_arrival'] = self._compute_next_arrival(route)
        success = self.bus_list.update_bus(bus_id, updated_data)
        
        if success:
            # Rebuild heaps with updated data
            all_buses = self.bus_list.get_all_buses()
            self.min_heap_arrival.rebuild_heap(all_buses)
            self.max_heap_priority.rebuild_heap(all_buses)
            self.save_data()
        
        return success
    
    def delete_bus(self, bus_id: int) -> bool:
        """Delete bus from system"""
        success = self.bus_list.remove_bus(bus_id)
        
        if success:
            # Rebuild heaps
            all_buses = self.bus_list.get_all_buses()
            self.min_heap_arrival.rebuild_heap(all_buses)
            self.max_heap_priority.rebuild_heap(all_buses)
            self.save_data()
        
        return success

    def update_bus_position(self, bus_id: int, lat: float, lng: float, stop_index: Optional[int] = None) -> bool:
        updates = {'current_lat': lat, 'current_lng': lng}
        if stop_index is not None:
            updates['current_stop_index'] = stop_index
        return self.update_bus(bus_id, updates)
    
    def allocate_bus_to_route(self, bus_id, route_id, route_name):
        """Allocate bus to specific route - UPDATED for UUID routes"""
        bus_node = self.bus_list.find_bus(bus_id)
        
        if bus_node:
            bus_node.bus_data['route_id'] = route_id  # Store as string (UUID)
            bus_node.bus_data['route_name'] = route_name
            
            # Update demand based on route (simulated)
            bus_node.bus_data['route_demand'] = 50
            self._normalize_bus_fields(bus_node.bus_data)
            
            # Rebuild heaps
            all_buses = self.bus_list.get_all_buses()
            self.min_heap_arrival.rebuild_heap(all_buses)
            self.max_heap_priority.rebuild_heap(all_buses)
            self.save_data()
            
            return True
        
        return False
    
    def get_next_arrival(self) -> Optional[Dict]:
        """Get next arriving bus"""
        return self.min_heap_arrival.peek()
    
    def get_priority_bus(self) -> Optional[Dict]:
        """Get highest priority bus"""
        return self.max_heap_priority.peek()
    
    def update_bus_arrival(self, bus_id: int, new_arrival: str):
        """Update bus arrival time after movement"""
        self.min_heap_arrival.update_arrival(bus_id, new_arrival)
        
        # Also update in main list
        self.bus_list.update_bus(bus_id, {'next_arrival': new_arrival})
        
        # Rebuild priority heap (scores may change)
        all_buses = self.bus_list.get_all_buses()
        self.max_heap_priority.rebuild_heap(all_buses)
        self.save_data()
    
    def get_buses_by_status(self, status: str) -> List[Dict]:
        """Get buses filtered by status"""
        return self.bus_list.filter_by_status(status)
    
    def get_buses_by_route(self, route_id: int) -> List[Dict]:
        """Get buses allocated to specific route"""
        return self.bus_list.filter_by_route(route_id)
    
    def get_bus_statistics(self) -> Dict:
        """Get bus system statistics"""
        all_buses = self.bus_list.get_all_buses()
        
        stats = {
            'total_buses': len(all_buses),
            'active_buses': len(self.bus_list.filter_by_status('active')),
            'inactive_buses': len(self.bus_list.filter_by_status('inactive')),
            'maintenance_buses': len(self.bus_list.filter_by_status('maintenance')),
            'total_capacity': sum(bus.get('capacity', 0) for bus in all_buses),
            'average_load': sum((bus.get('current_passengers', 0) / bus.get('capacity', 1)) * 100 
                               for bus in all_buses) / len(all_buses) if all_buses else 0,
            'next_arrival': self.min_heap_arrival.peek()['next_arrival'] if self.min_heap_arrival.peek() else 'N/A',
            'priority_bus': self.max_heap_priority.peek()['bus_number'] if self.max_heap_priority.peek() else 'N/A'
        }
        
        return stats

# Global instance
bus_manager = BusManager()
