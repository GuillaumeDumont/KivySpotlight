###############################################################################
# 	@package docstring
#
#	@author 	Guillaume Dumont
# 	@project	KivySpotlight
#	@repo	 	http://github.com/GuillaumeDumont/KivySpotlight
#
#	@brief		Description of the graphical design of this app using Kivy
#
###############################################################################
''' standard imports '''
from __future__ import division
from operator import itemgetter
''' kivy imports '''
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.text.markup import MarkupLabel
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.widget import Widget

class Separator(Widget):
	'''
		The separator widget is used in order to separate two
		results in the spotlight
	'''
	def __init__(self, **kwargs):
		super(Separator, self).__init__(**kwargs)
		# the height of the separator is fixed
		self.height = kwargs.get('height', 2)
		# the width shall be the one of the parent
		self.size_hint = (1, None)
		self.padding = [0, 0, 0, 0]
		# draw a colored rectangle of the size of the widget
		with self.canvas:
		    Color(.4, .4, .4)
		    self.rect = Rectangle(pos=self.pos, size=self.size)
		# register a callback for when the widget changes
		self.bind(size=self._update_rect, pos=self._update_rect)

	def _update_rect(self, instance, value):
		''' this function is the callback that will adapt the size and position
			of the rectangle to the size of the widget when a change occurs '''
		self.rect.pos = instance.pos
		self.rect.size = instance.size

class ColoredGridLayout(GridLayout):
	''' Similar to the separator, but inherits from grid
		This creates a colored grid.. '''
	def __init__(self, **kwargs):
		super(ColoredGridLayout, self).__init__(**kwargs)
		with self.canvas.before:
			Color(.3, .3, .3, 1)
			self.rect = Rectangle(size=self.size, pos=self.pos)
			self.bind(size=self._update_rect, pos=self._update_rect)

	def _update_rect(self, instance, value):
		self.rect.pos = instance.pos
		self.rect.size = instance.size


Builder.load_file('SearchInput.kv')
class SearchInput(TextInput):
	''' This class derives from TextInput to change its style via the builder '''
	pass

