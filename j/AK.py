# coding: utf-8
"""
          Jade Application Kit
 Author - Copyright (c) 2016 Vitor Lopes
 url    - https://codesardine.github.io/Jade-Application-Kit
"""

import argparse
import json
import os
import subprocess
import sys
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Gdk, WebKit2

def cml_options():
    # Create command line options
    option = argparse.ArgumentParser(description='''\
      Jade Application Kit
      --------------------
      Create desktop applications with
      Python, JavaScript and Webkit2
      Author : Vitor Lopes
      Licence: GPLv2
      url: https://codesardine.github.io/Jade-Application-Kit''', epilog='''\
      ex: jak /path/to/my/app/folder
      ex: jak -d http://my-url.com

      Press F11 for distraction free mode
      ''', formatter_class=argparse.RawTextHelpFormatter)
    option.add_argument("-d", "--debug", metavar='\b', help="Enable Developer Tools")
    option.add_argument("-vf", "--video", metavar='\b', help="Open a Video Floater on The screen corner")
    option.add_argument('route', nargs="?", help='''\
    Point to your application folder or url!
    ''')
    return option.parse_args()


options = cml_options()
path = os.getcwd()
jak_path = os.path.dirname(__file__)

if options.debug or options.video:
    options.route = sys.argv[2]

application_path = options.route

# if running as module
if application_path is None:
    # returns the path of the file importing the module
    application_path = os.path.dirname(os.path.abspath(sys.argv[0]))

if not application_path.startswith("http"):
    if application_path.endswith("/"):
        pass

    else:
        application_path += "/"


class Api:
    html = ""
    javascript = ""

    def openFile(file_name, access_mode="r"):
        """
            input:  filename and path.
            output: file contents.
        """
        try:
            with open(file_name, access_mode, encoding='utf-8') as file:
                return file.read()

        except IOError:
            print(file_name + " File not found.")
            sys.exit(0)


def load_window_css(css):
    styles = Gtk.CssProvider()

    if os.path.isfile(css):
        styles.load_from_path(css)

    else:
        styles.load_from_data(css)

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        styles,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def get_app_config():

    if application_path.startswith("http"):
        # web apps
        application_settings = path + "/application-settings.json"
        print(application_settings)

    else:
        application_settings = application_path + "application-settings.json"

    if os.path.exists(application_settings):
        # Open application-settings.json and return values

        application_settings = Api.openFile(application_settings)
        application_settings = json.loads(application_settings)

        application_name        = application_settings["application"]["name"]
        application_description = application_settings["application"].get("description")
        application_version     = application_settings["application"].get("version")
        application_author      = application_settings["application"].get("author")
        application_licence     = application_settings["application"].get("license")
        application_url         = application_settings["application"].get("url")

        application_window_hint_type   = application_settings["window"].get("hint_type")
        application_window_width       = application_settings["window"].get("width")
        application_window_height      = application_settings["window"].get("height")
        application_window_full_screen = application_settings["window"].get("fullscreen")
        application_window_resizable   = application_settings["window"].get("resizable")
        application_window_decorated   = application_settings["window"].get("decorated")
        application_window_transparent = application_settings["window"].get("transparent")
        application_window_icon        = application_settings["window"].get("window_icon")

        application_debug      = application_settings["webkit"].get("debug")
        application_cache      = application_settings["webkit"].get("cache")
        application_user_agent = application_settings["webkit"].get("user_agent")

    else:
        if options.video:
            application_name = "Video"

            application_description = \
                application_version = \
                application_author = \
                application_licence = \
                application_url = \
                application_user_agent = \
                application_window_full_screen = \
                application_window_transparent = \
                application_debug = \
                application_window_resizable = ""

            application_window_width = "640"
            application_window_height = "360"
            application_window_hint_type = "dialog"
            application_window_decorated = "no"
            application_cache = ""
            application_window_icon = ""

        else:
            application_name = \
                application_description = \
                application_version = \
                application_author = \
                application_licence = \
                application_url = \
                application_user_agent = \
                application_window_hint_type = \
                application_window_width = \
                application_window_height = \
                application_window_resizable = \
                application_window_decorated = \
                application_window_transparent = \
                application_window_icon = \
                application_debug = ""

            application_window_full_screen = "yes"
            application_cache = "none"

    return application_name, \
           application_description, \
           application_version, \
           application_author, \
           application_licence, \
           application_url, \
           application_user_agent, \
           application_path, \
           application_window_hint_type, \
           application_window_width, \
           application_window_height, \
           application_window_full_screen, \
           application_window_resizable, \
           application_window_decorated, \
           application_window_transparent, \
           application_window_icon, \
           application_debug, \
           application_cache


