import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
import heapq

# Graph Class (Dijkstra)
class Graph:
    def __init__(self):
        self.adj = {}  # adjacency list
        self.node_positions = {}  # positions for visualization

    def add_hospital(self, name, x=None, y=None):
        if name not in self.adj:
            self.adj[name] = {}
        if x is not None and y is not None:
            self.node_positions[name] = (x, y)
        elif name not in self.node_positions:
            idx = len(self.node_positions) + 1
            # Simple position generation if not provided
            self.node_positions[name] = (60 + (idx * 120) % 900, 60 + (idx * 80) % 500)

    def add_road(self, a, b, distance):
        self.add_hospital(a)
        self.add_hospital(b)
        self.adj[a][b] = distance
        self.adj[b][a] = distance

    def dijkstra(self, start):
        if start not in self.adj:
            return {}, {}
        dist = {n: float('inf') for n in self.adj}
        prev = {n: None for n in self.adj}
        dist[start] = 0
        heap = [(0, start)]
        while heap:
            d, node = heapq.heappop(heap)
            if d > dist.get(node, float('inf')):
                continue
            for nb, w in self.adj.get(node, {}).items():
                nd = d + w
                if nd < dist.get(nb, float('inf')):
                    dist[nb] = nd
                    prev[nb] = node
                    heapq.heappush(heap, (nd, nb))
        return dist, prev

    def reconstruct_route(self, prev, target):
        if target not in prev:
            return []
        route = []
        node = target
        while node is not None:
            route.insert(0, node)
            node = prev[node]
        return route

# Appointment Manager
class AppointmentManager:
    def __init__(self):
        self.heap = []
        self.counter = 0

    def book(self, name, priority, details=""):
        self.counter += 1
        heapq.heappush(self.heap, (priority, self.counter, name, details))

    def pop_next(self):
        if not self.heap:
            return None
        p, _, name, details = heapq.heappop(self.heap)
        return (p, name, details)

    def peek_all(self):
        return sorted(self.heap)

