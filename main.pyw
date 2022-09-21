import numpy as np
import tkinter as tk
import tkinter.messagebox as messagebox
import pickle
import os

import matplotlib.pyplot as plt
import networkx as nx

users = {}
papers = {}

def save():
    f = open("db.pickle","wb")
    pickle.dump((users,papers),f)
    f.close()

def create_user(uid,name):
    users[uid] = {"name":name,"uid":uid,"papers":[]}
    return users[uid]

def create_paper(pid,name,authors,references):
    papers[pid] = {"name":name,"pid":pid,"authors":authors,"references":references,"citations":[]}
    for author in authors:
                author["papers"].append(papers[pid])
    for reference in references:
                reference["citations"].append(papers[pid])
    return papers[pid]

def generate_uid():
    uid = 0
    if users!={}:
        uid = max(users.keys())
    return uid+1

def generate_pid():
    pid = 0
    if papers!={}:
        pid = max(papers.keys())
    return pid+1

def BM(p,t):
    l = len(p)
    if l==0:
        return 0
    m = {}
    for i,c in enumerate(p[:-1]):
        m[c] = l-i-1
    if p[-1] not in m.keys():
        m[p[-1]] = l
    i = 0
    while i<=len(t)-l:
        for j in range(l-1,-1,-1):
            if t[i+j] != p[j]:
                if t[i+j] in m.keys():
                    i += m[t[i+j]]
                else:
                    i+=l
                break
            if j==0:
                return i
    return -1
    

def search_user(name):
    u = {}
    for k,v in users.items():
        if BM(name,v["name"].lower())!=-1:
            u[k] = v
    return u

def search_paper(name):
    p = {}
    for k,v in papers.items():
        if BM(name,v["name"].lower())!=-1:
            p[k] = v
    return p

def score(user):
    s = 0
    p = user["papers"]
    for i in range(len(p)):
        c = 0
        for paper in p:
            if len(paper["citations"])>s:
                c+=1
        if c>=s:
            s+=1
        else:
            break
    return s

root = tk.Tk()
root.title("Papers")
root.geometry("500x500")

if os.path.exists("db.pickle"):
    f = open("db.pickle","rb")
    users,papers = pickle.load(f)
    f.close()

def root_close():
    root.destroy()
    save()
root.protocol("WM_DELETE_WINDOW",root_close)

menu = tk.Menu(root)
users_menu = tk.Menu(menu,tearoff=0)
def new_user():
    print("New User")
    top = tk.Toplevel(root)
    top.title("New User")
    name_label = tk.Label(top,text="Name:")
    name_label.grid(row=1,column=1)
    name_entry = tk.Entry(top)
    name_entry.grid(row=1,column=2)
    create_button = tk.Button(top,text="Create")
    create_button.grid(row=2,column=2)
    def action(*args):
        name = name_entry.get()
        uid = generate_uid()
        if name!='':
            print(name,uid)
            print(create_user(uid,name))
            messagebox.showinfo("User info",f"UID for user {name} is {uid}")
            top.destroy()
    create_button["command"] = action
    name_entry.bind("<Return>",action)
users_menu.add_command(label="New User",command=new_user)
def show_users():
    print("Show User")
    top = tk.Toplevel(root)
    top.title("Show Users")
    top.geometry("300x300")
    name_entry = tk.Entry(top)
    name_entry.pack()
    f = [tk.Frame(top)]
    allowed_users = [users]
    def search(*args):
        name = name_entry.get()
        allowed_users[0] = search_user(name.lower())
        display()
    name_entry.bind("<Return>",search)
    def display():
        f[0].destroy()
        f[0] = tk.Frame(top)
        uid_display = tk.Label(f[0],text="UID")
        uid_display.grid(row=1,column=1)
        name_display = tk.Label(f[0],text="Name")
        name_display.grid(row=1,column=2)
        score_display = tk.Label(f[0],text="Score")
        score_display.grid(row=1,column=3)
        for uid,user in allowed_users[0].items():
            uid_label = tk.Label(f[0],text=str(uid))
            uid_label.grid(row=uid+2,column=1)
            name_label = tk.Label(f[0],text=user["name"])
            name_label.grid(row=uid+2,column=2)
            score_label = tk.Label(f[0], text=str(score(user)))
            score_label.grid(row=uid+2,column=3)
        f[0].pack()
    display()
