from tkinter import *
from tkinter.scrolledtext import ScrolledText
from functools import partial
from tkinter import filedialog
import subprocess
import os

"""
    Brainfuck Compiler
    Created by Polybagel
"""

###a list of valid brainfuck commands###
valid_commands = "><+-.,[]"

###allowed file formats###
files = [('Brainfuck source file', '*.bf')]
ex = [('Excecutable file', '*.exe')]

###generates a .bat file containing the generated command to compile the c source with gcc.###
def generate_compile_batch(command):
    f=open("compile.bat","w")
    f.write(command)
    f.close()

    subprocess.call([r'compile.bat'])
    os.remove("compile.bat")

def save_code(code):
    got = code.get("1.0",'end-1c')
    f = filedialog.asksaveasfile(mode='w', filetypes = files, defaultextension=".bf")
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    text2save = got
    f.write(text2save)
    f.close() #create the c file

"""
    this function is a little more complicated.

    firstly, it asks for the file destination to put the exe.
    next, it generates the gcc command to compile the c source.
    and finally, it generates a .bat file containing the command, because subprocess for some reason did not want to cooperate.

    after all that is done, it removes the c source and batch file, leaving just the exe.
"""
def output_code(code):
    f = filedialog.asksaveasfile(mode='w', defaultextension=".c")
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    text2save = code
    f.write(text2save)
    f.close() #create the c file

    ###compile the c program###
    command = "gcc \""+f.name+"\" -o \""+f.name[0:len(f.name)-2]+"\""

    generate_compile_batch(command)

    os.remove(f.name)

###removes unsupported characters, blank lines, and formats it correctly.###
def cleanup_bf_code(bf_code):
    lines = bf_code.split("\n")

    result = ""

    for line in lines:
        ###test 1, is the line empty?
        if line == "":
            print("line empty!")
        else:
            ###step 2, cleanup the line itself
            cleanLine = ""
            for char in line:
                if char in valid_commands:
                    cleanLine+=char
                    
            result+=cleanLine

    return result

###takes the raw brainfuck code, cleans it, and converts it into C code.###
def generate_c_code(bf_code, memorySize):
    result = ""
    cleanedCode = cleanup_bf_code(bf_code)

    ###add header text###
    result+="""
/*
    C code generated by the Brainfuck compiler, created by Polybagel
*/\n\n"""

    ###add stdio.h include###
    result+="#include <stdio.h>\n\n"

    ###add int main()###
    result+="int main () \n{\n"

    ###create memory buffer stack with a set amount of ram, the typical size is 30,000 cells.###
    result+="      //create a memory buffer\n      int memory["+str(memorySize)+"];\nfor(int i = 0; i < "+str(memorySize)+"; i++){\nmemory[i]=0;\n}\n      int memPointer = 0;\n\n"

    ###replace brainfuck commands with C equivalants###






    previousCommand = "none"
    for i in range(len(cleanedCode)):
        command = cleanedCode[i]

        if not command == previousCommand:
            previousCommand = command
            commandRepeats = 0
            search = 1

            lastCommand = command
            while True:
                try:
                    if cleanedCode[i+search] == command:
                        search+=1
                        commandRepeats+=1
                    else:
                        break
                except:
                    ###we are at the last character of the code, break!
                    break
            
            if command == "<":
                result+="            memPointer-="+str(commandRepeats+1)+";\n"
            elif command == ">":
                result+="            memPointer+="+str(commandRepeats+1)+";\n"
            elif command == "+":
                result+="            memory[memPointer]+="+str(commandRepeats+1)+";\n"
            elif command == "-":
                result+="            memory[memPointer]-="+str(commandRepeats+1)+";\n"
                
        if command == ".":
            result+="            putchar(memory[memPointer]);\n"
        elif command == ",":
            result+="            memory[memPointer] = getchar();\n"
        elif command == "[":
            result+="\n      while(memory[memPointer] != 0)\n      {\n"
        elif command == "]":
            result+="}\n"






            
    
    ###add the final return 0 and '}' character###
    result+="\ngetchar();\nreturn 0;\n}"

    print(result)
    output_code(result)
    return result

###boilerplate tkinter code###
root = Tk()
root.title('Brainfuck Compiler v1.0.0')

###menu bar functions###
def load_code():
    f = filedialog.askopenfile(mode='r', filetypes = files, defaultextension=".bf")
    content = f.readlines()

    combined = ""

    for line in content:
        combined+=line

    code.delete(1.0,"end")
    code.insert(1.0, combined)

def new_code():
    code.delete(1.0,"end")

def client_exit():
    exit()

def compile_code(c):
    bf_code = c.get("1.0",'end-1c')
    generate_c_code(bf_code,30000)
    return 0

def about():
    filewin = Toplevel(root)
    filewin.geometry("320x240")
    filewin.title('About the Brainfuck compiler')
   
    label = Label(filewin, wraplength=250, text="The Brainfuck compiler is designed to take brainfuck source code, convert it to C code, and compile it into an .exe file using gcc.\n\nCreated by Polybagel")
    label.grid(row=0,column=0,padx=25,pady=10)

def tutorial():
    filewin = Toplevel(root)
    filewin.geometry("320x240")
    filewin.title('How to use the Brainfuck compiler')
   
    label = Label(filewin, wraplength=250, text="Upon opening the Brainfuck compiler, you can simply paste brainfuck source code into the text box.\n\nIf you want to save your code, simply go to File->Save, and select the file destination.\n\nIf you want to compile your code into an exe, go to File->Compile, and choose a file destination for the exe.\n\nTo open a source file, go to File->Open, and select the file to open.")
    label.grid(row=0,column=0,padx=25,pady=10)

###main code###
code = ScrolledText(root)
code.pack(side=TOP, fill=BOTH, expand=YES, padx=10, pady=10)

compile_code = partial(compile_code, code)
save_code = partial(save_code, code)
###main code###

###menubar###
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=new_code)
filemenu.add_command(label="Compile", command=compile_code)
filemenu.add_command(label="Save", command=save_code)
filemenu.add_command(label="Open", command=load_code)

filemenu.add_separator()

filemenu.add_command(label="Exit", command=client_exit)
menubar.add_cascade(label="File", menu=filemenu)
editmenu = Menu(menubar, tearoff=0)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About...", command=about)
helpmenu.add_command(label="How to use...", command=tutorial)
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)
root.mainloop()


