import os
import json 
import shutil 
from subprocess import PIPE, run 
import sys



GAME_DIR_PATTERN = "game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]

def make_executable(filepath):
    current_permissions = os.stat(filepath).st_mode
    os.chmod(filepath, current_permissions | 0o111)


def find_all_game_paths(source):
   #print(f"Searching in: {source}")
    game_paths = []
    for root, dirs, files in os.walk(source):
       # print(f"Examining directory: {root}")
       # print(f"Subdirectories: {dirs}")
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)
                #print(f"Found game directory: {path}")
        break
    #print(f"Game paths found: {game_paths}")
    return game_paths



def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)

    return new_names



def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)



def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source, dest)



def make_json_metadata_file(path, game_dirs):
    data = {
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs) 
    }
    with open(path, "w") as f:
        json.dump(data, f)


def compile_game_code(path):
    code_file_name = None 
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file 
                break
        break

    if code_file_name is None:
        return 

    executable_name = code_file_name[:-3]

    command = GAME_COMPILE_COMMAND + ["-o", executable_name, code_file_name]
    try:
        result = run_command(command, path)
        print(f"Compiled {code_file_name} to {executable_name}")
        print("Compilation result:", result)

        # Make the compiled file executable
        executable_path = os.path.join(path, executable_name)
        make_executable(executable_path)
        print(f"Made {executable_name} executable")
    except Exception as e:
        print(f"Error compiling {code_file_name}: {str(e)}")

def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)
    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("compile result:", result)
    os.chdir(cwd)
    return result


def main(source, target):
    cwd = os.getcwd()
    source_path = os.path.join(cwd, source)
    target_path = os.path.join(cwd, target)
    print(f"Source path: {source_path}")
    game_paths = find_all_game_paths(source_path)
    print("Game paths found:")
    for path in game_paths:
        print(path)
    new_game_dirs = get_name_from_paths(game_paths, "_game")
    print(new_game_dirs)

    create_dir(target_path)

    for src, dest in zip(game_paths, new_game_dirs):
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path)

    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)



if __name__ == "__main__":
    args = sys.argv
    if len(args) !=3:
        raise Exception("You must pass a source and target directory - only.")

    source, target = args[1:]
    main(source, target)
