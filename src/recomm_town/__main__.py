#!/usr/bin/env python3
from recomm_town.app import App

from recomm_town.creator.default import make_world
from recomm_town.creator.isolated import make_world
from recomm_town.draw import Draw


if __name__ == "__main__":
    world = make_world()

    app = App(world)
    draw = Draw(app.batch, app.people_group)
    draw.draw_gui(len(world.people), app.gui_group)
    draw.draw_path(world.town.path, app.town_group)
    draw.draw_places(world.town.places, app.town_group)
    draw.draw_people(app, world.people, app.people_group)
    app.run()
