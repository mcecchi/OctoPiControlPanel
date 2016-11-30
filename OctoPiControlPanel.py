#!/usr/bin/env python

"""
OctoPiControlPanel v0.1
"""
__author__ = "Mauro Cecchi"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE"

import os
import platform

import pygame
from cyrusbus import Bus
from pygame.locals import *

import pygbutton
from client import OctoPiClient
from config import OctoPiControlPanelConfig
from printer import Printer
from views.controlview import ControlView
from views.dashboardview import DashboardView
from views.graphview import GraphView
from views.menuview import MenuView
from views.settingsview import SettingsView


class OctoPiControlPanel():
    """
    @var done: anything can set to True to forcequit
    @var screen: points to: pygame.display.get_surface()        
    """

    def __init__(self, config):
        """
        .
        """
        self.bus = Bus()
        self.bus.subscribe("viewchange", self.handle_viewchange)

        self.config = config
        self.octopi_client = OctoPiClient(self.config.api_baseurl, self.config.apikey)
        self.printer = Printer()

        self.done = False

        self.background_image = pygame.image.load(os.path.join(self.config.script_directory, 'assets/background.png'))
        self.menu_button_image = os.path.join(self.config.script_directory, 'assets/button-menu.png')
        self.temperature_icon = pygame.image.load(
            os.path.join(self.config.script_directory, 'assets/icon-temperature.png'))

        self.menu = MenuView(self.config, self.bus)

        self.views = dict()
        self.views["dashboard"] = DashboardView(self.config, self.bus, self.octopi_client, self.printer)
        self.views["graph"] = GraphView(self.config, self.bus, self.printer)
        self.views["control"] = ControlView(self.config, self.bus, self.octopi_client)
        self.views["settings"] = SettingsView(self.config, self.bus)

        self.active_view = self.views["dashboard"]

        self.menu_open = False

        # Status flags
        self.getstate_ticks = pygame.time.get_ticks()

        if platform.system() == 'Linux':
            # Init framebuffer/touchscreen environment variables
            os.putenv('SDL_VIDEODRIVER', 'fbcon')
            os.putenv('SDL_FBDEV', '/dev/fb1')
            os.putenv('SDL_MOUSEDRV', 'TSLIB')
            os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

        # init pygame and set up screen
        pygame.init()
        if platform.system() == 'Windows' or platform.system() == 'Darwin':
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

        self.screen = pygame.display.set_mode((self.config.width, self.config.height))
        pygame.display.set_caption(self.config.caption)

        # Set font
        self.fntText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 12)
        self.fntTextSmall = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"),
                                             10)
        self.percent_txt = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 30)

        # backlight on off status and control
        self.bglight_ticks = pygame.time.get_ticks()
        self.bglight_on = True

        self.clock = pygame.time.Clock()

        self.btnMenu = pygbutton.PygButton((260, 0, 40, 40), normal=self.menu_button_image)

        # I couldnt seem to get at pin 252 for the backlight using the usual method, 
        # but this seems to work
        if platform.system() == 'Linux':
            os.system("echo 252 > /sys/class/gpio/export")
            os.system("echo 'out' > /sys/class/gpio/gpio252/direction")
            os.system("echo '1' > /sys/class/gpio/gpio252/value")

        # Init of class done
        print "OctoPiControlPanel initiated"

    def start(self):
        # OctoPiControlPanel started
        print "OctoPiControlPanel started!"
        print "---"

        # self.thread = Thread(target=self.state_thread)
        # self.thread.start()

        # Set status interval
        pygame.time.set_timer(USEREVENT + 1, self.config.updatetime)

        """ game loop: input, move, render"""
        while not self.done:
            # Handle events
            self.handle_events()

            # Is it time to turn of the backlight?
            if pygame.time.get_ticks() - self.bglight_ticks > self.config.backlightofftime and platform.system() == 'Linux':
                # disable the backlight
                os.system("echo '0' > /sys/class/gpio/gpio252/value")
                self.bglight_ticks = pygame.time.get_ticks()
                self.bglight_on = False

            # Draw everything
            self.draw()

        """ Clean up """
        # enable the backlight before quiting
        if platform.system() == 'Linux':
            os.system("echo '1' > /sys/class/gpio/gpio252/value")

        # OctoPiControlPanel is going down.
        print "OctoPiControlPanel is going down."

        """ Quit """
        pygame.quit()

    def handle_events(self):
        """handle all events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print "quit"
                self.done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print "Got escape key"
                    self.done = True

            # It should only be possible to click a button if you can see it
            #  e.g. the backlight is on
            if self.bglight_on:

                if self.menu_open:
                    self.menu.handle_event(event)
                else:
                    self.active_view.handle_event(event)

                if 'click' in self.btnMenu.handleEvent(event):
                    self.menu_open = not self.menu_open

            # Did the user click on the screen?
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Reset backlight counter
                self.bglight_ticks = pygame.time.get_ticks()

                if self.bglight_on == False and platform.system() == 'Linux':
                    # enable the backlight
                    os.system("echo '1' > /sys/class/gpio/gpio252/value")
                    self.bglight_on = True
                    print "Background light on."

            # Handle status update
            if event.type == USEREVENT + 1:
                self.state_thread()
                print "State update..."

    """
    Get status update from API, regarding temp etc.
    """

    def state_thread(self):
        # while not self.done:
        self.octopi_client.get_printer_status(self.printer)
        self.octopi_client.get_job_status(self.printer)
        self.octopi_client.get_connection_status(self.printer)

        # time.sleep(self.config.updatetime / 1000.0)

    def draw(self):
        self.clock.tick(30)

        # clear whole screen
        self.screen.blit(self.background_image, (0, 0))

        # render print progress background shade
        s = pygame.Surface((320 * self.printer.Completion / 100, 240), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.screen.blit(s, (0, 0))

        # Render current view
        if self.menu_open:
            self.menu.draw(self.screen)
        else:
            self.active_view.draw(self.screen)

        # Render menu button
        self.btnMenu.draw(self.screen)

        # Draw status bar
        self.screen.blit(self.temperature_icon, (0, 200))
        hot_end_label = self.fntText.render(
            u'Hot end: {0}\N{DEGREE SIGN}C ({1}\N{DEGREE SIGN}C)'.format(self.printer.HotEndTemp,
                                                                         self.printer.HotEndTempTarget), 1,
            (255, 255, 255))
        self.screen.blit(hot_end_label, (40, 205))
        bed_temp_label = self.fntText.render(
            u'Bed: {0}\N{DEGREE SIGN}C ({1}\N{DEGREE SIGN}C)'.format(self.printer.BedTemp, self.printer.BedTempTarget),
            1, (255, 255, 255))
        self.screen.blit(bed_temp_label, (40, 220))

        completion_label = self.percent_txt.render("{0:.1f}%".format(self.printer.Completion), 1, (255, 255, 255))
        self.screen.blit(completion_label, (310 - (completion_label.get_width()), 205))

        # update screen
        pygame.display.update()

    def handle_viewchange(self, eventkey, view_name):
        if view_name in self.views:
            self.active_view = self.views[view_name]
            self.menu_open = False

    # Reboot system
    def _reboot(self):
        if platform.system() == 'Linux':
            os.system("reboot")
        else:
            pygame.image.save(self.screen, "screenshot.jpg")

        self.done = True
        print "reboot"

        return

    # Shutdown system
    def _shutdown(self):
        if platform.system() == 'Linux':
            os.system("shutdown -h 0")

        self.done = True
        print "shutdown"

        return


if __name__ == '__main__':
    config = OctoPiControlPanelConfig.load_from_file()
    opp = OctoPiControlPanel(config)
    opp.start()
