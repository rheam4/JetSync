import datetime


class JetLagAdjuster:
    def __init__(self, departure, arrival, origin_tz, destination_tz, current_bedtime="00:00", current_waketime="08:00", days_before_departure=3, days_after_arrival=3):
        self.departure = datetime.datetime.strptime(departure, '%Y-%m-%d %H:%M')
        self.arrival = datetime.datetime.strptime(arrival, '%Y-%m-%d %H:%M')
        self.origin_tz = int(origin_tz)
        self.destination_tz = int(destination_tz)
        self.current_bedtime = datetime.datetime.strptime(current_bedtime, "%H:%M").time()
        self.current_waketime = datetime.datetime.strptime(current_waketime, "%H:%M").time()
        self.days_before_departure = int(days_before_departure)
        self.days_after_arrival = int(days_after_arrival)
        self.time_difference = self.origin_tz - self.destination_tz

        self.schedule = []
        self.new_bedtime = self.current_bedtime
        self.new_waketime = self.current_waketime
        self.current_sleep_hours = self._time_difference_in_hours(self.current_waketime, self.current_bedtime)
        self.origin_arrival_time = self.arrival + datetime.timedelta(hours=self.time_difference)
        self.flight_duration = self.origin_arrival_time - self.departure

    @staticmethod
    def _add_hours_to_time(base_time, hours):
        """Adds or subtracts hours from a `datetime.time` object and wraps around if needed."""
        base_datetime = datetime.datetime.combine(datetime.date.today(), base_time)
        new_datetime = base_datetime + datetime.timedelta(hours=hours)
        return new_datetime.time()

    @staticmethod
    def _time_difference_in_hours(end_time, start_time):
        """Computes the hour difference between two `datetime.time` objects."""
        end = datetime.datetime.combine(datetime.date.today(), end_time)
        start = datetime.datetime.combine(datetime.date.today(), start_time)
        delta = (end - start).seconds / 3600
        return delta

    def calculate_pre_adjustment_schedule(self, days_before_departure, shift_per_day):
        for day in range(days_before_departure):
            self.new_bedtime = self._add_hours_to_time(self.new_bedtime, shift_per_day)
            self.new_waketime = self._add_hours_to_time(self.new_waketime, shift_per_day)
            self.schedule.append({
                'day': f'Day {-days_before_departure + day}',
                'bedtime': self.new_bedtime.strftime("%H:%M"),
                'waketime': self.new_waketime.strftime("%H:%M")
            })

    def calculate_post_arrival_schedule(self, days_after_arrival, shift_per_day):
        for day in range(1, days_after_arrival + 1):
            self.new_bedtime = self._add_hours_to_time(self.new_bedtime, shift_per_day)
            self.new_waketime = self._add_hours_to_time(self.new_waketime, shift_per_day)
            self.schedule.append({
                'day': f'Day {day}',
                'bedtime': self.new_bedtime.strftime("%H:%M"),
                'waketime': self.new_waketime.strftime("%H:%M")
            })

   
    def flight_day_schedule(self, days_before_departure, shift_per_day, offset):
          # Calculate preparation times
          departure_prep_time = self.departure - datetime.timedelta(hours=2)
          arrival_prep_time = self.origin_arrival_time + datetime.timedelta(hours=2)

          # Calculate flight day bedtime and waketime
          flight_day_bedtime = self._add_hours_to_time(self.current_bedtime, days_before_departure * shift_per_day + offset)
          flight_day_waketime = self._add_hours_to_time(self.current_waketime, days_before_departure * shift_per_day + offset)

          # Helper to determine if a time falls within bedtime and waketime range
          def is_within_sleep_window(time):
            if flight_day_bedtime <= flight_day_waketime:
              return flight_day_bedtime < time < flight_day_waketime
            else: # over midnight e.g., 23:30-04:15
              return flight_day_bedtime <= time or time < flight_day_waketime


          def is_departure_affected():
            return is_within_sleep_window(departure_prep_time.time()) and is_within_sleep_window(self.departure.time())

          def is_arrival_affected():
            return is_within_sleep_window(arrival_prep_time.time()) and is_within_sleep_window(self.origin_arrival_time.time())



          

          # Case 1: Departure and arrival times overlap with sleep window
          if is_departure_affected() and is_arrival_affected():
              if self.current_sleep_hours - 2 > self.flight_duration.total_seconds() / 3600:
                  if (flight_day_bedtime.hour - offset - arrival_prep_time.hour < departure_prep_time.hour - flight_day_waketime.hour):
                      return (arrival_prep_time - datetime.timedelta(hours=1)).time(), (arrival_prep_time + datetime.timedelta(hours=self.current_sleep_hours - 1)).time()
                  else:
                      return (departure_prep_time - datetime.timedelta(hours=self.current_sleep_hours)).time(), departure_prep_time.time()
              elif self.current_sleep_hours > self.flight_duration.total_seconds() / 3600:
                  return self.departure.time(), self.origin_arrival_time.time()
              else:
                  return self.departure.time(), (self.departure + datetime.timedelta(hours=self.current_sleep_hours)).time()


          # Case 2: Only Departure overlaps with sleep window
          if is_departure_affected():
              if self.current_sleep_hours - 2 > self.flight_duration.total_seconds() / 3600:
                  return (departure_prep_time - datetime.timedelta(hours=self.current_sleep_hours)).time(), departure_prep_time.time()
              elif self.current_sleep_hours > self.flight_duration.total_seconds() / 3600:
                  return self.departure.time(), self.origin_arrival_time.time()
              else:
                  return self.departure.time(), (self.departure + datetime.timedelta(hours=self.current_sleep_hours)).time()
                  

          # Case 3: Only arrival overlaps with sleep window
          if is_arrival_affected():
              if self.current_sleep_hours - 2 > self.flight_duration.total_seconds() / 3600:
                  return (arrival_prep_time - datetime.timedelta(hours=1)).time(), (arrival_prep_time + datetime.timedelta(hours=self.current_sleep_hours - 1)).time()
              elif self.current_sleep_hours > self.flight_duration.total_seconds() / 3600:
                  return self.departure.time(), self.origin_arrival_time.time()
              else:
                  return self.departure.time(), (self.departure + datetime.timedelta(hours=self.current_sleep_hours)).time()
                  

          # Default: Return calculated bedtime and waketime
          return flight_day_bedtime, flight_day_waketime


    def calculate_flight_day_schedule(self, shift_per_day, flight_day_bedtime, flight_day_waketime):
        self.new_bedtime = self._add_hours_to_time(self.new_bedtime, shift_per_day)
        self.new_waketime = self._add_hours_to_time(self.new_waketime, shift_per_day)
        self.schedule.append({
            'day': 'Day 0',
            'bedtime': flight_day_bedtime.strftime("%H:%M"),
            'waketime': flight_day_waketime.strftime("%H:%M")
        })

    def generate_optimal_schedule(self):
      shift_per_day = 2
      time_to_adjust = abs(self.time_difference)
      day_require = -(time_to_adjust // -shift_per_day)
      days_before_departure = (day_require - 1) // 2
      days_after_arrival = -((day_require - 1) // -2)
      offset = time_to_adjust % shift_per_day

      def calculate_days_to_adjust(current_time, target_time, shift_per_day):
        current_datetime_hour = current_time.hour
        target_datetime_hour = target_time.hour
        if ((target_datetime_hour - current_datetime_hour)%24 < (current_datetime_hour - target_datetime_hour)%24):
          delta_hours = (target_datetime_hour - current_datetime_hour)%24
          dir = "foward"
        else:
          delta_hours = (current_datetime_hour - target_datetime_hour)%24
          dir = "backward"

        return delta_hours // shift_per_day, dir, delta_hours % shift_per_day


      if self.time_difference < 0:
          flight_day_bedtime, flight_day_waketime = self.flight_day_schedule(days_before_departure, -shift_per_day, -offset)
          days_before_departure, dir_before, offset_before = calculate_days_to_adjust(self.current_bedtime, flight_day_bedtime, shift_per_day)
          bedtime_adjusted = (datetime.datetime.combine(datetime.date.today(), self.current_bedtime) + 
                               datetime.timedelta(hours=self.time_difference)).time()
          days_after_arrival, dir_after, offset_after = calculate_days_to_adjust(flight_day_bedtime, bedtime_adjusted, shift_per_day)
          
          
      else:
          flight_day_bedtime, flight_day_waketime = self.flight_day_schedule(days_before_departure, shift_per_day, offset)
          days_before_departure, dir_before, offset_before = calculate_days_to_adjust(self.current_bedtime, flight_day_bedtime, shift_per_day)
          bedtime_adjusted = (datetime.datetime.combine(datetime.date.today(), self.current_bedtime) + 
                               datetime.timedelta(hours=self.time_difference)).time()
          days_after_arrival, dir_after, offset_after = calculate_days_to_adjust(flight_day_bedtime, bedtime_adjusted, shift_per_day)

          

      if offset_before == 0 and offset_after == 0:
        offset = 2
        days_before_departure-=1
      elif offset_before == 1 and offset_after == 1:
        offset = 0
      else:
        offset = offset_before+offset_after


          

      if (dir_before == "backward"):
        self.calculate_pre_adjustment_schedule(days_before_departure, -shift_per_day)
      else:
        self.calculate_pre_adjustment_schedule(days_before_departure, shift_per_day)

      if (dir_before == "backward" and dir_after == "backward"):
        
        self.calculate_flight_day_schedule(-offset, flight_day_bedtime, flight_day_waketime)
      elif (dir_before == "foward" and dir_after == "foward"):   
        
        self.calculate_flight_day_schedule(offset, flight_day_bedtime, flight_day_waketime)
      elif(dir_before == "backward" and dir_after == "foward"):
        if offset == 0:
          offset = 2
        self.calculate_flight_day_schedule(-offset, flight_day_bedtime, flight_day_waketime)
      elif(dir_before == "foward" and dir_after == "backward"):
        if offset == 0:
          offset = 2
        self.calculate_flight_day_schedule(offset, flight_day_bedtime, flight_day_waketime)

      

      


      if (dir_after == "backward"):
        self.calculate_post_arrival_schedule(days_after_arrival, -shift_per_day)
      else:
        self.calculate_post_arrival_schedule(days_after_arrival, shift_per_day)



      return {
          'schedule': self.schedule,
          'flight_duration': self.flight_duration
      }


# Example Usage
# departure = "2024-12-03 23:00"
# arrival = "2024-12-04 20:00"
# origin_tz = "-5"  #fl NY
# destination_tz = "4"  # Dubai

departure = "2024-12-03 16:00"
arrival = "2024-12-04 23:00"
origin_tz = "-8"  # SF
destination_tz = "8"  # TW

adjuster = JetLagAdjuster(departure, arrival, origin_tz, destination_tz)
plan = adjuster.generate_optimal_schedule()

# Display the plan
print("Adjustment Schedule:")
for entry in plan['schedule']:
    print(f"{entry['day']}: Bedtime: {entry['bedtime']}, Waketime: {entry['waketime']}")

print(f"\nFlight Duration: {plan['flight_duration']}")
