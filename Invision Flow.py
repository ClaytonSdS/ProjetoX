from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics','position','custom')

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty
from kivy.utils import get_color_from_hex
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivymd.uix.behaviors import HoverBehavior
from kivy.uix.behaviors import DragBehavior
from kivy.factory import Factory
Factory.register('HoverBehavior', HoverBehavior)
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivymd.app import MDApp
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.logger import Logger
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
import pandas as pd
import numpy as np

# CLASSES PARA AREA DE TRABALHO
class worksheet():
	def __init__(self, size_x, size_y):
		self.size_x = size_x
		self.size_y = size_y

		self.grid_generator()
		self.elements_grid()

	# FIND CLUSTERS AND NAME IT
	def cluster_finder(self, grid):
		grid_w_elements = pd.DataFrame(grid)
		element_count = 1
		for row in range(grid.shape[0]):
			for col in range(grid.shape[1]):
				try:
					if str(int(grid[row][col + 1])).isnumeric() == True and str(
							int(grid[row][col - 1])).isnumeric() == True and str(
							int(grid[row + 1][col])).isnumeric() == True and str(
							int(grid[row - 1][col])).isnumeric() == True and (row % 2) != 0:
						grid_w_elements.loc[row, col] = f"E{element_count}"
						element_count += 1

				except ValueError:
					pass
				except IndexError:
					pass
		return grid_w_elements

	# GENERATE MY GRID ARRAY WITH NODES
	def grid_generator(self):
		node_grid_space = np.empty((2 * self.size_x + 1, 2 * self.size_y + 1))
		node_grid_space[:] = np.NaN
		count = 0
		for row in range(node_grid_space.shape[0]):
			if (row % 2) == 0:
				for col in range(0, len(node_grid_space[row]) - 1, 2):
					count += 1
					node_grid_space[row][col + 1] = int(count)
			else:
				for col in range(0, len(node_grid_space[row]), 2):
					count += 1
					node_grid_space[row][col] = int(count)

		self.grid = self.cluster_finder(node_grid_space)

	# GENERATE AND ARRAY LIKE WITH MY ELEMENTS AND THEM RESPECTIVELY POSITION IN MY GRID ARRAY
	def elements_grid(self):
		self.e_grid = self.grid[[x for x in self.grid.columns if x % 2 != 0]].loc[
			[y for y in self.grid.columns if y % 2 != 0]].values
