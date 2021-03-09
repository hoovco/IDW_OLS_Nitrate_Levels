import tkinter
from tkinter import *
import matplotlib
import matplotlib.pyplot as plt

#creating GUI interface
window = Tk()
window.title("Cancer and Nitrate Spatial Analysis")
menu = Menu(window)
new_item = Menu(menu)
new_item.add_command(label='Save As')
menu.add_cascade(label='File', menu = new_item)
window.config(menu=menu)
window.geometry('800x600')

frame1 = Frame(window, bg = 'white', borderwidth = 2)
frame1.pack()
frame1.grid(row=2, column=1)
frame2 = Frame(window, bg = 'white', borderwidth = 2)
frame2.grid(row=3, column=1)
frame3 = Frame(window, bg = 'white', borderwidth = 2)
frame3.grid(row=4, column=1)
frame4 = Frame(window, bg = 'white', borderwidth = 2)
frame4.grid(row=5, column=1)

L1 = Label(frame1, text="IDW k Value > 0: ")
L1.pack(side = LEFT)
L2 = Label(frame2, text="Smoothing Variable >= 0: ")
L2.pack(side = LEFT)
E1 = Entry(frame1, bd =5)
E1.pack(side = LEFT)
E2 = Entry(frame2, bd =5)
E2.pack(side=LEFT)
IDWButton = Button(frame3, text="GET THIS PARTY STARTED", bg = 'red', fg = 'white', relief = 'raised', borderwidth = 3)
IDWButton.pack(side=LEFT)
plot_button1 = Button(frame4, text = "Plot Mean Nitrate Values", bg = 'red', fg = 'white', relief = 'raised', borderwidth = 3)
plot_button2 = Button(frame4, text = "Plot Cancer Rate Values", bg = 'red', fg = 'white', relief = 'raised', borderwidth = 3)
plot_button3 = Button(frame4, text = "Plot OLS Error Values", bg = 'red', fg = 'white', relief = 'raised', borderwidth = 3)
plot_button1.pack(side=LEFT)
plot_button2.pack(side=LEFT)
plot_button3.pack(side=LEFT)
window.mainloop()

