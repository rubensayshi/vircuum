from flask import current_app
from vircu.view.menu import Menu, MenuItem, PlaceholderMenuItem, SectionMenuItem, MailtoMenuItem, WILDCARD_VIEW_ARG

class MainMenu(Menu):
    def build_items(self):
        # register list_articles menu item
        self.add(MenuItem('Home',
                          endpoint='main.index',
                          faicon='fa-home',
                          weight=0))