class element():
	def __init__(self, code, grid, e_grid, prop_data, type_element=None):
		self.initial_start = True
		self.code = code
		self.prop_data = prop_data
		self.type_element = type_element
		self.grid = grid
		self.e_grid = e_grid
		self.angle_rotation = 0
		self.nodes_recognizer()
		self.default_positions = {"top": [self.node_top], "bottom": [self.node_bottom], "left": [self.node_left],
								  "right": [self.node_right]}
		self.positions = {0: {"top": [], "bottom": [], "left": [], "right": []},  #
						  90: {"top": [], "bottom": [], "left": [], "right": []},  #
						  180: {"top": [], "bottom": [], "left": [], "right": []},  #
						  270: {"top": [], "bottom": [], "left": [], "right": []}}
		self.generate_rotations(4)
		self.set_default_nodes(self.prop_data)

	# FIND MY POSITION BASED ON THE CODE AND RETURN MY X,Y COORDINATES IN THE GRID GENERATOR
	def index_finder(self, grid, search):
		for col in grid.columns:
			if len(grid.loc[grid[col] == str(search)].index) > 0:
				row = grid.loc[grid[col] == str(search)].index.values[0]
				return [row, col]

			# FIND NODES NEXT TO MY ELEMENT CODE (RIGHT, LEFT, TOP, BOTTOM OF IT)

	def nodes_recognizer(self):
		self.pos = self.index_finder(grid=self.grid, search=str(self.code))
		self.node_top = self.grid.loc[self.pos[0] - 1, self.pos[1]]
		self.node_bottom = self.grid.loc[self.pos[0] + 1, self.pos[1]]
		self.node_right = self.grid.loc[self.pos[0], self.pos[1] + 1]
		self.node_left = self.grid.loc[self.pos[0], self.pos[1] - 1]

	# GENERATE ALL MY NODES POSITION COMBINATIONS IN FUNCTION OF MY ROTATION
	def generate_rotations(self, iterations):
		for i in range(iterations):
			self.angle_rotation += 90
			if self.angle_rotation >= 360:
				self.angle_rotation = 0
			old_top = self.node_top
			old_bottom = self.node_bottom
			old_left = self.node_left
			self.node_top = self.node_right
			self.node_left = old_top
			self.node_bottom = old_left
			self.node_right = old_bottom

			if self.node_top not in self.positions[self.angle_rotation]["top"]:
				self.positions[self.angle_rotation]["top"].append(self.node_top)

			if self.node_bottom not in self.positions[self.angle_rotation]["bottom"]:
				self.positions[self.angle_rotation]["bottom"].append(self.node_bottom)

			if self.node_right not in self.positions[self.angle_rotation]["right"]:
				self.positions[self.angle_rotation]["right"].append(self.node_right)

			if self.node_left not in self.positions[self.angle_rotation]["left"]:
				self.positions[self.angle_rotation]["left"].append(self.node_left)

	# SET MY IMPORTANT NODE SUCH AS NODES OF CONVERGENCE/ DIVERGENCE OF FLUX, ETC
	def set_default_nodes(self, database):

		# SIMMETRIC MERGING
		if self.type_element == "TEE-SYMMETRICAL-MERGING":
			self.node_to1 = self.fix_node_pos(self.default_positions["bottom"][0])
			self.node_from1 = self.fix_node_pos(self.default_positions["left"][0])
			self.node_from2 = self.fix_node_pos(self.default_positions["right"][0])

			UNIQUE_CODE_link_1 = "-".join(
				[str(self.code), str(self.type_element), str(int(self.default_positions["left"][0])),
				 str(int(self.default_positions["bottom"][0]))])
			UNIQUE_CODE_link_2 = "-".join(
				[str(self.code), str(self.type_element), str(int(self.default_positions["right"][0])),
				 str(int(self.default_positions["bottom"][0]))])

			database.add_element(element=self.code, type_=self.type_element, from_=int(self.node_from1),
								 to_=int(self.node_to1), UC=UNIQUE_CODE_link_1)
			database.add_element(element=self.code, type_=self.type_element, from_=int(self.node_from2),
								 to_=int(self.node_to1), UC=UNIQUE_CODE_link_2)

			if self.initial_start == False:
				database.change_node(UNIQUE_CODE_link_1, self.node_from1, self.node_to1)
				database.change_node(UNIQUE_CODE_link_2, self.node_from2, self.node_to1)

			# NON SIMMETRIC MERGING
		if self.type_element == "TEE-NONSYMMETRICAL-MERGING":
			self.node_to1 = self.fix_node_pos(self.default_positions["right"][0])
			self.node_from1 = self.fix_node_pos(self.default_positions["left"][0])  # TRECHO RETO
			self.node_from2 = self.fix_node_pos(self.default_positions["bottom"][0])  # TRECHO LATERAL

			UNIQUE_CODE_link_1 = "-".join(
				[str(self.code), str(self.type_element), str(int(self.default_positions["left"][0])),
				 str(int(self.default_positions["right"][0]))])
			UNIQUE_CODE_link_2 = "-".join(
				[str(self.code), str(self.type_element), str(int(self.default_positions["bottom"][0])),
				 str(int(self.default_positions["right"][0]))])

			database.add_element(element=self.code, type_=self.type_element, from_=int(self.node_from1),
								 to_=int(self.node_to1), UC=UNIQUE_CODE_link_1)
			database.add_element(element=self.code, type_=self.type_element, from_=int(self.node_from2),
								 to_=int(self.node_to1), UC=UNIQUE_CODE_link_2)

			if self.initial_start == False:
				database.change_node(UNIQUE_CODE_link_1, self.node_from1, self.node_to1)
				database.change_node(UNIQUE_CODE_link_2, self.node_from2, self.node_to1)

			# SIMMETRIC DIVIDING
		if self.type_element == "TEE-SYMMETRICAL-DIVIDING":
			self.node_from1 = self.fix_node_pos(self.default_positions["bottom"][0])
			self.node_to1 = self.fix_node_pos(self.default_positions["left"][0])
			self.node_to2 = self.fix_node_pos(self.default_positions["right"][0])

			UNIQUE_CODE_link_1 = "-".join(
				[str(self.code), str(self.type_element), str(int(self.default_positions["bottom"][0])),
				 str(int(self.default_positions["left"][0]))])
			UNIQUE_CODE_link_2 = "-".join(
				[str(self.code), str(self.type_element), str(int(self.default_positions["bottom"][0])),
				 str(int(self.default_positions["right"][0]))])

			database.add_element(element=self.code, type_=self.type_element, from_=int(self.node_from1),
								 to_=int(self.node_to1), UC=UNIQUE_CODE_link_1)
			database.add_element(element=self.code, type_=self.type_element, from_=int(self.node_from1),
								 to_=int(self.node_to2), UC=UNIQUE_CODE_link_2)

			if self.initial_start == False:
				database.change_node(UNIQUE_CODE_link_1, self.node_from1, self.node_to1)
				database.change_node(UNIQUE_CODE_link_2, self.node_from1, self.node_to2)

			# NON SIMMETRIC DIVIDING
		if self.type_element == "TEE-NONSYMMETRICAL-DIVIDING":
			self.node_from1 = self.fix_node_pos(self.default_positions["left"][0])
			self.node_to1 = self.fix_node_pos(self.default_positions["right"][0])  # trecho reto
			self.node_to2 = self.fix_node_pos(self.default_positions["bottom"][0])  # trecho lateral

			UNIQUE_CODE_link_1 = "-".join(
				[str(self.code), str(self.type_element), str(int(self.default_positions["left"][0])),
				 str(int(self.default_positions["right"][0]))])
			UNIQUE_CODE_link_2 = "-".join(
				[str(self.code), str(self.type_element), str(int(self.default_positions["left"][0])),
				 str(int(self.default_positions["bottom"][0]))])

			database.add_element(element=self.code, type_=self.type_element, from_=int(self.node_from1),
								 to_=int(self.node_to1), UC=UNIQUE_CODE_link_1)
			database.add_element(element=self.code, type_=self.type_element, from_=int(self.node_from1),
								 to_=int(self.node_to2), UC=UNIQUE_CODE_link_2)

			if self.initial_start == False:
				database.change_node(UNIQUE_CODE_link_1, self.node_from1, self.node_to1)
				database.change_node(UNIQUE_CODE_link_2, self.node_from1, self.node_to2)

			# FUNCTION TO ROTATE MY ELEMENT AND MY IMAGE

	def rotate(self):
		self.angle_rotation += 90
		if self.angle_rotation >= 360:
			self.angle_rotation = 0

		self.initial_start = False
		self.set_default_nodes(database=self.prop_data)

	# FIX MY DEFAULT NODES POSITION IN FUNCTION OF MY ROTATION ANGLE
	def fix_node_pos(self, node):
		for index in range(4):
			key = list(self.positions[self.angle_rotation].keys())[index]
			if self.positions[self.angle_rotation][key][0] == node:
				return self.default_positions[key][0]
