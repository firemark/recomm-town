#!/usr/bin/env python3
import argparse

import pyglet

pyglet.options["debug_gl"] = False

from recomm_town.app import App
from recomm_town.draw import Draw
from importlib import import_module


parser = argparse.ArgumentParser()
parser.add_argument("town")


if __name__ == "__main__":
    args = parser.parse_args()
    # TODO - change importing town to another format (XML?)
    module = import_module(f"recomm_town.creator.{args.town}")
    world = module.make_world()

    app = App(world)
    draw = Draw(app.batch, app.people_group)
    draw.draw_gui(len(world.people), app.gui_group)
    draw.draw_path(world.town.path, app.town_group)
    draw.draw_places(world.town.places, app.town_group)
    draw.draw_people(app, world.people, app.people_group)
    app.run()
