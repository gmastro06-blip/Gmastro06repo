import tkinter as tk

root = tk.Tk()
root.title("Prueba Tkinter")
root.geometry("400x300")
label = tk.Label(root, text="¡Si ves esta ventana, Tkinter funciona correctamente!", font=("Arial", 16))
label.pack(expand=True)
root.mainloop()