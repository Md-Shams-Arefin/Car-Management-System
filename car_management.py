import tkinter as tk
from tkinter import messagebox

START_USER = 228
END_USER = 275

CARS = ["V-1", "V-2", "AutoV-3", "V-4"]

used_users = {}

root = tk.Tk()
root.title("Car Management System")
root.geometry("750x650")

title = tk.Label(root, text="Car Management System", font=("Arial", 20, "bold"))
title.pack(pady=10)

frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

canvas = tk.Canvas(frame)
scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)

scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


def toggle_car(user_id, car_name, btn):
    # If already used → make green again
    if user_id in used_users and used_users[user_id] == car_name:
        del used_users[user_id]

        btn.config(
            bg="green",
            fg="white",
            text=car_name
        )

        messagebox.showinfo("Removed", f"Student {user_id} removed from {car_name}")
        return

    # If another car already used
    if user_id in used_users:
        messagebox.showwarning(
            "Already Used",
            f"Student {user_id} already used {used_users[user_id]}"
        )
        return

    # Assign car
    used_users[user_id] = car_name

    btn.config(
        bg="red",
        fg="white",
        text=f"{car_name}\nUSED"
    )

    messagebox.showinfo(
        "Assigned",
        f"Student {user_id} assigned to {car_name}"
    )


for user in range(START_USER, END_USER + 1):

    row = tk.Frame(scrollable_frame, pady=4)
    row.pack(fill="x")

    user_label = tk.Label(
        row,
        text=f"Student - {user}",
        width=12,
        font=("Arial", 11, "bold")
    )

    user_label.pack(side="left")

    for car in CARS:

        btn = tk.Button(
            row,
            text=car,
            bg="green",
            fg="white",
            width=10,
            height=2
        )

        btn.config(
            command=lambda u=user, c=car, b=btn: toggle_car(u, c, b)
        )

        btn.pack(side="left", padx=5)


root.mainloop()
