from re import search, findall, DOTALL
from subprocess import run
from tempfile import NamedTemporaryFile
import pygame as pg
from smartfust.scripts.input_manager import InputManager, EXIT, KEYS, LEFTCLICK_DOWN, \
    MOUSE_POS, RIGHT, LEFT, UP, DOWN, DELETE
from smartfust.scripts.physics import mouse_in_rect



FPS = 30
SCREEN_DIMS = (600, 400)
ROUND_THRESHOLD = 5

def edit_and_read():
    # Crée un fichier temporaire
    with NamedTemporaryFile(mode='r+', suffix='.txt', delete=False) as tmp:
        filename = tmp.name

    # Lance Notepad sur ce fichier (bloquant jusqu'à la fermeture)
    run(["notepad", filename])

    # Après la fermeture de Notepad, on lit le contenu du fichier
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    return content

def get_dims_from_string(text):
    splitted = text.split(",")
    return tuple(int(i) for i in splitted)

def extract_outer_parentheses(text):
    start = text.find('(')
    if start == -1:
        return None

    count = 0
    for i in range(start, len(text)):
        if text[i] == '(':
            count += 1
        elif text[i] == ')':
            count -= 1
            if count == 0:
                return text[start + 1:i]  # sans les parenthèses

    return None  # si parenthèses non équilibrées


def dicstring_parser(dicstring):
    usable = search(r"\{(.*?)\}", dicstring, DOTALL)
    if not usable:
        return {}  # Aucun contenu trouvé entre accolades
    lines = usable.group(1).split("\n")

    dic = {}
    for line in lines:
        if ':' not in line:
            continue
        _id, widget = line.split(":", 1)
        widget = extract_outer_parentheses(widget)
        parentheses = findall(r"\((.*?)\)", widget)
        resultat = [get_dims_from_string(i) for i in parentheses[:2]]  # garder que les 2 premières
        dic[int(_id.strip())] = resultat
    return dic

def round_to_threshold(value, threshold=ROUND_THRESHOLD):
    return round(value / threshold) * threshold

def format_widgets(widget_dict: dict):
    tot_text = []
    for _id, widget in widget_dict.items():
        inner_text = f"    {_id}: sf.Widget({widget.pos}, {widget.dims}),"
        tot_text.append(inner_text)

    return "{\n" + "\n".join(tot_text) + "\n}"

class ConstantManager:
    def __init__(self):
        self.SD = SCREEN_DIMS

    @property
    def halfSD(self):
        return self.SD[0] // 2, self.SD[1] // 2

class Renderer:
    def __init__(self, cst_man):
        pg.font.init()
        self.SCREEN = pg.display.set_mode(cst_man.SD)
        pg.display.set_caption("Menu Creation")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 20)

    def display_on_screen(self, widgets, focused):
        self.SCREEN.fill((200, 200, 200))
        for widget in widgets.values():
            if widget == focused:
                pg.draw.rect(self.SCREEN, (150, 150, 150), widget.focus_rect)
            #bigger_rect = widget.bigger_rect
            #pg.draw.rect(self.SCREEN, (255, 0, 0), bigger_rect)
            pg.draw.rect(self.SCREEN, (100, 100, 100), widget.rect)

            # Get text
            text = self.font.render(widget.text, True, (0, 0, 0))
            relposx = (widget.width - text.get_width()) // 2
            relposy = (widget.height - text.get_height()) // 2
            self.SCREEN.blit(text, (widget.posx + relposx, widget.posy + relposy))

    def update(self):
        pg.display.flip()
        self.clock.tick(FPS)


