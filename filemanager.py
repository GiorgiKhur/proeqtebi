class Node:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent


class File(Node):
    def __init__(self, name, parent=None, content=""):
        super().__init__(name, parent)
        self.content = content

    def get_size(self):
        return len(self.content)


class Directory(Node):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.children = {}

    def get_size(self):

        total = 0
        for child in self.children.values():
            total += child.get_size()
        return total


class FileSystem:
    def __init__(self):
        self.root = Directory("/")
        self.current = self.root

    def pwd(self):
        if self.current == self.root:
            return "/"
        path = []
        temp = self.current
        while temp and temp.name != "/":
            path.append(temp.name)
            temp = temp.parent
        return "/" + "/".join(reversed(path))

    def mkdir(self, name):
        if name in self.current.children:
            print(f"Error: '{name}' already exists.")
            return
        new_dir = Directory(name, self.current)
        self.current.children[name] = new_dir

    def create_file(self, name):
        if name in self.current.children:
            print(f"Error: '{name}' already exists.")
            return
        content = input(f"Enter content for {name}: ")
        new_file = File(name, self.current, content)
        self.current.children[name] = new_file

    def ls(self):
        if not self.current.children:
            print("(Empty Directory)")
        for name, node in self.current.children.items():
            suffix = "/" if isinstance(node, Directory) else ""
            print(f"{node.get_size()}\t {name}{suffix}")

    def cd(self, name):
        if name == "..":
            if self.current.parent:
                self.current = self.current.parent
            return
        if name == "/":
            self.current = self.root
            return

        if name in self.current.children:
            target = self.current.children[name]
            if isinstance(target, Directory):
                self.current = target
            else:
                print(f"Error: '{name}' is a file, not a directory.")
        else:
            print(f"Error: Directory '{name}' not found.")

    def rm(self, name):
        if name in self.current.children:
            del self.current.children[name]
        else:
            print(f"Error: '{name}' not found.")


def run_sim():
    fs = FileSystem()
    print("--- File System Simulator ---")
    print("Commands: mkdir [name], touch [name], ls, cd [name], pwd, rm [name], size, exit")

    while True:
        try:
            cmd_input = input(f"FS_Sim:{fs.pwd()}$ ").strip().split()
            if not cmd_input: continue

            cmd = cmd_input[0].lower()
            args = cmd_input[1:] if len(cmd_input) > 1 else []

            if cmd == "exit":
                break
            elif cmd == "mkdir" and args:
                fs.mkdir(args[0])
            elif cmd == "touch" and args:
                fs.create_file(args[0])
            elif cmd == "ls":
                fs.ls()
            elif cmd == "cd" and args:
                fs.cd(args[0])
            elif cmd == "pwd":
                print(fs.pwd())
            elif cmd == "rm" and args:
                fs.rm(args[0])
            elif cmd == "size":
                print(f"Total Directory Size: {fs.current.get_size()} bytes")
            else:
                print("Unknown command or missing arguments.")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    run_sim()