from abc import ABC, abstractmethod
from datetime import datetime
import math




class Vehicle(ABC):
    def __init__(self, license_plate):
        self.license_plate = license_plate

    @property
    @abstractmethod
    def size_required(self):
        pass

    @property
    @abstractmethod
    def hourly_rate(self):
        pass


class Bike(Vehicle):
    size_required = 1
    hourly_rate = 5.0


class Car(Vehicle):
    size_required = 2
    hourly_rate = 10.0


class Truck(Vehicle):
    size_required = 3
    hourly_rate = 20.0


class ParkingSpot:
    def __init__(self, spot_id, size):
        self.spot_id = spot_id
        self.size = size
        self.vehicle = None

    def is_available(self):
        return self.vehicle is None

    def can_fit(self, vehicle):
        return self.is_available() and self.size >= vehicle.size_required

    def park(self, vehicle):
        self.vehicle = vehicle

    def remove_vehicle(self):
        self.vehicle = None


class Ticket:
    def __init__(self, vehicle, spot):
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()


class ParkingLot:
    def __init__(self, num_small, num_med, num_large):
        self.spots = []

        for i in range(num_small): self.spots.append(ParkingSpot(f"S-{i}", 1))
        for i in range(num_med): self.spots.append(ParkingSpot(f"M-{i}", 2))
        for i in range(num_large): self.spots.append(ParkingSpot(f"L-{i}", 3))
        self.active_tickets = {}

    def park_vehicle(self, vehicle):
        for spot in self.spots:
            if spot.can_fit(vehicle):
                spot.park(vehicle)
                ticket = Ticket(vehicle, spot)
                self.active_tickets[vehicle.license_plate] = ticket
                return ticket
        return None

    def exit_vehicle(self, license_plate):
        if license_plate not in self.active_tickets:
            return None

        ticket = self.active_tickets.pop(license_plate)
        ticket.spot.remove_vehicle()


        duration = datetime.now() - ticket.entry_time
        hours = max(1, math.ceil(duration.total_seconds() / 3600))
        total_fee = hours * ticket.vehicle.hourly_rate

        return total_fee




def main():
    lot = ParkingLot(num_small=2, num_med=5, num_large=2)
    print("--- Parking System Active ---")

    while True:
        action = input("\n1. Park\n2. Exit\n3. Quit\n> ")

        if action == '1':
            v_type = input("Type (Bike/Car/Truck): ").strip().lower()
            plate = input("License Plate: ")


            types = {"bike": Bike, "car": Car, "truck": Truck}
            if v_type in types:
                vehicle = types[v_type](plate)
                ticket = lot.park_vehicle(vehicle)
                if ticket:
                    print(f"Parked in {ticket.spot.spot_id}")
                else:
                    print("No suitable spots available.")
            else:
                print("Invalid vehicle type.")

        elif action == '2':
            plate = input("License Plate: ")
            fee = lot.exit_vehicle(plate)
            if fee is not None:
                print(f"Vehicle exited. Total fee: ${fee}")
            else:
                print("Vehicle not found.")

        elif action == '3':
            break


if __name__ == "__main__":
    main()