users_menu.add_command(label="Users",command=show_users)
menu.add_cascade(label="Users",menu=users_menu)
papers_menu = tk.Menu(menu,tearoff=0)
def new_paper():
    print("New Paper")
    top = tk.Toplevel(root)
    top.title("New Paper")
    name_label = tk.Label(top,text="Name:")
    name_label.grid(row=1,column=1)
    name_entry = tk.Entry(top)
    name_entry.grid(row=1,column=2)
    authors_label = tk.Label(top,text="Author UIDs seperated by ',' :")
    authors_label.grid(row=2,column=1)
    authors_entry = tk.Entry(top)
    authors_entry.grid(row=2,column=2)
    reference_label = tk.Label(top,text="Reference PIDs seperated by ',' :")
    reference_label.grid(row=3,column=1)
    reference_entry = tk.Entry(top)
    reference_entry.grid(row=3,column=2)
    create_button = tk.Button(top,text="Create")
    create_button.grid(row=4,column=2)
    def action(*args):
        name = name_entry.get()
        a = authors_entry.get()
        r = reference_entry.get()
        if name!='' and a!='':
            uids = a.split(',')
            authors = []
            for uid in uids:
                try:
                    authors.append(users[int(uid)])
                except:
                    messagebox.showerror("Paper Error",f"{uid} is not a uid")
                    return None
            references = []
            if r!='':
                pids = r.split(',')
                for pid in pids:
                    try:
                        references.append(papers[int(pid)])
                    except:
                        messagebox.showerror("Paper Error",f"{pid} is not a pid")
            pid = generate_pid()
            print(name,pid)
            paper = create_paper(pid,name,authors,references)
            messagebox.showinfo("Paper info",f"PID for paper {name} is {pid}")
            top.destroy()
    create_button["command"] = action
papers_menu.add_command(label="New Paper",command=new_paper)
def show_papers():
    print("Show User")
    top = tk.Toplevel(root)
    top.title("Show Users")
    top.geometry("300x300")
    name_entry = tk.Entry(top)
    name_entry.pack()
    f = [tk.Frame(top)]
    allowed_papers = [papers]
    def search(*args):
        name = name_entry.get()
        allowed_papers[0] = search_paper(name.lower())
        display()
    name_entry.bind("<Return>",search)
    def display():
        f[0].destroy()
        f[0] = tk.Frame(top)
        pid_display = tk.Label(f[0],text="PID")
        pid_display.grid(row=1,column=1)
        name_display = tk.Label(f[0],text="Name")
        name_display.grid(row=1,column=2)
        authors_display = tk.Label(f[0],text="Authors")
        authors_display.grid(row=1,column=3)
        references_display = tk.Label(f[0],text="References")
        references_display.grid(row=1,column=4)
        citations_display = tk.Label(f[0],text="Citations")
        citations_display.grid(row=1,column=5)
        for pid,paper in allowed_papers[0].items():
            pid_label = tk.Label(f[0],text=str(pid))
            pid_label.grid(row=pid+2,column=1)
            name_label = tk.Label(f[0],text=paper["name"])
            name_label.grid(row=pid+2,column=2)
            a = ""
            for author in paper["authors"]:
                a+=str(author["uid"])+", "
            authors_label = tk.Label(f[0],text=a[:-2])
            authors_label.grid(row=pid+2,column=3)
            r = ""
            for reference in paper["references"]:
                r+=str(reference["pid"])+", "
            references_label = tk.Label(f[0],text=r[:-2])
            references_label.grid(row=pid+2,column=4)
            citations_label = tk.Label(f[0], text=str(len(paper["citations"])))
            citations_label.grid(row=pid+2,column=5)
        f[0].pack()
    display()
papers_menu.add_command(label="Papers",command=show_papers)
menu.add_cascade(label="Papers",menu=papers_menu)
view_menu = tk.Menu(menu,tearoff=0)
def view_user_graph():
    print("View user graph")
    g = nx.DiGraph()
    for uid,user in users.items():
        if user["papers"]==[]:
            g.add_node(uid)
    for uid1,user in users.items():
        for paper in user["papers"]:
            for author in paper["authors"]:
                if author!=user:
                    g.add_edge(uid1,author['uid'],color='green')
                    g.add_edge(author['uid'],uid1,color='green')
            for reference in paper["references"]:
                for author in reference["authors"]:
                    if author!=user:
                        g.add_edge(uid1,author["uid"],color='orange',label=reference["name"])
    colors = nx.get_edge_attributes(g,'color').values()
    #labels = nx.get_edge_attributes(g,'label')
    pos = nx.spring_layout(g)
    nx.draw(g,pos=pos,with_labels=True,node_size=1000,edge_color=colors,connectionstyle='arc3, rad = 0.1')
    #nx.draw_networkx_edge_labels(g,pos,edge_labels=labels,label_pos=0.5)
    plt.show()
view_menu.add_command(label="User Graph",command=view_user_graph)
def view_paper_graph():
    print("View paper graph")
    g = nx.DiGraph()
    for pid,paper in papers.items():
        if paper["citations"]==[]:
            g.add_node(pid)
    for pid1,paper1 in papers.items():
        for paper2 in paper1["references"]:
                    g.add_edge(pid1,paper2["pid"],color='orange')
    colors = nx.get_edge_attributes(g,'color').values()
    nx.draw(g,with_labels=True,node_size=1000,edge_color=colors,connectionstyle='arc3, rad = 0.1')
    plt.show()
view_menu.add_command(label="Paper Graph",command=view_paper_graph)
menu.add_cascade(label="View",menu=view_menu)
root["menu"] = menu

root.mainloop()
