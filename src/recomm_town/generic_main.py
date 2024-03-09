#!/usr/bin/env python3
from pathlib import Path
from functools import partial
import pyglet
pyglet.options["debug_gl"] = False

from recomm_town.app import App
from recomm_town.draw import Draw
from recomm_town.creator.parser import WorldParser
from recomm_town.reporter import TriviaReporter


def run(town: Path, match_time: int, fullscreen: bool):
    parser = WorldParser(town)
    parser.load()
    world = parser.create_world()

    app = App(world, match_time=match_time)
    if fullscreen:
        display = pyglet.canvas.get_display()
        screen = display.get_screens()[0]
        app.set_fullscreen(screen=screen)
    draw = Draw(app.batch, app.people_group, app.gui_group)
    draw.draw_gui(app.match_time)
    draw.draw_path(world.town.path, app.town_group)
    draw.draw_places(world.town.places, app.town_group)
    draw.draw_people(app, world.people, app.people_group)

    app.human_observers["draw"] = draw.track_human
    app.time_observers["draw"] = draw.tick_tock
    reporter = TriviaReporter(world.town.boundaries)
    app.time_observers["report"] = partial(reporter.write_on_minute, "wtf.json")
    reporter.register(world.people)
    try:
        app.run()
    finally:
        reporter.write("wtf.json")