# GUI Application
class SmartMedicalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Medical System")
        self.geometry("1250x760")
        self.minsize(980, 620)

       
        self.bg_color = "#1E1A3A"        
        self.panel_bg = "#2A2550"        
        self.card_bg = "#2A2550"         
        self.button_bg = "#6E44FF"       
        self.highlight = "#C9B6FF"       
        self.text_primary = "#C9B6FF"    
        self.subtle = "#8E88B9"          
        self.warn = "#FF3864"            
        self.success = "#32E0C4"         
        self.entry_bg = "#EBE3FF"        

        self.configure(bg=self.bg_color)

        # Data
        self.graph = Graph()
        self.app_mgr = AppointmentManager()
        self._populate_data()

        # Added for shortest path storage
        self.last_shortest_hospital = None 

        # Fonts
        self.header_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.label_font = tkfont.Font(family="Arial", size=10)
        self.button_font = tkfont.Font(family="Arial", size=10, weight="bold")
        self.text_font = tkfont.Font(family="Consolas", size=10)

        # Pages Container
        container = tk.Frame(self, bg=self.bg_color)
        container.pack(fill="both", expand=True)

        self.pages = {}
        # Instantiate all pages: StartPage -> EmergencyRoutingPage -> AppointmentsPage
        for P in (StartPage, EmergencyRoutingPage, AppointmentsPage):
            page = P(container, self)
            self.pages[P.__name__] = page
            page.place(relwidth=1, relheight=1)

        # Start the application on the StartPage
        self.show_page("StartPage")

    def show_page(self, name):
        page = self.pages[name]
        page.lift()
        if name == "EmergencyRoutingPage":
            page.draw_map()
        elif name == "AppointmentsPage":
            page.update_queue_display()
            # If coming from routing, pre-fill the hospital field
            if self.last_shortest_hospital:
                page.hospital_var.set(self.last_shortest_hospital)
            else:
                # If no routing was done, default to the first hospital
                page.hospital_var.set(list(self.graph.adj.keys())[0])
                def show_page(self, page_name):
                    page = self.pages[page_name]
                    page.tkraise()

                    # When opening the AppointmentsPage, auto-refresh queue
                    if page_name == "AppointmentsPage":
                        page.update_queue_display()


    def _populate_data(self):
        # Hospitals
        self.graph.add_hospital("Agha Khan", 360, 140)
        self.graph.add_hospital("Jinnah Hospital", 560, 220)
        self.graph.add_hospital("Saifee Hospital", 180, 80)
        self.graph.add_hospital("Civil Hospital", 600, 420)
        self.graph.add_hospital("Ziauddin Hospital", 820, 140)
        self.graph.add_hospital("Indus Hospital", 80, 320)
        

        # Roads (km)
        self.graph.add_road("Agha Khan", "Jinnah Hospital", 15)
        self.graph.add_road("Agha Khan", "Saifee Hospital", 25)
        self.graph.add_road("Jinnah Hospital", "Civil Hospital", 10)
        self.graph.add_road("Saifee Hospital", "Civil Hospital", 35)
        self.graph.add_road("Agha Khan", "Ziauddin Hospital", 20)
        self.graph.add_road("Jinnah Hospital", "Ziauddin Hospital", 30)
        self.graph.add_road("Indus Hospital", "Agha Khan", 18)
        
        self.app_mgrs = {h: AppointmentManager() for h in self.graph.adj.keys()}

        # Appointments
        # Agha Khan Hospital
        self.app_mgrs["Agha Khan"].book("Sarah Feroz", 3, "Annual Checkup")
        self.app_mgrs["Agha Khan"].book("Hamza Ali", 2, "High Fever")
        self.app_mgrs["Agha Khan"].book("Mahira Usman", 1, "Severe Bleeding")
        self.app_mgrs["Agha Khan"].book("Rimsha Khalid", 2, "Severe Headache")
        self.app_mgrs["Agha Khan"].book("Usman Tariq", 1, "Accidental Injury")
        self.app_mgrs["Agha Khan"].book("Laiba Ahmed", 3, "Diabetes Follow-up")
        self.app_mgrs["Agha Khan"].book("Irfan Siddiqui", 2, "Abdominal Pain")

        # Jinnah Hospital
        self.app_mgrs["Jinnah Hospital"].book("Nawera Khan", 1, "Severe Chest Pain")
        self.app_mgrs["Jinnah Hospital"].book("Daniyal Ahmed", 2, "Migraine")
        self.app_mgrs["Jinnah Hospital"].book("Areeba Shah", 3, "Routine Follow-up")
        self.app_mgrs["Jinnah Hospital"].book("Sarmad Ali", 3, "Throat Infection")
        self.app_mgrs["Jinnah Hospital"].book("Maryam Zehra", 2, "High Blood Pressure")


        # Saifee Hospital
        self.app_mgrs["Saifee Hospital"].book("Alyana Abid", 2, "Flu Symptoms")
        self.app_mgrs["Saifee Hospital"].book("Hassan Raza", 1, "Asthma Attack")
        self.app_mgrs["Saifee Hospital"].book("Fatima Noor", 3, "Blood Test")

        # Civil Hospital
        self.app_mgrs["Civil Hospital"].book("Zohaib Khan", 1, "Road Accident Injury")
        self.app_mgrs["Civil Hospital"].book("Sadia Mirza", 2, "Infection")
        self.app_mgrs["Civil Hospital"].book("Areesha Tariq", 3, "General Checkup")

        # Ziauddin Hospital
        self.app_mgrs["Ziauddin Hospital"].book("Talha Siddiqui", 2, "Back Pain")
        self.app_mgrs["Ziauddin Hospital"].book("Noor Fatima", 1, "Shortness of Breath")
        self.app_mgrs["Ziauddin Hospital"].book("Rehan Ali", 3, "X-ray Appointment")
        self.app_mgrs["Ziauddin Hospital"].book("Hiba Shafqat", 1, "Critical Injury")
        self.app_mgrs["Ziauddin Hospital"].book("Adeel Qureshi", 3, "Physiotherapy Session")
        self.app_mgrs["Ziauddin Hospital"].book("Sadia Hussain", 2, "Allergy Reaction")


        # Indus Hospital
        self.app_mgrs["Indus Hospital"].book("Kiran Baloch", 1, "High Risk Pregnancy")
        self.app_mgrs["Indus Hospital"].book("Shahzaib Akhtar", 2, "Ear Infection")
        self.app_mgrs["Indus Hospital"].book("Mariam Javed", 3, "Skin Rash")
