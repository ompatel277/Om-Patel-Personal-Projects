## important download this
# pip install fastf1

import fastf1
import turtle
import time
import numpy as np
import csv

# User inputs
year = 2024
track = 'Spain'
session_type = 'R'
driver_code = 'LEC'
total_laps = 5

# API Setup
session = fastf1.get_session(year, track, session_type)
session.load()

if driver_code != "":
    driver_laps = session.laps.pick_drivers(driver_code)
    lap = driver_laps.pick_fastest()
else:
    lap = session.laps.pick_fastest()

telemetry = lap.get_telemetry()
circuit_info = session.get_circuit_info()

# Telemetry rotation function
def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)

telemetry_points = telemetry[['X', 'Y']].to_numpy()
angle = circuit_info.rotation / 180 * np.pi
rotated_points = rotate(telemetry_points, angle=angle)

x = rotated_points[:, 0].tolist()
y = rotated_points[:, 1].tolist()
speed = telemetry['Speed'].to_list()
gear = telemetry['nGear'].to_list()

min_x, max_x = min(x), max(x)
min_y, max_y = min(y), max(y)
mid_x = (min_x + max_x) / 2
mid_y = (min_y + max_y) / 2
scale = max(max_x - min_x, max_y - min_y) / 700

def to_turtle_coords(raw_x, raw_y):
    return (raw_x - mid_x) / scale, (raw_y - mid_y) / scale

# Trutle setup
screen = turtle.Screen()
screen.setup(width=1000, height=800)
screen.title(f"{track} {year} - Session: {session_type}")



# Draw track
track_turtle = turtle.Turtle()
track_turtle.hideturtle()
track_turtle.pensize(6)
track_turtle.color("gray")
track_turtle.penup()
tx0, ty0 = to_turtle_coords(x[0], y[0])
track_turtle.goto(tx0, ty0)
track_turtle.pendown()

for i in range(1, len(x)):
    tx, ty = to_turtle_coords(x[i], y[i])
    track_turtle.goto(tx, ty)

# Car
car = turtle.Turtle()
car.shape("turtle")
car.color("red")
car.pensize(3)
car.penup()
car.speed(0)
car.goto(to_turtle_coords(x[0], y[0]))
car.pendown()

# Lap info display
lap_info = turtle.Turtle()
lap_info.hideturtle()
lap_info.penup()
lap_info.color("black")
lap_info.goto(-480, 330)

# simulation
simulated_times = []
for lap_index in range(total_laps):
    simulated_times.append([])

fastest_sim_lap = None 

step_delay = 0.01

# automation
for lap_num in range(1, total_laps + 1):
    lap_start = time.time()
    for i in range(len(x)):
        tx, ty = to_turtle_coords(x[i], y[i])
        car.goto(tx, ty)

        current_time = time.time() - lap_start
        simulated_times[lap_num - 1].append(current_time)

        if fastest_sim_lap is None:
            display_fastest = 0
        else:
            display_fastest = fastest_sim_lap

        lap_info.clear()
        lap_info.write(
            f"Lap {lap_num}/{total_laps}   Fastest: {display_fastest:.2f} sec   Current: {current_time:.2f} sec")
        time.sleep(step_delay)

    lap_time = time.time() - lap_start
    if fastest_sim_lap is None or lap_time < fastest_sim_lap:
        fastest_sim_lap = lap_time

# csv
csv_filename = f'{track}_{year}_{session_type}_{driver_code or "fastest"}.csv'

with open(csv_filename, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)

    # header
    header = ['X', 'Y', 'Speed', 'nGear', 'Time', 'Driver']
    for i in range(total_laps):
        header.append(f'SimTime_Lap{i+1}')
    writer.writerow(header)

    # Write telemetry rows with sim times per coordinate
    for i in range(len(telemetry)):
        row = [
            telemetry['X'].iloc[i],
            telemetry['Y'].iloc[i],
            telemetry['Speed'].iloc[i],
            telemetry['nGear'].iloc[i],
            str(telemetry['Time'].iloc[i]),
            lap['Driver']
        ]

        sim_time_at_idx = []
        for lap_index in range(total_laps):  
            if i < len(simulated_times[lap_index]):
                sim_time_at_idx.append(simulated_times[lap_index][i])
            else:
                sim_time_at_idx.append('')

        writer.writerow(row + sim_time_at_idx)

screen.mainloop()
