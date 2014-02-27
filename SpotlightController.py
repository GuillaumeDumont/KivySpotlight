import os, sys, json, operator, subprocess
from Spotlight import Spotlight
import FuzzySearch
from kivy.logger import Logger

class Item:
	def __init__(self, **kwargs):
		self.name = kwargs.get('name', 'unknown')
		self.cmd = kwargs.get('cmd', '')
		self.index = -1

	def __str__(self):
		return '{ name=[' + self.name + '], cmd=[' + self.cmd + '] }'

	@staticmethod
	def reset(item):
		item.index = -1

class SpotlightController:
	def __init__(self, **kwargs):
		self._spotlight = kwargs.get('spotlight', None)
		self._source_file = kwargs.get('source_file', 'actions.json')
		if not self._spotlight:
			raise Exception('No spotlight provided')
		if not os.path.exists(self._source_file):
			raise Exception('The source file provided doesn\'t exist')
		self.update()
		self._spotlight.user_bind(on_build = self.build)
		self._spotlight.user_bind(on_text = self.on_text)
		self._spotlight.user_bind(on_enter = self.on_enter)

	def update(self):
		self._items = []
		with open(self._source_file, 'r') as f:
			content = f.read()
			root = json.loads(content)
			for item in root['items']:
				if '[name]' in item and '[cmd]' in item:
					name = item['[name]']
					cmd = item['[cmd]']
					i = Item(name=name, cmd=cmd)
					self._items.append(i)
			self._items.sort(key=(lambda item : item.name[0]))
			self._spotlight.pre_allocate(len(self._items))

	def build(self):
		self._display_list = []
		for item in self._items:
			if item.index > -1:
				continue
			item.index = self._spotlight.add_result('[color=dddddd]' + item.name + '[/color]')
			self._display_list.append(item)

	def decorate(self, sentence, solution):
		result = ''
		for i, c in enumerate(sentence):
			result += '[color=dddddd]' + c + '[/color]' if not i in solution else '[color=ffffff][b]' + c + '[/b][/color]'
		return result

	def on_text(self, instance, value, text):
		text = text.strip()
		text = text.translate(None, ' \t\n\r')
		self._spotlight.clear_results(False)
		map(Item.reset, self._items)
		if not text:			
			self.build()
			return
		search_list = []
		for item in self._items:
			(score, solution) = FuzzySearch.tag(text, item.name)
			if score > 0:
				search_list.append((score, solution, item))
		search_list.sort(key=operator.itemgetter(0), reverse=True)
		self._display_list = []
		for _, solution, item in search_list:
			item.index = self._spotlight.add_result(self.decorate(item.name, solution), False)
			self._display_list.append(item)
		self._spotlight.update_window()

	def on_enter(self, instance, index):
		if not self._display_list:
			exit(0)
		item = self._display_list[index]
		self._start_cmd(item)
		exit(0)
		
	def _start_cmd(self, item):
		subprocess.Popen([item.cmd], close_fds=True, shell=True)

	def __str__(self):
		res = ''
		for item in self._items:
			res += str(item) + '\n'
		return res