class properties():
  def __init__(self):
    self.database = pd.DataFrame(data={"element":[], "type":[], "UC":[], "from":[], "to": []})

  def add_element(self, element=1, type_=1, UC=1, from_=1, to_=1):
    if len(self.database["UC"].loc[self.database["UC"]==UC]) == 0:
      new_row = [element, type_, UC, int(from_), int(to_)]
      self.database = self.database.append(pd.Series(new_row, index=self.database.columns), ignore_index=True)

  def change_node (self, unique_code, new_from, new_to):
    index = self.database.loc[self.database["UC"] == unique_code][["from", "to"]].index[0]
    self.database.loc[index,"from"] = int(new_from)
    self.database.loc[index,"to"] = int(new_to)

class Interface (MDGridLayout):
	pass

class Propriedades (MDGridLayout):
	pass

class Simulacao (MDGridLayout):
	pass

class Gerais (MDGridLayout):
	pass

class TittleBar_Button(ButtonBehavior, HoverBehavior, MDFloatLayout):
	cor = StringProperty("494a4c")

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.name = None
		self.icon = None
		self.md_bg_color = get_color_from_hex("#{}".format(self.cor))

		Clock.schedule_interval(self.set_icon_and_name, 1)

	def animate_enter(self, widget, *args):
		animate = Animation(md_bg_color=get_color_from_hex("#585a5c"), duration=0.25)
		animate.start(widget)

	def animate_leave(self, widget, *args):
		animate = Animation(md_bg_color=get_color_from_hex("#494a4c"), duration=0.25)
		animate.start(widget)

	def animate_press(self, widget, *args):
		animate = Animation(md_bg_color=get_color_from_hex("#252525"), duration=0.02)
		animate.start(widget)

	def animate_release(self, widget, *args):
		animate = Animation(md_bg_color=get_color_from_hex("#494a4c"), duration=0.1)
		animate.start(widget)
		self.cor = 'eeeeee'

	def set_icon_and_name (self, dt):
		if self.icon != None:
			self.ids.icon_tittlebar.source = f"icons\\{self.icon}.png"

		if self.name != None:
			self.ids.icon_name.text = self.name

	def on_enter(self):
		self.animate_enter(self)

	def on_leave(self):
		self.animate_leave(self)

	def on_press(self):
		self.animate_press(self)


	def on_release(self):
		self.animate_leave(self)