class Widget:
    def __init__(self, pos=None, dims=None, midpos=None):
        self.width, self.height = dims if dims else (100, 30)
        if midpos:
            self.posx, self.posy = midpos
            self.posx -= self.hwidth
            self.posy -= self.hheight
        if pos:
            self.posx, self.posy = pos
        self.color = (100, 100, 100)

        self.bigger_pos_offset = (20, 20)

    def offcenter(self, mouse_pos):
        self.posx = mouse_pos[0] - self.hwidth
        self.posy = mouse_pos[1] - self.hheight

    def xcenter(self, hSD):
        self.posx = hSD[0] - (self.width // 2)

    def ycenter(self, hSD):
        self.posy = hSD[1] - (self.height // 2)

    def w_extend(self, value):
        self.width += value
        if self.width < 0:
            self.width = 0
            return
        self.posx -= value // 2

    def h_extend(self, value):
        self.height += value
        if self.height < 0:
            self.height = 0
            return
        self.posy -= value // 2

    def round_coords(self):
        self.posx = round_to_threshold(self.posx)
        self.posy = round_to_threshold(self.posy)

    @property
    def text(self):
        return f"{self.posx} {self.posy} {self.width} {self.height}"

    @property
    def rect(self):
        return self.posx, self.posy, self.width, self.height

    @property
    def bigger_rect(self):
        return self.posx - self.bigger_pos_offset[0], \
            self.posy - self.bigger_pos_offset[1], \
            self.width + self.bigger_pos_offset[0] * 2, \
            self.height + self.bigger_pos_offset[1] * 2

    @property
    def focus_rect(self):
        d = 5
        return self.posx - d, \
            self.posy - d, \
            self.width + 2*d, \
            self.height + 2*d

    @property
    def hwidth(self):
        return self.width // 2

    @property
    def hheight(self):
        return self.height // 2

    @property
    def pos(self):
        return self.posx, self.posy

    @property
    def dims(self):
        return self.width, self.height

class FocusManager:
    def __init__(self, cst_man):
        self.focused_widget = None
        self.widgets = {}
        self.cst_man: ConstantManager = cst_man

    def load_dic(self):
        print("Paste the dictionary and remove all \':\' which are not a main id: widget separator")
        texte = edit_and_read()
        parsed = dicstring_parser(texte)
        self.widgets = {}
        for key, caracs in parsed.items():
            self.widgets[key] = Widget(pos=caracs[0], dims=caracs[1])


    def delete_focus(self):
        if not self.focused_widget:
            return
        # get key of widget
        for key, item in self.widgets.items():
            if item == self.focused_widget:
                del self.widgets[key]
                return

    def add_widget(self):
        max_key = max(self.widgets.keys(), default=-1)
        self.widgets[max_key + 1] = Widget(midpos=self.cst_man.halfSD)

    def grab_widget(self, mouse_pos):
        self.focused_widget = None
        for widget in self.widgets.values():
            if mouse_in_rect(mouse_pos, widget.bigger_rect):
                self.focused_widget = widget


def main():
    cst_man = ConstantManager()
    renderer = Renderer(cst_man)
    focus_man = FocusManager(cst_man)
    input_manager = InputManager()
    running = True

    while running:
        input = input_manager.get_events()
        if EXIT in input:
            running = False


        pressed_key = input.get(KEYS, None)
        last_pressed_key = input_manager.last_events.get(KEYS, None)
        if pressed_key == "n" and last_pressed_key != "n":
            focus_man.add_widget()
        if pressed_key == "p" and last_pressed_key != "p":
            print(format_widgets(focus_man.widgets))
        if pressed_key == "l" and last_pressed_key != "l":
            focus_man.load_dic()
        if LEFTCLICK_DOWN in input:
            # Get mouse position
            mouse_pos = input[MOUSE_POS]
            focus_man.grab_widget(mouse_pos)
            if focus_man.focused_widget:
                focus_man.focused_widget.offcenter(input[MOUSE_POS])

        if focus_man.focused_widget:
            if pressed_key == "x":
                focus_man.focused_widget.xcenter(cst_man.halfSD)
            if pressed_key == "y":
                focus_man.focused_widget.ycenter(cst_man.halfSD)
            if pressed_key == "r":
                focus_man.focused_widget.round_coords()
            if RIGHT in input:
                focus_man.focused_widget.w_extend(ROUND_THRESHOLD)
            if LEFT in input:
                focus_man.focused_widget.w_extend(-ROUND_THRESHOLD)
            if UP in input and focus_man.focused_widget:
                focus_man.focused_widget.h_extend(ROUND_THRESHOLD)
            if DOWN in input and focus_man.focused_widget:
                focus_man.focused_widget.h_extend(-ROUND_THRESHOLD)
            if DELETE in input:
                focus_man.delete_focus()

        input_manager.set_last_events()

        renderer.display_on_screen(focus_man.widgets, focus_man.focused_widget)
        renderer.update()





if __name__ == "__main__":
    main()
