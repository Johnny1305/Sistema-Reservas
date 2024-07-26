import tkinter as tk
from tkinter import ttk, messagebox
from supabase_client import supabase
from datetime import datetime

def fetch_reservations():
    response = supabase.table('reservations').select('*').execute()
    return response.data

def create_reservation(name, date, time, guests):
    response = supabase.table('reservations').insert({
        'name': name,
        'date': date,
        'time': time,
        'guests': guests
    }).execute()
    return response.data

def delete_reservation(reservation_id):
    response = supabase.table('reservations').delete().eq('id', reservation_id).execute()
    return response.data

def update_reservation(reservation_id, name=None, date=None, time=None, guests=None):
    updates = {}
    if name:
        updates['name'] = name
    if date:
        updates['date'] = date
    if time:
        updates['time'] = time
    if guests:
        updates['guests'] = guests
    response = supabase.table('reservations').update(updates).eq('id', reservation_id).execute()
    return response.data

class ReservationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reservas")

        # Ajustar el tamaño de la ventana
        self.root.geometry("800x400")

        # Crear la barra de menús
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        # Crear el menú "Opciones"
        self.options_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Opciones", menu=self.options_menu)
        self.options_menu.add_command(label="Crear Reserva", command=self.open_create_window)
        self.options_menu.add_command(label="Editar Reserva", command=self.open_edit_window)
        self.options_menu.add_command(label="Eliminar Reserva", command=self.delete_reservation)

        # Menú Acerca de
        self.about_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Info", menu=self.about_menu)
        self.about_menu.add_command(label="Acerca de", command=self.show_info)

        # Treeview para mostrar reservas
        self.tree = ttk.Treeview(root, columns=('ID', 'Name', 'Date', 'Time', 'Guests'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Nombre')
        self.tree.heading('Date', text='Fecha')
        self.tree.heading('Time', text='Hora')
        self.tree.heading('Guests', text='Invitados')
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.load_data()

    def load_data(self):
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')
        today = now.strftime('%Y-%m-%d')
        self.reservations = fetch_reservations()  # Cargar las reservas globalmente
        for row in self.tree.get_children():
            self.tree.delete(row)
        for reservation in self.reservations:
            reservation_time = reservation['time']
            reservation_date = reservation['date']
            if reservation_date == today and reservation_time < current_time:
                # Reserva pasada
                self.tree.insert('', 'end', values=(reservation['id'], reservation['name'], reservation['date'], reservation['time'], reservation['guests']), tags=('past',))
            elif reservation_date == today:
                # Reserva del día actual
                self.tree.insert('', 'end', values=(reservation['id'], reservation['name'], reservation['date'], reservation['time'], reservation['guests']), tags=('today',))
            else:
                self.tree.insert('', 'end', values=(reservation['id'], reservation['name'], reservation['date'], reservation['time'], reservation['guests']))
        
        # Configurar estilos
        self.tree.tag_configure('today', background='lightblue')
        self.tree.tag_configure('past', background='lightcoral')

    def open_create_window(self):
        self.create_window = tk.Toplevel(self.root)
        self.create_window.title("Crear Reserva")
        self.create_window.geometry("400x220")

        tk.Label(self.create_window, text="Nombre").pack()
        self.name_entry = tk.Entry(self.create_window)
        self.name_entry.pack()

        tk.Label(self.create_window, text="Fecha (YYYY-MM-DD)").pack()
        self.date_entry = tk.Entry(self.create_window)
        self.date_entry.pack()

        tk.Label(self.create_window, text="Hora (HH:MM:SS)").pack()
        self.time_entry = tk.Entry(self.create_window)
        self.time_entry.pack()

        tk.Label(self.create_window, text="Número de Invitados").pack()
        self.guests_entry = tk.Entry(self.create_window)
        self.guests_entry.pack()

        tk.Button(self.create_window, text="Crear", command=self.create_reservation).pack(pady=10)

    def create_reservation(self):
        name = self.name_entry.get()
        date = self.date_entry.get()
        time = self.time_entry.get()
        guests = int(self.guests_entry.get())

        create_reservation(name, date, time, guests)
        self.load_data()
        self.create_window.destroy()

    def open_edit_window(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona una reserva para editar")
            return

        reservation_id = int(self.tree.item(selected_item[0], 'values')[0])
        print(f"ID de reserva seleccionado: {reservation_id}")  # Depuración
        reservation = next((r for r in self.reservations if r['id'] == reservation_id), None)

        if not reservation:
            messagebox.showerror("Error", "Reserva no encontrada")
            print(f"Reservas disponibles: {self.reservations}")  # Depuración
            return

        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Editar Reserva")
        self.edit_window.geometry("400x220")

        tk.Label(self.edit_window, text="Nombre").pack()
        self.edit_name_entry = tk.Entry(self.edit_window)
        self.edit_name_entry.insert(0, reservation['name'])
        self.edit_name_entry.pack()

        tk.Label(self.edit_window, text="Fecha (YYYY-MM-DD)").pack()
        self.edit_date_entry = tk.Entry(self.edit_window)
        self.edit_date_entry.insert(0, reservation['date'])
        self.edit_date_entry.pack()

        tk.Label(self.edit_window, text="Hora (HH:MM:SS)").pack()
        self.edit_time_entry = tk.Entry(self.edit_window)
        self.edit_time_entry.insert(0, reservation['time'])
        self.edit_time_entry.pack()

        tk.Label(self.edit_window, text="Número de Invitados").pack()
        self.edit_guests_entry = tk.Entry(self.edit_window)
        self.edit_guests_entry.insert(0, reservation['guests'])
        self.edit_guests_entry.pack()

        tk.Button(self.edit_window, text="Actualizar", command=lambda: self.edit_reservation(reservation_id)).pack(pady=10)

    def edit_reservation(self, reservation_id):
        name = self.edit_name_entry.get()
        date = self.edit_date_entry.get()
        time = self.edit_time_entry.get()
        guests = int(self.edit_guests_entry.get())

        print(f"Actualizando reserva ID: {reservation_id}")  # Depuración
        print(f"Datos de reserva: {name}, {date}, {time}, {guests}")  # Depuración
        update_reservation(reservation_id, name, date, time, guests)
        self.load_data()
        self.edit_window.destroy()

    def delete_reservation(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona una reserva para eliminar")
            return
        reservation_id = int(self.tree.item(selected_item[0], 'values')[0])
        delete_reservation(reservation_id)
        self.load_data()

    def show_info(self):
        info_message = "Sistema de Reservas\n\nVersion 1.0\nDesarrollado por [Johnny13]"
        messagebox.showinfo("Acerca de", info_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = ReservationApp(root)
    root.mainloop()