class Spotlight(App):
	''' This class represents the kivy app that will run the spotlight '''

	def __init__(self, **kwargs):
		super(Spotlight, self).__init__(**kwargs)
		# fixed width of the app, will never change
		self._width = kwargs.get('width', 500)
		# tells how many entries can be displayed on the screen at the same time. The rest will be accessible via a scroller
		self._max_results_displayed = kwargs.get('max_results_displayed', 5)
		# gives the height of the separators that will be used between each entry
		self._sep_height = kwargs.get('sep_height', 1)
		# static height of the main search bar: SearchInput
		self._search_field_height = kwargs.get('search_field_height', 35)
		# height of each entry
		self._result_height = kwargs.get('result_height', 25)
		# this is the spacing between the search bar and the scroller containing the entries
		self._spacing = kwargs.get('spacing', 1)
		# this is the padding of the main window
		self._padding = 5
		# this is the space between each separator/result in the dropdown list
		self._result_spacing = kwargs.get('result_spacing', 1)
		# color of a non-selected entry
		self._inactive_button_color = (.0,.0,.0, 0)
		# color of a selected entry
		self._active_button_color = (.4, .4, .4, 1)
		# store all the visible entries on the screen as a pair (button, separator) for convenience
		self._results = []
		# index of the result that is currently highlighted
		self._highlight_index = -1
		# these 3 variables are the 3 callbacks that the controller can input
		self._on_build = None
		self._on_enter = None
		self._on_text = None
		# this field holds a preset number of buttons for efficiency
		self._button_pool = []
		# parse the callbacks passed in the constructor
		self.user_bind(**kwargs)
		# update the window size
		self.update_window()

	def user_bind(self, **kwargs):
		''' this function saves the callbacks passed to this function into the 3 available holders '''
		# this event is triggered when the application is drawn for the first time
		self._on_build = kwargs.get('on_build', self._on_build)
		# this event is triggered when the user presses enter
		self._on_enter = kwargs.get('on_enter', self._on_enter)
		# this even is triggered whenever the text in the search field is changed
		self._on_text = kwargs.get('on_text', self._on_text)

	def on_start(self):
		'''  when the window is drawn and the application started we update the size of the window '''
		self.update_window()

	def build(self):
		''' this function builds the whole app '''
		self._search_field = SearchInput(multiline=False, focus=True, realdonly=False, height=self._search_field_height, size_hint=(1, None), markup=True,
			valign='middle', font_size = 20, font_name = 'data/fonts/DejaVuSans.ttf')
		self._search_field.bind(focus=self._on_focus)
		self._search_field._keyboard.bind(on_key_down=self._on_keyboard_down)
		self._search_field.background_active = ''
		self._search_field.font_size = 20
		self._search_field.bind(on_text_validate = self._on_text_validate)
		self._search_field.bind(text = self._on_new_text)
		self._search_field.text = ''
		self._drop_down_list = GridLayout(cols=1, width=self._width, spacing=self._result_spacing, size_hint = (None, None))
		self._drop_down_list.bind(minimum_height = self._drop_down_list.setter('height'))
		self._scroller = ScrollView(scroll_distance=10, scroll_type=['bars'], do_scroll_x=False, bar_width=10, size_hint=(1, 1))
		self._scroller.add_widget(self._drop_down_list)
		self._layout = ColoredGridLayout(cols=1, width=self._width, height=self._search_field_height, padding=(self._padding, self._padding), spacing=self._spacing*2)
		self._layout.add_widget(self._search_field)
		self._layout.add_widget(self._scroller)
		if self._on_build:
			self._on_build()
		return self._layout

	def _on_new_text(self, value, text):
		if self._on_text:
			self._on_text(self, value, text)

	def _on_text_validate(self, value):
		''' when the user pressed enter, we forward the callback to the controller with the current hightlight index '''
		if self._on_enter:
			self._on_enter(value, self._highlight_index)

	def _on_focus(self, instance, value):
		''' this function is called whenever the focus of the search field changes. We do NOT allow defocus '''
		if not value:
			self._search_field.focus = True
			# since the search field has to re-claim the keyboard, we re-bind our callback
			self._search_field._keyboard.bind(on_key_down=self._on_keyboard_down)

	def update_window(self, *args):
		''' based on the current amount of entries shown, we adapt the size of the window '''
		result_count = len(self._results)
		win_width = 2*self._padding + self._width
		win_height = 2*self._padding + self._search_field_height + self._spacing + (self._result_spacing * 2 + self._result_height + self._sep_height) * result_count
		max_height = 2*self._padding + self._search_field_height + self._spacing + (self._result_spacing * 2 + self._result_height + self._sep_height) * self._max_results_displayed
		if self._app_window:
			self._app_window.size = win_width, min(win_height, max_height)

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		''' we handle 3 keys: up (resp. down) to hightlight the entry above (resp. below) and escape to quit the application '''
		if keycode[1] == 'up':
			self._highlight_up()  
		elif keycode[1] == 'down':
			self._highlight_down()
		elif keycode[1] == 'escape':
			keyboard.release()
			exit(0)
		else:
			# mark the key press as not handled
			return False
		# mark the key press as handled
		return True

	def pre_allocate(self, number):
		self._button_pool = []
		for _ in range(0, number):
			btn = Button(text='str', height=self._result_height, size_hint=(1, None), valign='middle',
					halign='left', background_color=self._inactive_button_color, markup = True, padding_x = 0)
			btn.bind(width = lambda s, w: s.setter('text_size')(s, (w-20, None)))
			btn.bind(on_press=self._on_click)
			btn.bind(texture_size=btn.setter('text_size'))
			btn.background_normal = ''
			btn.background_down = btn.background_normal
			self._button_pool.append(btn)

	def _build_button(self):
		if self._button_pool:
			return self._button_pool.pop()
		btn = Button(text='str', height=self._result_height, size_hint=(1, None), valign='middle',
					halign='left', background_color=self._inactive_button_color, markup = True, padding_x = 0)
		btn.bind(width = lambda s, w: s.setter('text_size')(s, (w-20, None)))
		btn.bind(on_press=self._on_click)
		btn.bind(texture_size=btn.setter('text_size'))
		btn.background_normal = ''
		btn.background_down = btn.background_normal
		return btn

	def _release_button(self, btn):
		btn.background_color = self._inactive_button_color
		self._button_pool.append(btn)

	def add_result(self, str, redraw = True):
		''' add a new entry to the dropdown list; an index is returned '''
		btn = self._build_button()
		btn.text = str
		sep = Separator(height = self._sep_height)
		self._drop_down_list.add_widget(sep)
		self._drop_down_list.add_widget(btn)
		self._results.append((btn, sep))
		# we reset the highlight
		self._highlight_reset()
		if redraw:
			self.update_window()
		return len(self._results)-1

	def get_result(self, idx):
		''' get a button object from an index - returned from a previous call to add_result '''
		if not idx < len(self._results) or not idx >= 0:
			return
		e, _ = self._results[idx]
		return e

	def remove_result(self, idx, redraw = True):
		''' remove a result object from its index - returned from a previous call to add_result '''
		if not idx < len(self._results) or not idx >= 0:
			return
		e, sep = self._results[idx]
		if sep:
			self._drop_down_list.remove_widget(sep)
		self._drop_down_list.remove_widget(e)
		self._results.remove((e, sep))
		self._release_button(e)
		# we reset the highlight
		self._highlight_reset()
		# resize the window accordingly
		if redraw:
			self.update_window()

	def clear_results(self, redraw = True):
		''' clear all the results '''
		for e, sep in self._results:
			self._release_button(e)
		self._drop_down_list.clear_widgets()
		self._results = []
		# we reset the highlight
		self._highlight_reset()
		# resize the window accordingly
		if redraw:
			self.update_window()

	def _on_click(self, instance):
		''' this callback is called whenever a click on a result is done; the highlight is adapted '''
		for i in range(0, len(self._results)):
			e, _ = self._results[i]
			if e is instance:
				offset = i-self._highlight_index
				self._highlight_update(offset)
				break

	def _scroll_update(self):
		''' this function adapts the scroller to ensure that the highlighted object is visible '''
		highlight_reverse_index = len(self._results) - 1 - self._highlight_index
		item_lb = highlight_reverse_index * (self._result_spacing*2 + self._sep_height + self._result_height)
		item_ub = item_lb + self._result_height + self._result_spacing*2 + self._sep_height
		view_size = (self._result_spacing * 2 + self._result_height + self._sep_height) * self._max_results_displayed
		total_size = (self._result_spacing * 2 + self._result_height + self._sep_height) * len(self._results)
		lb = self._scroller.scroll_y * (total_size - view_size)
		ub = lb + view_size
		if item_lb < lb:
			self._scroller.scroll_y -= self._scroller.convert_distance_to_scroll(0, lb - item_lb)[1]
		elif item_ub > ub:
			self._scroller.scroll_y += self._scroller.convert_distance_to_scroll(0, item_ub - ub)[1]

	def _highlight_update(self, offset):
		''' move the hightlight by `offset' amount '''
		if self._highlight_index > -1 and self._highlight_index < len(self._results):
			e, sep = self._results[self._highlight_index]
			e.background_color = self._inactive_button_color
		self._highlight_index += offset
		self._highlight_index = min(self._highlight_index, len(self._results)-1)
		if self._results:
			self._highlight_index = max(self._highlight_index, 0)
		else:
			self._highlight_index = max(self._highlight_index, 1)
		if self._highlight_index > -1 and self._highlight_index < len(self._results):
			e, sep = self._results[self._highlight_index]
			e.background_color = self._active_button_color
			self._scroll_update()

	def _highlight_reset(self):
		offset = -self._highlight_index
		self._highlight_update(offset)

	def _highlight_up(self):
		self._highlight_update(-1)

	def _highlight_down(self):
		self._highlight_update(+1)

''' Main... '''
if __name__ == '__main__':
	from SpotlightController import SpotlightController
	spotlight = Spotlight()
	controller = SpotlightController(spotlight = spotlight)
	spotlight.run()