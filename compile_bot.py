import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("bot_path", help="path to the bot you want to compile", type=str)
args = parser.parse_args()
path = args.bot_path
compile_path = path + '_to_compile'

print('Compiling:')
print('   ' + path)
print('into:')
print('   ' + compile_path)
print('files:')
files = []
for rel_path, j, y in os.walk('./' + path):
    for py_file in y:
        files.append(rel_path + '/' + py_file)

# files = [x for x in reversed(files)]
for file in files:
    print('   ' + file)

print('creating the robot folder')
os.makedirs('./' + compile_path, exist_ok=True)
print('   ./' + compile_path)

print('joining them...')

call_0 = "echo \# > ./{}/_aux.py".format(compile_path)
os.system(call_0)
# os.wait()
# print(call_0)

for i, file in enumerate(files):
    call_1 = "cat {} > ./{}/robot.py ./{}/_aux.py".format(file, compile_path, compile_path)
    call_2 = "cp ./{}/robot.py ./{}/_aux.py".format(compile_path, compile_path)
    # print(call_1)
    # print(call_2)
    os.system(call_1)
    # os.wait()
    os.system(call_2)
    # os.wait()

call_3 = "rm -f ./{}/_aux.py".format(compile_path)
os.system(call_3)
# os.wait()
# print(call_3)

# print('Compiling the bot')
# call_4 = "".format(compile_path)
# os.system(call_4)
# # os.wait()
# # print(call_4)
print('   done')
print("Fixing Imports")

robot_file = "./{}/robot.py".format(compile_path)
# Read in the file
with open(robot_file, 'r') as file:
    filedata = file.read()

# Replace the target string
filedata = filedata.replace('\nimport', '\n# import')
filedata = filedata.replace('\nfrom', '\n# from')
filedata = 'import random\n' + filedata
filedata = 'import battlecode as bc\n' + filedata
filedata = 'from battlecode import BCAbstractRobot, SPECS\n' + filedata

# Write the file out again
with open(robot_file, 'w') as file:
    file.write(filedata)

print('   done')