# Start Page (REINSTATED)
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Center Frame (Card)
        center_card = tk.Frame(self, bg=controller.card_bg, padx=60, pady=60)
        center_card.grid(row=0, column=0, sticky="nsew", padx=150, pady=150)
        center_card.columnconfigure(0, weight=1)

        # Title Label
        tk.Label(center_card, text="Smart Care Navigator", bg=controller.card_bg,
                    fg=controller.highlight, font=("Helvetica", 36, "bold")).pack(pady=(20, 10))
        
        # Subtitle/Welcome
        tk.Label(center_card, text="🩺 Integrated Medical Appointment & Emergency Routing System 🗺️", 
                    bg=controller.card_bg, fg=controller.subtle, font=("Arial", 14)).pack(pady=(0, 40))

        # Start Button - MODIFIED to go to EmergencyRoutingPage
        tk.Button(center_card, text="Access Emergency Routing", 
                    command=lambda: controller.show_page("EmergencyRoutingPage"),
                    bg=controller.button_bg, fg="white", font=controller.title_font, 
                    relief="flat", padx=20, pady=10).pack(pady=(20, 0))

# Appointments Page
class AppointmentsPage(tk.Frame):
    LEFT_WIDTH = 360
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller
        self.columnconfigure(0, minsize=self.LEFT_WIDTH)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left_card = tk.Frame(self, bg=controller.card_bg, bd=0, padx=14, pady=12)
        left_card.grid(row=0, column=0, sticky="nswe", padx=(24,12), pady=24)

        title = tk.Label(left_card, text="📅 Appointment Scheduler", bg=controller.card_bg,
                         font=controller.title_font, fg=controller.highlight)
        title.pack(anchor="w", pady=(0,8))

        tk.Label(left_card, text="Target Hospital", bg=controller.card_bg, fg=controller.text_primary,
                 font=controller.label_font).pack(anchor="w", pady=(8,2))
        hospital_options = list(controller.graph.adj.keys())
        self.hospital_var = tk.StringVar(value=hospital_options[0])
        hospital_menu = tk.OptionMenu(left_card, self.hospital_var, *hospital_options,
                                      command=lambda e: self.update_queue_display())
        hospital_menu.config(width=26, bg=controller.button_bg, fg="white", font=controller.button_font)
        hospital_menu["menu"].config(bg=controller.panel_bg, fg=controller.text_primary)
        hospital_menu.pack(anchor="w", pady=2)

        tk.Label(left_card, text="Patient Name", bg=controller.card_bg, fg=controller.text_primary,
                 font=controller.label_font).pack(anchor="w", pady=(8,2))
        self.name_entry = tk.Entry(left_card, font=controller.text_font, width=28,
                                   bg=controller.entry_bg, relief="flat")
        self.name_entry.pack(anchor="w", pady=2)

        tk.Label(left_card, text="Priority (1=Emergency,2=Urgent,3=Standard)", bg=controller.card_bg,
                 fg=controller.text_primary, font=controller.label_font).pack(anchor="w", pady=(8,2))
        self.priority_var = tk.StringVar(value="3")
        priority_menu = tk.OptionMenu(left_card, self.priority_var, "1","2","3")
        priority_menu.config(width=5, bg=controller.button_bg, fg="white", font=controller.button_font)
        priority_menu["menu"].config(bg=controller.panel_bg, fg=controller.text_primary)
        priority_menu.pack(anchor="w", pady=2)

        tk.Label(left_card, text="Details", bg=controller.card_bg, fg=controller.text_primary,
                 font=controller.label_font).pack(anchor="w", pady=(8,2))
        self.details_entry = tk.Entry(left_card, font=controller.text_font, width=28,
                                      bg=controller.entry_bg, relief="flat")
        self.details_entry.pack(anchor="w", pady=2)

        btn_frame = tk.Frame(left_card, bg=controller.card_bg)
        btn_frame.pack(anchor="w", pady=12, fill="x")
        tk.Button(btn_frame, text="Book Appointment", command=self.book_appointment,
                  bg=controller.button_bg, fg="white", font=controller.button_font, relief="flat", padx=8).pack(side="left", padx=(0,8))
        tk.Button(btn_frame, text="Call Next Patient", command=self.call_next_patient,
                  bg=controller.warn, fg="white", font=controller.button_font, relief="flat", padx=8).pack(side="left")

        bottom_nav = tk.Frame(left_card, bg=controller.card_bg)
        bottom_nav.pack(side="bottom", fill="x", pady=(12,0))
        tk.Button(bottom_nav, text="Go to Emergency Routing",
                  command=lambda: controller.show_page("EmergencyRoutingPage"),
                  bg=controller.success, fg="black", font=controller.button_font, relief="flat").pack(side="right")
        tk.Button(bottom_nav, text="Go to Start Page",
                  command=lambda: controller.show_page("StartPage"),
                  bg=controller.subtle, fg="white", font=controller.button_font, relief="flat").pack(side="left")

        # Right panel
        right_card = tk.Frame(self, bg=controller.panel_bg, padx=14, pady=12)
        right_card.grid(row=0, column=1, sticky="nswe", padx=(12,24), pady=24)
        right_card.columnconfigure(0, weight=1)
        right_card.rowconfigure(1, weight=1)

        tk.Label(right_card, text="Current Appointment Queue", bg=controller.panel_bg,
                 font=controller.header_font, fg=controller.highlight).grid(row=0, column=0, sticky="w")

        self.queue_text = tk.Text(right_card, height=18, wrap="word", state="disabled", font=controller.text_font,
                                  bg=controller.bg_color, fg=controller.text_primary, bd=0, padx=8, pady=8)
        self.queue_text.grid(row=1, column=0, sticky="nswe", pady=(8,0))

        scrollbar = tk.Scrollbar(right_card, command=self.queue_text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(8,0))
        self.queue_text.config(yscrollcommand=scrollbar.set)

        self.queue_text.tag_configure("p1", foreground=controller.warn)
        self.queue_text.tag_configure("p2", foreground=controller.subtle)
        self.queue_text.tag_configure("p3", foreground=controller.success)
        self.queue_text.tag_configure("meta", foreground=controller.subtle)

        self.hospital_var.trace("w", lambda *args: self.update_queue_display())


    def book_appointment(self):
        name = self.name_entry.get().strip()
        details = self.details_entry.get().strip()
        hospital = self.hospital_var.get()
        try:
            priority = int(self.priority_var.get())
        except ValueError:
            messagebox.showerror("Input Error", "Priority must be 1, 2, or 3.")
            return
        if not name:
            messagebox.showerror("Input Error", "Please enter a patient name.")
            return
        if priority not in (1,2,3):
            messagebox.showerror("Input Error", "Priority must be 1, 2, or 3.")
            return

        full_details = f"{details}".strip()
        self.controller.app_mgrs[hospital].book(name, priority, full_details)
        messagebox.showinfo("Success", f"Appointment booked for {name} (Priority {priority}) at {hospital}.")
        self.name_entry.delete(0, tk.END)
        self.details_entry.delete(0, tk.END)
        self.update_queue_display()

    def call_next_patient(self):
        hospital = self.hospital_var.get()
        patient = self.controller.app_mgrs[hospital].pop_next()
        if not patient:
            messagebox.showinfo("Info", "No pending appointments.")
            return
        p, name, details = patient
        messagebox.showinfo("Now Serving", f"Patient: {name}\nPriority: {p}\nDetails: {details}")
        self.update_queue_display()

    def update_queue_display(self):
        hospital = self.hospital_var.get()
        items = self.controller.app_mgrs[hospital].peek_all()
        self.queue_text.config(state="normal")
        self.queue_text.delete("1.0", tk.END)
        if not items:
            self.queue_text.insert(tk.END, "No pending appointments.\n", "meta")
        else:
            for p, _, name, details in items:
                line = f"P: {p} | {name}"
                if details:
                    line += f" — {details}"
                line += "\n"
                tag = "p3"
                if p == 1:
                    tag = "p1"
                elif p == 2:
                    tag = "p2"
                self.queue_text.insert(tk.END, line, tag)
        self.queue_text.config(state="disabled")

