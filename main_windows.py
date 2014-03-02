from Spotlight import Spotlight
from SpotlightController import SpotlightController
from pyHook import HookManager
from pyHook.HookManager import HookConstants
from pythoncom import PumpMessages, PumpWaitingMessages

def is_shortcut(keys, combination):
	for key in combination:
		if not key in keys:
			return False
	return True

''' Main... '''
if __name__ == '__main__':

	global spotlight, hook_manager

	from SpotlightController import SpotlightController
	hook_manager = HookManager()
	spotlight = None
	controller = None

	keys_pressed = []
	trigger = ['Lcontrol', '1']
	quit = ['Lcontrol', 'Q']

	def OnKeyDown(event):
		global keys_pressed, spotlight, controller
		if not event.GetKey() in keys_pressed:
			keys_pressed.append(event.GetKey())
		
		if is_shortcut(keys_pressed, quit):
			exit(0)

		if is_shortcut(keys_pressed, trigger):
			spotlight = Spotlight()
			controller = SpotlightController(spotlight = spotlight)
			keys_pressed = []
			return False
		return True

	def OnKeyUp(event):
		global keys_pressed
		if event.GetKey() in keys_pressed:
			keys_pressed.remove(event.GetKey())
		return True

	hook_manager.KeyDown = OnKeyDown
	hook_manager.KeyUp = OnKeyUp
	hook_manager.HookKeyboard()


	while True:
		if spotlight:
			hook_manager.UnhookKeyboard()
			spotlight.run()
			spotlight = None
			controller = None
			hook_manager.HookKeyboard()
		else:
			PumpWaitingMessages()