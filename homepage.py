from tkinter import *
from tkinter import messagebox  
import tkinter
from PIL import ImageTk, Image


main = tkinter.Tk()
main.title("2584 fibonacii game")
main.geometry("1000x1000")


font = ('times', 15, 'bold')
title = Label(main, text='2584 FIBONACCI GAME', justify=CENTER)
title.config(bg='lavender blush', fg='DarkOrchid1')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=10,y=5)
title.pack()
image = Image.open("instructions.jpg")





def Page():
    main.destroy()
    import maincode.py
    
def help1():
    #messagebox.showinfo("Help","For instructions Click `OK` ")
    #import info.py
    
    #image = Image.open("instructions.jpg")
    
    l = Label(main, text = "")
    l.config(font =("Times", 14,),bg = "light blue")
    l.pack()
    l = Label(main, text = "")
    l.config(font =("Times", 14,),bg = "light blue")
    l.pack()
    l = Label(main, text = "")
    l.config(font =("Times", 14,),bg = "light blue")
    l.pack()
    resize_image = image.resize((500, 500))
    img = ImageTk.PhotoImage(resize_image)
    label1 = Label(image=img)
    label1.image = img
    label1.pack()
    
     



def nextPage():
    t= messagebox.askyesno("Application","EXIT?") 
    if(t== True):
        main.destroy()
    #import maincode.py

#font1 = ('times', 12, 'bold')
'''Start = Button(main, text="Start", image =photo,height=50,width=100,command= Page)
Start.place(x=100,y=800)'''

start = Button(main, text="START ",command= Page)
start.place(x=200,y=100)
start.config(font=font) 

"""user = Button(main, text="USER", image = photo1,height=550,width=650,command= Page)
user.place(x=800,y=100)"""
help = Button(main, text="HELP ",command= help1)
help.place(x=300,y=100)
help.config(font=font) 

exit = Button(main, text="EXIT ",command= nextPage)
exit.place(x=400,y=100)
exit.config(font=font) 







main.config(bg='light blue')
main.mainloop()