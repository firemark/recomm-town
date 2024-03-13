#!/usr/bin/env python3
from pathlib import Path
from functools import partial
from queue import Queue
from threading import Thread, Event
from time import sleep

import serial
import pyglet

pyglet.options["debug_gl"] = False

from recomm_town.app import App
from recomm_town.draw import Draw
from recomm_town.creator.parser import WorldParser
from recomm_town.reporter import TriviaReporter


def run(town: Path, match_time: int, fullscreen: bool, output_filename: str):
    parser = WorldParser(town)
    parser.load()
    world = parser.create_world()
    event_queue = Queue()

    app = App(world, event_queue, match_time=match_time)
    if fullscreen:
        display = pyglet.canvas.get_display()
        screen = display.get_screens()[0]
        app.set_fullscreen(screen=screen)
    draw = Draw(app.batch, app.people_group, app.gui_group, app.width, app.height)
    draw.draw_gui(app.match_time)
    draw.draw_blobs(world.town.boundaries, app.town_group)
    draw.draw_path(world.town.path, app.town_group)
    draw.draw_places(world.town.places, app.town_group)
    draw.draw_people(app, world.people, app.people_group)

    serial_thread_event = Event()
    serial_thread = Thread(
        target=_serial,
        args=(event_queue, serial_thread_event),
    )
    serial_thread.start()

    app.resize_observers["draw"] = draw.on_resize
    app.human_observers["draw"] = draw.track_human
    app.time_observers["draw"] = draw.tick_tock
    reporter = TriviaReporter(world.town.boundaries)
    app.time_observers["report"] = partial(reporter.write_on_minute, output_filename)
    reporter.register(world.people)
    try:
        app.run()
    finally:
        serial_thread_event.set()
        reporter.write(output_filename)


def _serial(event_queue: Queue, event: Event):
    conn = serial.Serial(port="/dev/ttyUSB0", baudrate=9600, timeout=0.1)
    while not event.is_set():
        for line in conn.readlines():
            match line.strip():
                case b"CHANGE-HUMAN":
                    event_queue.put("on_change_human")
                case b"CHANGE-PLACE":
                    event_queue.put("on_change_place")
        sleep(0.01)
    conn.close()