# Emergency Routing Page 
class EmergencyRoutingPage(tk.Frame):
    LEFT_WIDTH = 360
    location_map = {
        "streat 21": (200, 520),
        "main street": (600, 500),
        "park avenue": (400, 400),
        "riverdale bridge": (100, 500),
        "industrial zone east": (800, 300),
        "old town square": (450, 250),
        "west suburbs exit": (150, 450)
    }
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller

        self.columnconfigure(0, minsize=self.LEFT_WIDTH)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Left panel (omitted for brevity)
        left_card = tk.Frame(self, bg=controller.card_bg, padx=14, pady=12)
        left_card.grid(row=0, column=0, sticky="nswe", padx=(24,12), pady=24)

        tk.Label(left_card, text="🚨 Emergency Routing", bg=controller.card_bg,
                    font=controller.title_font, fg=controller.highlight).pack(anchor="w", pady=(0,8))

        tk.Label(left_card, text="Your Current Location (type to set):", bg=controller.card_bg,
                    fg=controller.text_primary, font=controller.label_font).pack(anchor="w", pady=(6,2))
        self.location_entry = tk.Entry(left_card, width=30, font=controller.text_font,
                                            bg=controller.entry_bg, relief="flat")
        self.location_entry.pack(anchor="w", pady=2)

        tk.Label(left_card, text="(Simulated distances in km)", bg=controller.card_bg,
                    fg=controller.subtle, font=("Arial", 9)).pack(anchor="w", pady=(4,8))

        tk.Button(left_card, text="🚨 Find Nearest Hospital", command=self.find_nearest,
                    bg=controller.warn, fg="white", font=controller.button_font, relief="flat", padx=8, pady=6).pack(anchor="w", pady=(2,10))

        tk.Label(left_card, text="Search Result:", bg=controller.card_bg,
                    fg=controller.text_primary, font=controller.label_font).pack(anchor="w", pady=(6,2))
        self.result_text = tk.Text(left_card, height=10, width=36, state="disabled",
                                     font=controller.text_font, bd=0, relief="flat", bg=controller.bg_color, fg=controller.text_primary, padx=8, pady=8, wrap="word")
        self.result_text.pack(fill="x", pady=6)

        bottom_nav = tk.Frame(left_card, bg=controller.card_bg)
        bottom_nav.pack(fill="x", pady=(6,0))
        # Changed navigation to go to AppointmentsPage
        tk.Button(bottom_nav, text="Go to Appointments", command=lambda: controller.show_page("AppointmentsPage"),
                    bg=controller.button_bg, fg="white", font=controller.button_font, relief="flat").pack(side="right")
        tk.Button(bottom_nav, text="Go to Start Page",
                    command=lambda: controller.show_page("StartPage"),
                    bg=controller.subtle, fg="white", font=controller.button_font, relief="flat").pack(side="left")
        
        
        # Right panel: map canvas
        right_card = tk.Frame(self, bg=controller.panel_bg, padx=12, pady=12)
        right_card.grid(row=0, column=1, sticky="nswe", padx=(12,24), pady=24)
        right_card.rowconfigure(1, weight=1)
        right_card.columnconfigure(0, weight=1)

        tk.Label(right_card, text="🗺️ Hospital Network Map (distances in km)",
                    bg=controller.panel_bg, fg=controller.highlight, font=controller.header_font).grid(row=0, column=0, sticky="w")

        self.canvas = tk.Canvas(right_card, bg=controller.bg_color, bd=0, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nswe", pady=(8,0))

        self.v_scroll = tk.Scrollbar(right_card, orient="vertical", command=self.canvas.yview)
        self.v_scroll.grid(row=1, column=1, sticky="ns")
        self.h_scroll = tk.Scrollbar(right_card, orient="horizontal", command=self.canvas.xview)
        self.h_scroll.grid(row=2, column=0, sticky="we")
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        self.canvas_frame = tk.Frame(self.canvas, bg=self.canvas['bg'])
        self.canvas_window = self.canvas.create_window((0,0), window=self.canvas_frame, anchor="nw")
        # Bind the canvas resize event to redraw and center the map
        self.canvas.bind('<Configure>', self.recenter_map)
        
        self.current_route = None
        self.user_pos = None

        self.draw_map()

    def recenter_map(self, event=None):
        """Called on resize to ensure the map drawing remains centered."""
        self.draw_map()

    def reset_map_state(self):
        """Resets the map state to show only the original hospital network."""
        self.current_route = None
        self.user_pos = None
        
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state="disabled")
        
        self.draw_map() 
    
    def find_nearest(self):
        start_label = self.location_entry.get().strip()
        if not start_label:
            messagebox.showerror("Input Error", "Enter your location name.")
            return

        # 1. Create a DEEP COPY of the original graph to isolate the user node
        temp_graph = Graph()
        # Copy nodes and positions
        temp_graph.adj = {k: v.copy() for k, v in self.controller.graph.adj.items()}
        temp_graph.node_positions = self.controller.graph.node_positions.copy()
        
        # Set user location (can be pre-defined or simulated if not found)
        # Normalize the input to lowercase for lookup against the location_map keys
        normalized_label = start_label.lower() 
        if normalized_label in self.location_map:
            user_x, user_y = self.location_map[normalized_label]
            start_label = normalized_label # Use normalized key for consistency
        else:
            # Simple simulation for a new location near the existing network
            user_x = 50 + (hash(start_label) % 900)
            user_y = 50 + (hash(start_label) % 500)
            
        temp_graph.add_hospital(start_label, user_x, user_y)
        self.user_pos = start_label 

        # 2. Connect user location to existing hospitals
        hospital_nodes = list(self.controller.graph.adj.keys()) 
        temp_graph.adj[start_label] = {}
        
        for hosp in hospital_nodes:
             if hosp != start_label:
                 x1, y1 = temp_graph.node_positions[start_label]
                 x2, y2 = temp_graph.node_positions[hosp]
                 # Distance calculation
                 distance = int(((x1-x2)**2 + (y1-y2)**2)**0.5 / 20)
                 distance = max(distance, 5) 
                 
                 temp_graph.adj[start_label][hosp] = distance
                 # Ensure the back-connection is correctly added to the temp_graph copy
                 if hosp in temp_graph.adj:
                     temp_graph.adj[hosp][start_label] = distance 

        # 3. Find the shortest path using Dijkstra
        dist, prev = temp_graph.dijkstra(start_label)
        
        # 4. Find the nearest hospital 
        nearest_hosp = min(
            self.controller.graph.adj.keys(), # Only consider original hospitals
            key=lambda h: dist.get(h, float('inf')) 
        )
        
        route = temp_graph.reconstruct_route(prev, nearest_hosp)

        # 5. Store the final route and the nearest hospital name
        self.current_route = (temp_graph, route) 
        self.controller.last_shortest_hospital = nearest_hosp # Store nearest hospital

        # 6. Update results text
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Nearest Hospital: {nearest_hosp}\nDistance: {dist[nearest_hosp]} km\nRoute: {' → '.join(route)}")
        self.result_text.config(state="disabled")
        
        # 7. Redraw the map
        self.draw_map()
        
    def draw_map(self):
        self.canvas.delete("all")
        
        g = self.controller.graph 
        route_nodes = []
        
        if self.current_route is not None:
            g = self.current_route[0]
            route_nodes = self.current_route[1]
            
        # 1. Draw Edges (Roads)
        for a, nbrs in g.adj.items():
            x1, y1 = g.node_positions.get(a, (0,0))
            for b, dist in nbrs.items():
                if a < b:  # prevent double draw
                    x2, y2 = g.node_positions.get(b, (0,0))
                    
                    is_in_route = False
                    if len(route_nodes) >= 2:
                        for i in range(len(route_nodes) - 1):
                            n1, n2 = route_nodes[i], route_nodes[i+1]
                            if (a == n1 and b == n2) or (a == n2 and b == n1):
                                is_in_route = True
                                break
                                
                    line_color = self.controller.warn if is_in_route else self.controller.subtle
                    
                    self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=2, tags="map_element")
                    self.canvas.create_text(
                        (x1+x2)/2, (y1+y2)/2 - 6, 
                        text=f"{dist} km", 
                        fill=self.controller.subtle, 
                        font=("Arial", 8, "bold" if is_in_route else "normal"),
                        tags="map_element"
                    )

        # 2. Draw Nodes (Hospitals/Location)
        for node, (x, y) in g.node_positions.items():
            is_hospital = node in self.controller.graph.adj # Check if it's one of the permanent hospitals
            fill_color = self.controller.button_bg if is_hospital else self.controller.highlight
            outline_color = "white"
            size = 10
            
            if node == self.user_pos and self.current_route is not None:
                fill_color = self.controller.highlight 
                outline_color = self.controller.warn
                size = 12
            elif node in route_nodes and is_hospital:
                fill_color = self.controller.warn
                outline_color = self.controller.highlight
                size = 10

            self.canvas.create_oval(x-size, y-size, x+size, y+size, 
                                         fill=fill_color, outline=outline_color, width=2, tags="map_element")
            
            self.canvas.create_text(x, y - size - 4, 
                                         text=node, 
                                         fill=self.controller.text_primary, 
                                         font=("Arial", 10, "bold" if node in route_nodes else "normal"), 
                                         anchor="s",
                                         tags="map_element")
            
        # 3. Center the map drawing within the canvas
        self.canvas.update_idletasks()
        
        # Get bounding box for all drawn elements
        bbox = self.canvas.bbox("map_element") 
        if bbox:
            x_min, y_min, x_max, y_max = bbox
            
            # Dimensions of the drawn content
            map_width = x_max - x_min
            map_height = y_max - y_min
            
            # Dimensions of the canvas viewable area
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Calculate shift needed to center the content
            x_shift = (canvas_width / 2) - (x_min + map_width / 2)
            y_shift = (canvas_height / 2) - (y_min + map_height / 2)

            # Move all drawn elements
            self.canvas.move("map_element", x_shift, y_shift)

        # Set scrollregion to cover the entire drawing area after movement, or just canvas size
        self.canvas.config(scrollregion=(0, 0, max(self.canvas.winfo_width(), x_max - x_min + 50), max(self.canvas.winfo_height(), y_max - y_min + 50)))


# Run App
if __name__ == "__main__":
    app = SmartMedicalApp()
    app.mainloop()

