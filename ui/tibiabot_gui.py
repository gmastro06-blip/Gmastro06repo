def __init__(self):
    self.root = tk.Tk()
    self.root.title("Tibiabot v2.1 PRO - Grok Edition")
    self.root.geometry("400x300")
    self.root.configure(bg='#2e2e2e')

    self.engine = None
    self.stop_event = threading.Event()

    # PRIMERO carga la config
    self.load_config()        # ← PRIMERO
    self.load_waypoints()     # ← DESPUÉS (ahora self.config ya existe)

    self.create_widgets()

    self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    self.root.mainloop()