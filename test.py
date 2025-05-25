import smartfust as sf


texture1 = sf.load_texture(r"C:\Users\Eleve\Pictures\Screenshots\Capture d’écran (4562).png", smoothscale=0.1)

dic = {
    0: sf.Label((100, 50), (60, 30), "Label", (0, 0, 0), colors=[(0, 255, 255), (255, 255, 0)], text_height=15),
    1: sf.Button((100, 100), (100, 100), "Button QUIT", None, (255, 255, 255), colors=[(0, 0, 0), (255, 0, 0)], animation={"size": (2, 2), "color": 6, "duration": 10}, text_height=13),
    2: sf.Checkbox((100, 220), (50, 50), colors=[(0, 150, 150), (150, 150, 0)], borders=[3]),
    3: sf.Entry((100, 300), (200, 30), inner_text="click here to change"),
    4: sf.TextureWidget((250, 100), (250, 150), texture1, colors=[(255, 0, 0)]),
    5: sf.Slider((400, 300), (100, 30)),
    6: sf.List((400, 100), (100, 30))
}
display = sf.Display(dims=(600, 400), title="Hello")
display.add_widgets(dic)
display.set_bg("custom", array=[[(0 + i)%3, (1 + i)%3, (2+i)%3] * 10 for i in range(30)], colors=((255, 0, 0), (0, 255, 0), (0, 0, 255)), shadow={"sign": (-10, 10),"mult": 3})
display.mainloop()

outputs = display.get_output()
for id, value in outputs.items():
    print(id, value)