class AppWindow(Gtk.Window):

    def __init__(self):
        # get tuple values from function
        application_name, \
        application_description, \
        application_version, \
        application_author, \
        application_licence, \
        application_url, \
        application_user_agent, \
        application_path, \
        application_window_hint_type, \
        application_window_width, \
        application_window_height, \
        application_window_full_screen, \
        application_window_resizable, \
        application_window_decorated, \
        application_window_transparent, \
        application_window_icon, \
        application_debug, \
        application_cache = get_app_config()

        if application_window_hint_type == "desktop" or application_window_hint_type == "dock":
            Gtk.Window.__init__(self, title=application_name, skip_pager_hint=True, skip_taskbar_hint=True)

        else:
            Gtk.Window.__init__(self, title=application_name)

        # create webview
        context = WebKit2.WebContext.get_default()
        sm = context.get_security_manager()

        self.cookies = context.get_cookie_manager()
        self.manager = WebKit2.UserContentManager()
        self.webview = WebKit2.WebView.new_with_user_content_manager(self.manager)
        self.add(self.webview)
        self.settings = self.webview.get_settings()

        if application_user_agent:
            self.settings.set_user_agent(application_user_agent)

        print("Identifying User Agent as - " + self.settings.get_user_agent())

        cookiesPath = '/tmp/cookies.txt'
        storage = WebKit2.CookiePersistentStorage.TEXT
        policy = WebKit2.CookieAcceptPolicy.ALWAYS

        self.cookies.set_accept_policy(policy)
        self.cookies.set_persistent_storage(cookiesPath, storage)

        if application_cache == "local":
            cache_model = WebKit2.CacheModel.DOCUMENT_BROWSER

        elif application_cache == "online":
            cache_model = WebKit2.CacheModel.WEB_BROWSER
            self.settings.set_property("enable-offline-web-application-cache", True)
            self.settings.set_property("enable-dns-prefetching", True)
            self.settings.set_property("enable-page-cache", True)

        else:
            cache_model = WebKit2.CacheModel.DOCUMENT_VIEWER
            print("Cache model not set, default is NO CACHE")

        context.set_cache_model(cache_model)

        screen = Gtk.Window.get_screen(self)

        application_window_style = application_path + "window.css"

        if os.path.isfile(application_window_style):
            load_window_css(application_window_style)

        if application_window_transparent == "yes":

            # EXPERIMENTAL FEATURE:
            color = screen.get_rgba_visual()

            if color is not None and screen.is_composited():
                self.set_app_paintable(True)  # not sure if i need this

                css = b"""
                #jade-window, #jade-dock, #jade-desktop {
                    background-color: rgba(0,0,0,0);
                } """

                # TODO hint type dock, remove box shadow, need to find the right css class.
                # TODO hint type dock or desktop, transparent window appears black.
                # TODO this needs more testing maybe using cairo is a better option.

                load_window_css(css)
                self.webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))

            else:
                print("Your system does not supports composite windows")

        if application_window_hint_type == "desktop":
            Gtk.Window.set_name(self, 'jade-desktop')
            Gtk.Window.set_type_hint(self, Gdk.WindowTypeHint.DESKTOP)
            Gtk.Window.set_resizable(self, False)

        elif application_window_hint_type == "dialog":
            Gtk.Window.set_name(self, 'jade-popup')
            Gtk.Window.set_type_hint(self, Gdk.WindowTypeHint.DIALOG)

        elif application_window_hint_type == "tooltip":
            Gtk.Window.set_name(self, 'jade-tooltip')
            Gtk.Window.set_type_hint(self, Gdk.WindowTypeHint.TOOLTIP)

        elif application_window_hint_type == "notification":
            Gtk.Window.set_name(self, 'jade-notification')
            Gtk.Window.set_type_hint(self, Gdk.WindowTypeHint.NOTIFICATION)

        elif application_window_hint_type == "dock":
            Gtk.Window.set_type_hint(self, Gdk.WindowTypeHint.DOCK)
            Gtk.Window.set_name(self, 'jade-dock')

        else:
            Gtk.Window.set_type_hint(self, Gdk.WindowTypeHint.NORMAL)
            Gtk.Window.set_name(self, "jade-window")

        Gtk.Window.set_position(self, Gtk.WindowPosition.CENTER)
        window_icon = application_window_icon

        if os.path.isfile(window_icon):
            Gtk.Window.set_icon_from_file(self, window_icon)

        if application_window_resizable == "no":
            Gtk.Window.set_resizable(self, False)

        if application_window_decorated == "no":
            Gtk.Window.set_decorated(self, False)

        if application_window_full_screen == "yes":
            Gtk.Window.set_default_size(self, screen.width(), screen.height())

        else:
            Gtk.Window.set_default_size(self, int(application_window_width), int(application_window_height))

        if options.video:
            Gtk.Window.set_keep_above(self, True)
            Gtk.Window.set_gravity(self, Gdk.Gravity.SOUTH_EAST)
            #  in multi head setups this will be the last screen
            Gtk.Window.move(self ,screen.width(), screen.height())

        self.settings.set_enable_smooth_scrolling(self)

        self.settings.set_default_charset("UTF-8")
        self.settings.set_property("allow-universal-access-from-file-urls", True)
        self.settings.set_property("allow-file-access-from-file-urls", True)
        self.settings.set_property("enable-write-console-messages-to-stdout", True)
        self.settings.set_property("enable-spatial-navigation", True)  # this is good for usability
        self.settings.set_property("enable-java", False)
        self.settings.set_property("enable-plugins", False)
        self.settings.set_property("enable-accelerated-2d-canvas", True)
        self.settings.set_property("enable-site-specific-quirks", True)

        if application_debug == "yes" or options.debug:
            self.settings.set_property("enable-developer-extras", True)

            # disable all cache in debug mode
            self.settings.set_property("enable-offline-web-application-cache", False)
            self.settings.set_property("enable-page-cache", False)

        else:
            # Disable webview rigth click menu
            def disable_menu(*args):
                return True

            self.webview.connect("context-menu", disable_menu)

        screen_width = screen.width()
        screen_height = screen.height()

        # TODO javascript Api
        Api.javascript = '''
        var jadeApplication = {
        'name'         : '%(application_name)s',
        'description'  : '%(application_description)s',
        'version'      : '%(application_version)s',
        'author'       : '%(application_author)s',
        'license'      : '%(application_licence)s',
        'url'          : '%(application_url)s',
        'user_agent'   : '%(application_user_agent)s',
        'windowWidth'  : '%(application_window_width)s',
        'windowHeight' : '%(application_window_height)s',
        'screenWidth'  : %(screen_width)s,
        'screenHeight' : %(screen_height)s
        };
        jadeApplication.windowWidth = parseInt(jadeApplication.windowWidth);
        jadeApplication.windowHeight = parseInt(jadeApplication.windowHeight);
        if (isNaN(jadeApplication.windowWidth) || isNaN(jadeApplication.windowHeight)) {
            jadeApplication.windowWidth = jadeApplication.screenWidth;
            jadeApplication.windowHeight = jadeApplication.screenHeight;
        };
        ''' % locals()

        self.webview.run_javascript(Api.javascript)

        if os.path.isdir(application_path):

            index = application_path + "index.html"

            if os.path.isfile(index):
                index = "file://" + index
                self.webview.load_uri(index)
                print("index.html loaded in the webview.")

            else:
                application_path = "file://" + application_path
                self.webview.load_html(Api.html, application_path)
                print("Loaded webview as python module.")

        elif application_path.startswith("w") or application_path.startswith("h"):
            NOSSL_MSG = "You can only run unsecured url's in debug mode. Change "
            SSL_MSG = " forcing SSL"

            if not options.debug and application_path.startswith("http://"):
                application_path = application_path.replace("http:", "https:")
                print(NOSSL_MSG + "http: to https:" + SSL_MSG)

            print("URL loaded in the webview.")
            self.webview.load_uri(application_path)
            sm.register_uri_scheme_as_cors_enabled(application_path)
            print(sm.uri_scheme_is_cors_enabled(application_path))

        def on_key_press_event(self, event):

            if event.keyval == Gdk.KEY_F11:

                # distraction free mode, this only works on decorated windows
                is_fullscreen = self.get_window().get_state() & Gdk.WindowState.FULLSCREEN != False
                if is_fullscreen:
                    Gtk.Window.unfullscreen(self)

                else:
                    Gtk.Window.fullscreen(self)

                return True

        self.connect("key-press-event", on_key_press_event)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()  # maybe i should only show the window wen the webview finishes loading?


def main():
    AppWindow()
    Gtk.main()


def cml():
    if options.route:
        main()

    else:
        subprocess.call(["jak", "-h"])
