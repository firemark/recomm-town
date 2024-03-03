#!/usr/bin/env python3
import argparse
from functools import partial

import pyglet

from recomm_town.reporter import TriviaReporter

pyglet.options["debug_gl"] = False

from recomm_town.app import App
from recomm_town.draw import Draw
from recomm_town.creator.parser import WorldParser
from importlib import import_module


parser = argparse.ArgumentParser()
parser.add_argument("town")
parser.add_argument("--match-time", type=int, default=600)
parser.add_argument("--fullscreen", action="store_true")


if __name__ == "__main__":
    args = parser.parse_args()
    # TODO - change importing town to another format (XML?)
    module = import_module(f"recomm_town.creator.{args.town}")
    world = module.make_world()

    parser = WorldParser("towns/mixed.yaml")
    parser.load()

    app = App(world, match_time=args.match_time)
    if args.fullscreen:
        display = pyglet.canvas.get_display()
        screen = display.get_screens()[0]
        app.set_fullscreen(screen=screen)
    draw = Draw(app.batch, app.people_group, app.gui_group)
    draw.draw_gui(len(world.people), app.match_time)
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
