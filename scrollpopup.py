from kivy.app import App
from kivy.lang import Builder
kv = '''
RecycleView:
    data: [{"text": "Label "+str(x)} for x in range(50)]
    viewclass: 'Button'
    do_scroll_y: True
    RecycleGridLayout:
        cols: 5
        #default_size: None, 200
        #default_size_hint: 1, None
        default_size: None, None
        default_size_hint: 1, None
        size_hint: None, None
        height: 800
        width: 2000
'''
class MyApp(App):
    def build(self):
        return Builder.load_string(kv)
MyApp().run()