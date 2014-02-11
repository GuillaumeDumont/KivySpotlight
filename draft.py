import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.listview import ListView
from kivy.uix.gridlayout import GridLayout
from kivy.config import Config
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from functools import partial

bar_width = 500
bar_height = 25
max_items = 10
spacing = 5
item_spacing = 1
win_height = bar_height*max_items+item_spacing*max_items+2*spacing+bar_height

test = ['Inkscape: Vectorial drawing', 'Microsoft Paint', 'Visual Studio 2010', 'Visual Studio 2012', 'Dependency Walker',
        'Handler detector', 'Microsoft Communicator', 'Microsoft Outlook', 'Microsoft Excel', 'Microsoft Word', 'Microsoft Visio'
        , 'Microsoft Powerpoint', 'My Documents', 'Google Chrome', 'Internet Explorer', 'Device Manager']

class CustomLayout(GridLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(CustomLayout, self).__init__(**kwargs)

        with self.canvas.before:
            Color(.3, .3, .3, 1)
            self.rect = Rectangle(
                            size=self.size,
                            pos=self.pos)

        self.bind(
                    size=self._update_rect,
                    pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class AccessBar(App):

    def __init__(self, **kwargs):
        super(AccessBar, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'up':
            new_index = min(len(self._list.children)-1, self.index+1)
            Window.height = str(200)
        elif keycode[1] == 'down':
            new_index = max(0, self.index-1)
            self._app_window.size = 100, 100 
        elif keycode[1] == 'escape':
            keyboard.release()
            exit(0)
        else:
            return False
        self._update_list(new_index)
        return True

    def _update_list(self, new_index):
        old_index = self.index
        self.index = new_index
        self._list.children[old_index].background_color=(.5,.5,.5,0)
        self._list.children[self.index].background_color=(.7,.7,.7,1)

    def _on_item_clicked(self, item):
        new_index = self._list.children.index(item)
        self._update_list(new_index)

    def build(self):
#        layout = CustomLayout(cols=1, width=bar_width, padding=(5,5), spacing=spacing)
        layout = GridLayout(cols=1, width=bar_width, padding=(5,5), spacing=spacing)
        with layout.canvas.before:
            Color(.3, .3, .3, 1)
        input_box = TextInput(text=''
            , size_hint=(None, None)
            , size=(bar_width, bar_height)
            , line_height=bar_height
            , font_size=14
            , multiline=False
            , Focus = True)
        choices = GridLayout(cols=1, width=bar_width, spacing=item_spacing, size_hint=(None, None))
        choices.bind(minimum_height=choices.setter('height'))

        for i in test:
            btn = Button(text=i
                , height=bar_height
                , size_hint=(1, None)
                , valign='middle'
                , halign='left'
                , text_size=(bar_width-(spacing*2), bar_height)
                , background_color=(.5,.5,.5,0))
            btn.bind(on_press=self._on_item_clicked)
            choices.add_widget(btn)
        self.index = len(choices.children)-1
        choices.children[self.index].background_color=(.7,.7,.7,1)

        scroller_height = (bar_height+item_spacing)*max_items
        scroller = ScrollView(size_hint=(None, None)
            , height=scroller_height
            , width=bar_width
            , scroll_distance = 10
            , scroll_type = ['bars']
            , do_scroll_x=False
            , bar_width=10)
        scroller.add_widget(choices)

        layout.add_widget(input_box)
        layout.add_widget(scroller)
        self._layout = layout
        self._list = choices
        self._scroller = scroller
        return layout

if __name__ == '__main__':
    Config.set('graphics', 'fullscreen', 'fake')
    Config.set('graphics', 'width', str(bar_width + 10))
    Config.set('graphics', 'height', str(win_height))
    Config.set('graphics', 'position', 'custom')
    Config.set('graphics', 'top', '100')
    Config.set('graphics', 'left', '100')
    Config.write()
    AccessBar().run()
