import datetime

class JetLagAdjuster:
    def __init__(self, departure, arrival, origin_tz, destination_tz, current_bedtime = 24, current_waketime = 8, days_before_departure = 3, days_after_arrival = 3):
        self.departure = datetime.datetime.strptime(departure, '%Y-%m-%d %H:%M')
        self.arrival = datetime.datetime.strptime(arrival, '%Y-%m-%d %H:%M')
        self.origin_tz = int(origin_tz)
        self.destination_tz = int(destination_tz)
        self.current_bedtime = int(current_bedtime)
        self.current_waketime = int(current_waketime)
        self.days_before_departure = int(days_before_departure)
        self.days_after_arrival = int(days_after_arrival)
        self.time_difference = self.origin_tz - self.destination_tz
        self.flight_duration = self.arrival - self.departure
        self.schedule = []
        self.new_bedtime = self.current_bedtime
        self.new_waketime = self.current_waketime

    def calculate_pre_adjustment_schedule(self, days_before_departure, shift_per_day):
        for day in range(days_before_departure):
            self.new_bedtime = (self.new_bedtime + shift_per_day) % 24
            self.new_waketime = (self.new_waketime + shift_per_day) % 24
            self.schedule.append({
                'day': f'Day {-days_before_departure + day}',
                'bedtime': self.new_bedtime,
                'waketime': self.new_waketime
            })


    def calculate_flight_Day_schedule(self, shift_per_day):
        self.new_bedtime = (self.new_bedtime + shift_per_day) % 24
        self.new_waketime = (self.new_waketime + shift_per_day) % 24
        self.schedule.append({
                'day': f'Day {0}',
                'bedtime': self.new_bedtime,
                'waketime': self.new_waketime
            })


    def calculate_post_arrival_schedule(self, days_after_arrival, shift_per_day):
        for day in range(1, days_after_arrival + 1):
            self.new_bedtime = (self.new_bedtime + shift_per_day) % 24
            self.new_waketime = (self.new_waketime + shift_per_day) % 24
            self.schedule.append({
                'day': f'Day {day}',
                'bedtime': self.new_bedtime,
                'waketime': self.new_waketime
            })


    def generate_plan(self):
        if (self.time_difference < 0):
            time_to_adjust = -self.time_difference
        else:
            time_to_adjust = self.time_difference

        shift_per_day = time_to_adjust // (self.days_before_departure + self.days_after_arrival)

        if (shift_per_day == 0):
            return self.generate_optimal_schedule()

        offset = time_to_adjust % (self.days_before_departure + self.days_after_arrival)

        if (self.time_difference < 0):
            self.calculate_pre_adjustment_schedule(self.days_before_departure, -shift_per_day)
            self.calculate_flight_Day_schedule(-offset)
            self.calculate_post_arrival_schedule(self.days_after_arrival, -shift_per_day)
        else:
            self.calculate_pre_adjustment_schedule(self.days_before_departure, shift_per_day)
            self.calculate_flight_Day_schedule(offset)
            self.calculate_post_arrival_schedule(self.days_after_arrival, shift_per_day)

        return {
            'schedule': self.schedule,
            'time_difference': self.time_difference
        }

    def generate_optimal_schedule(self):
        shift_per_day = 2
        if (self.time_difference < 0):
          time_to_adjust = -self.time_difference
        else:
          time_to_adjust = self.time_difference

        day_require = -(time_to_adjust // -shift_per_day)

        days_before_departure = (day_require-1)// 2
        days_after_arrival = -((day_require-1) // -2)

        offset = time_to_adjust % shift_per_day

        if (self.time_difference < 0):
          self.calculate_pre_adjustment_schedule(days_before_departure, -shift_per_day)
          self.calculate_flight_Day_schedule(-offset)
          self.calculate_post_arrival_schedule(days_after_arrival, -shift_per_day)
        else:
          self.calculate_pre_adjustment_schedule(days_before_departure, shift_per_day)
          self.calculate_flight_Day_schedule(offset)
          self.calculate_post_arrival_schedule(days_after_arrival, shift_per_day)


        return {
            'schedule': self.schedule,
            'time_difference': self.time_difference
        }




# Example
departure = "2024-12-02 23:00"
arrival = "2024-12-03 15:00"
origin_tz = "-8"  
destination_tz = "1"  

adjuster = JetLagAdjuster(departure, arrival, origin_tz, destination_tz)
# plan = adjuster.generate_plan()
plan = adjuster.generate_optimal_schedule()

# Display
print("Adjustment Schedule:")
for entry in plan['schedule']:
    print(f"{entry['day']}: Bedtime: {entry['bedtime']}:00, Waketime: {entry['waketime']}:00")

print(f"\nTime Difference: {plan['time_difference']}")