class Button_Referencia (HoverBehavior, ButtonBehavior, MDBoxLayout, DragBehavior):
	cor = StringProperty("494a4c")
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.md_bg_color = get_color_from_hex("#{}".format(self.cor))

	def animate_enter(self, widget, *args):
		animate = Animation(md_bg_color=get_color_from_hex("#585a5c"), duration=0.25)
		animate.start(widget)

	def animate_leave(self, widget, *args):
		animate = Animation(md_bg_color=get_color_from_hex("#494a4c"), duration=0.25)
		animate.start(widget)

	def animate_press(self, widget, *args):
		animate = Animation(md_bg_color=get_color_from_hex("#252525"), duration=0.02)
		animate.start(widget)

	def animate_release(self, widget, *args):
		animate = Animation(md_bg_color=get_color_from_hex("#494a4c"), duration=0.1)
		animate.start(widget)
		self.cor = 'eeeeee'

	def on_enter(self):
		self.animate_enter(self)

	def on_leave(self):
		self.animate_leave(self)

	def on_press(self):
		self.animate_press(self)



	def on_release(self):
		def delay(dt):
			self.animate_release(self)
			self.animate_release(self.parent)
		Clock.schedule_once(delay, 0.2)


class Inicio(Screen):
	pass


from kivy.uix.recycleview import RecycleView

class WorkSpace(Screen):
	recycle_view = ObjectProperty(None)
	items_box = ObjectProperty(None)
	from kivy.uix.recycleview.views import RecycleDataAdapter

	class Teste(BoxLayout):
		def t(self):
			a = Button(text = "aaaa")
			#self.ids.box_work.add_widget(a)

	def increase(self):
		self.recycle_view.width += 100

	def on_enter(self):
		self.work = worksheet(3, 3)
		self.properties = properties()
		self.element1 = element(code="E1", type_element="TEE-NONSYMMETRICAL-MERGING",
								grid=self.work.grid, e_grid=self.work.e_grid, prop_data=self.properties)
		#self.work.e_grid
		self.Teste.t(self)
		colunas = len(self.work.e_grid[0])

		print()

		if len(self.ids.recycle_view.data) == 0:
			for i in range(1,10):
				ids = str(i)
				self.ids.recycle_view.data.append({'id_': ids})




class WindowManager(ScreenManager):
	pass

class InvisionFlow(MDApp):


	def on_start(self):
		import pickle
		#self.a = 33
		#pickle.dump(self.a, open("teste.ifp", "wb"))

		self.b = pickle.load((open("teste.ifp", "rb")))

		def refresh_name(dt):
			if Window.size[0] < 800 :
				Window.size = (800,Window.size[1])
			if Window.size[1] < 600:
				Window.size = (Window.size[0],600)
		Clock.schedule_interval(refresh_name, 0.05)

	def build(self):
		#Window.custom_titlebar = True
		self.title = 'Invision Flow'
		self.icon = 'icon.png'

		#WorkSpace.ids.add_widget(title_bar)

	#Window.borderless = True
	#Window.maximize()

	Window.top = 50
	Window.left = 50

if __name__ == '__main__':
	InvisionFlow().run()


