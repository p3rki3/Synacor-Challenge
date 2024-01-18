import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from vm import VM, VMInOut   # Requires python >= 3.10 (match/case statements)
import threading
import time
from typing import Any

def start_vm(vm):
    vm.run_vm()

def run_vm():
    global myvm, fspeed, ftrace, fusedips, ftest
    myvm.slow = True if fspeed.get() == 1 else False
    myvm.fulltrace = True if ftrace.get() == 1 else False
    myvm.usedips = True if fusedips.get() == 1 else False
    myvm.test = True if ftest.get() == 1 else False
    myvm.start_vm_flag = 1

def create_widgets():
    global wip, wregs, wipval, wregsval, codes, locs, codevals, codelocs, game_txt, instr_txt, wcount, wcounter, userinp, wuserinp, fspeed, ftrace, fusedips, ftest

    labelname = ["IP Address", "Register 1", "Register 2", "Register 3", "Register 4", "Register 5", "Register 6", "Register 7", "Register 8", "Counter", "Code1", "Code2", "Code3", "Code4", "Code5", "Code6", "Code7", "Code8", "IP, Registers, Codes", "Select Options" ]
    labelrow = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 1, 1]
    labelcol = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3 ]
    for i in range(len(labelname)):
        l_temp = tk.Label(root, text=labelname[i])
        l_temp.grid(row=labelrow[i], column=labelcol[i], padx=15, pady=2, sticky="e")
    
    close_button = tk.Button(text="Close VM!", width=15, height=3, command=root.destroy).grid(row=21, column=3, padx=5, pady=5)
    run_button = tk.Button(text="Run VM!", width=15, height=3, command=run_vm).grid(row=21, column=2, padx=5, pady=5)
    wip = tk.Entry(root, textvariable=wipval, width=15)
    wip.grid(row=2, column=2)
    wcount = tk.Entry(root, textvariable=wcounter, width=15)
    wcount.grid(row=11, column=2)
    for i in range(8):
        wregs[i] = tk.Entry(root, textvariable=wregsval[i], width=15)
        wregs[i].grid(row=3+i, column=2)
        codes[i] = tk.Entry(root, textvariable=codevals[i], width=15)
        codes[i].grid(row=12+i, column=2)
        locs[i] = tk.Entry(root, textvariable=codelocs[i], width=15)
        locs[i].grid(row=12+i, column=3, padx=5)
    game_txt = ScrolledText(root, height=25, width=120, font=("consolas", "8", "normal"))
    game_txt.grid(row=2, rowspan=12, column=4)
    game_txt.configure(state="normal")
    instr_txt = ScrolledText(root, height=15, width=120, font=("consolas", "8", "normal"))
    instr_txt.grid(row=14, rowspan=8, column=4)
    instr_txt.configure(state="normal")
    wuserinp = tk.Entry(root, textvariable=userinp, width=123)
    wuserinp.grid(row=23, column=4, pady=5)

    fspeed = tk.IntVar(root, 1 if myvm.slow == True else 0)
    tk.Checkbutton(root, text="Slow VM Down?", variable=fspeed).grid(row=2, column=3, padx=5)
    ftrace = tk.IntVar(root, 1 if myvm.fulltrace == True else 0)
    tk.Checkbutton(root, text="Dump Trace to file?", variable=ftrace).grid(row=3, column=3, padx=5)
    fusedips = tk.IntVar(root, 1 if myvm.usedips == True else 0)
    tk.Checkbutton(root, text="Used IPs to file?", variable=fusedips).grid(row=4, column=3, padx=5)
    ftest = tk.IntVar(root, 1 if myvm.test == True else 0)
    tk.Checkbutton(root, text="Run Initial test?", variable=ftest).grid(row=5, column=3, padx=5)

def update_widgets(delay):
    global wipval, wregsval, codevals, codelocs, wcounter
    while True:
        wipval.set(myvm.ip)
        wcounter.set(myvm.instcount)
        for i in range(8):
            wregsval[i].set(myvm.regs[i])
            codevals[i].set(vminout.codes[i])
            codelocs[i].set(vminout.locs[i])
        if len(vminout.queuedline) > 0:
            for i in range(len(vminout.queuedline)):
                game_txt.insert("end", vminout.queuedline[i])
            game_txt.see("end")
            vminout.queuedline = []
        if len(vminout.queuedinstr) > 0:
            for i in range(len(vminout.queuedinstr)):
                instr_txt.insert("end", vminout.queuedinstr[i])
            instr_txt.see("end")
            vminout.queuedinstr = []
        time.sleep(delay)

def press_enter(event):
    # method to take contents of entry box and use as user input to the VM
    inp = userinp.get() + '\n'
    userinp.set('')
    vminout.queuedinstr.append(inp)
    vminout.inptr_auto, vminout.instr_auto = 0, inp

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Synacor Challenge VM/Debugger")
    wip, wregs, wipval, wregsval, wcount, wcounter = Any, [Any for _ in range(8)], tk.IntVar(), [tk.IntVar() for _ in range(8)], Any, tk.IntVar()
    codevals, codelocs, codes, locs = [tk.StringVar() for _ in range(8)], [tk.StringVar() for _ in range(8)], ["Not found" for _ in range(8)], ["Not found" for _ in range(8)]
    game_txt, instr_txt, wuserinp, userinp = Any, Any, Any, tk.StringVar()
    fspeed, ftrace, fusedips, ftest = Any, Any, Any, Any
    
    vminout = VMInOut("instr.txt")
    myvm = VM("challenge.bin", vminout, test=False, slow=False, usedips=False, trace=False)
    vminout.store_vm_ref(myvm)

    create_widgets()

    vmthread = threading.Thread(target = start_vm, args=(myvm,), daemon=True)
    vmthread.start()

    watching = threading.Thread(target = update_widgets, args=(0.1,), daemon=True)
    watching.start()
    root.bind('<Return>', press_enter)
    root.mainloop()
