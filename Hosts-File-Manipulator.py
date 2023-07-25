import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from ipaddress import ip_address
import re

HOSTS_FILE = r"C:\Windows\System32\drivers\etc\hosts"

def is_valid_domain(domain):
    if len(domain) > 0 and "." in domain:
        return True
    return False

def is_valid_ip(ip):
    try:
        ip_address(ip)
        return True
    except ValueError:
        return False

def get_domains():
    with open(HOSTS_FILE, 'r') as file:
        return [line for line in file if line.count('.') > 1 and not line.startswith('#')]

def add_domain():
    ip = ip_var.get()
    domain = domain_var.get()
    comment = comment_var.get()

    if not is_valid_domain(domain) or not is_valid_ip(ip):
        messagebox.showerror("Error", "Invalid domain or IP address")
        return

    with open(HOSTS_FILE, 'r+') as file:
        lines = file.readlines()
        for line in lines:
            if domain in line.split():
                messagebox.showerror("Error", "Domain already exists")
                return
        file.write('# ' + comment + '\n' + ip + ' ' + domain + '\n')

    messagebox.showinfo("Success", "Domain added successfully")
    update_domains()

def remove_domain():
    selected_items = tree.selection()
    if not messagebox.askyesno("Confirmation", "Are you sure you want to remove the selected domains?"):
        return
    for selected_item in selected_items:
        domain = tree.item(selected_item)['values'][1]
        with open(HOSTS_FILE, 'r') as file:
            lines = file.readlines()

        with open(HOSTS_FILE, 'w') as file:
            for line in lines:
                if domain not in line.split():
                    file.write(line)

    messagebox.showinfo("Success", "Selected domains removed successfully")
    update_domains()

def edit_domain():
    selected_item = tree.selection()[0]
    ip, domain, comment = tree.item(selected_item)['values']
    comment = comment[2:]  # remove '# '

    edit_window = tk.Toplevel(window)
    edit_window.title("Edit Domain")
    edit_window.geometry('350x100')

    new_ip_var = tk.StringVar(edit_window, value=ip)
    tk.Label(edit_window, text="IP Address:").grid(row=0, column=0, sticky='e')
    tk.Entry(edit_window, textvariable=new_ip_var).grid(row=0, column=1)

    new_domain_var = tk.StringVar(edit_window, value=domain)
    tk.Label(edit_window, text="Domain:").grid(row=1, column=0, sticky='e')
    tk.Entry(edit_window, textvariable=new_domain_var).grid(row=1, column=1)

    new_comment_var = tk.StringVar(edit_window, value=comment)
    tk.Label(edit_window, text="Comment:").grid(row=2, column=0, sticky='e')
    tk.Entry(edit_window, textvariable=new_comment_var).grid(row=2, column=1)

    def save_changes():
        new_ip = new_ip_var.get()
        new_domain = new_domain_var.get()
        new_comment = new_comment_var.get()

        if not is_valid_ip(new_ip) or not is_valid_domain(new_domain):
            messagebox.showerror("Error", "Invalid IP address or domain")
            return

        with open(HOSTS_FILE, 'r') as file:
            lines = file.readlines()

        with open(HOSTS_FILE, 'w') as file:
            for i, line in enumerate(lines):
                if domain in line.split():
                    lines[i] = new_ip + ' ' + new_domain + '\n'
                if i != 0 and '#' in lines[i - 1]:
                    lines[i - 1] = '# ' + new_comment + '\n'
                file.write(lines[i])

        messagebox.showinfo("Success", "Domain edited successfully")
        update_domains()
        edit_window.destroy()

    tk.Button(edit_window, text="Save", command=save_changes).grid(row=3, column=0, columnspan=2)

def update_domains():
    for i in tree.get_children():
        tree.delete(i)

    domains = get_domains()
    for domain in domains:
        ip, domain = domain.split()
        comment = ""
        with open(HOSTS_FILE, 'r') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if domain in line and i != 0 and '#' in lines[i - 1]:
                    comment = lines[i - 1].strip()
        tree.insert('', 'end', values=(ip, domain, comment))

def main():
    global window, tree, ip_var, domain_var, comment_var
    window = tk.Tk()
    window.title("Domain Management")
    window.geometry('700x500')
    window.configure(bg='#282a36')

    ip_var = tk.StringVar()
    domain_var = tk.StringVar()
    comment_var = tk.StringVar()

    top_frame = tk.Frame(window, bg='#282a36')
    top_frame.pack(fill='x', padx=10, pady=10)

    tk.Label(top_frame, text="IP Address:", bg='#282a36', fg='#f8f8f2').grid(row=0, column=0)
    tk.Entry(top_frame, textvariable=ip_var, bg='#44475a', fg='#f8f8f2').grid(row=0, column=1)

    tk.Label(top_frame, text="Domain:", bg='#282a36', fg='#f8f8f2').grid(row=0, column=2)
    tk.Entry(top_frame, textvariable=domain_var, bg='#44475a', fg='#f8f8f2').grid(row=0, column=3)

    tk.Label(top_frame, text="Comment:", bg='#282a36', fg='#f8f8f2').grid(row=0, column=4)
    tk.Entry(top_frame, textvariable=comment_var, bg='#44475a', fg='#f8f8f2').grid(row=0, column=5)

    tk.Button(top_frame, text="Add a domain", command=add_domain, bg='#50fa7b', fg='#282a36').grid(row=0, column=6, padx=10)

    tk.Frame(window, bg='#6272a4', height=1).pack(fill='x', padx=10, pady=10)

    mid_frame = tk.Frame(window, bg='#282a36')
    mid_frame.pack(fill='x', padx=10, pady=10)

    tk.Button(mid_frame, text="Edit selected domain", command=edit_domain, bg='#8be9fd', fg='#282a36').grid(row=0, column=0)
    tk.Button(mid_frame, text="Remove selected domains", command=remove_domain, bg='#ff5555', fg='#282a36').grid(row=0, column=1)

    tree = ttk.Treeview(window, style='Treeview')
    tree["columns"]=("IP", "Domain", "Comment")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("IP", width=150)
    tree.column("Domain", width=150)
    tree.column("Comment", width=200)

    tree.heading("IP", text="IP", anchor=tk.W)
    tree.heading("Domain", text="Domain", anchor=tk.W)
    tree.heading("Comment", text="Comment", anchor=tk.W)

    tree.pack(fill='both', expand=True, padx=10, pady=10)

    style = ttk.Style()
    style.theme_use('default')
    style.configure('Treeview', background='#44475a', foreground='#f8f8f2', rowheight=25)
    style.configure('Treeview.Heading', background='#6272a4', foreground='#f8f8f2')

    update_domains()
    window.mainloop()

if __name__ == "__main__":
    main()
