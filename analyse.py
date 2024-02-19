import glob
import statistics
import json
import platform
import psutil
import platform
import subprocess
import re


algorithms = {}


def get_system_info():
    cpufreq = psutil.cpu_freq()
    cpuname = ""
    algorithms["system_info"] = {}

    command = "cat /proc/cpuinfo"
    all_info = subprocess.check_output(command, shell=True).decode().strip()
    for line in all_info.split("\n"):
        if "model name" in line:
            cpuname = re.sub(".*model name.*:", "", line, 1)

    algorithms["system_info"]["platform"] = platform.system()
    algorithms["system_info"]["platform-release"] = platform.release()
    algorithms["system_info"]["platform-version"] = platform.version()
    algorithms["system_info"]["architecture"] = platform.machine()
    algorithms["system_info"]["processor"] = cpuname
    algorithms["system_info"]["min_requency"] = f"{cpufreq.min:.2f}Mhz"
    algorithms["system_info"]["max_requency"] = f"{cpufreq.max:.2f}Mhz"
    algorithms["system_info"]["frequency_used"] = "3.6Mhz"
    algorithms["system_info"]["physical cores"] = psutil.cpu_count(logical=False)
    algorithms["system_info"]["total cores"] = psutil.cpu_count(logical=True)
    algorithms["system_info"][
        "ram"
    ] = f"{round(psutil.virtual_memory().total/1000000000, 2)} GB"


def parse_file(filename: str):
    functions = {}

    with open(filename, "r") as f:
        lines = map(lambda line: line.strip(), f.readlines())

    current_function = None
    for line in lines:
        if len(line) == 0:
            continue
        if line[-1] == ":":
            current_function = line[:-1]
            if current_function not in functions:
                functions[current_function] = []
            continue

        functions[current_function].append(int(line))
    return functions


def analyse(filename, functions):
    for function in functions:
        print(f"{function}:")
        print(f"Mean: {round(statistics.mean(functions[function]))}")
        print(f"Median: {round(statistics.median(functions[function]))}")
        print()
        if filename.replace("./results_", "") not in algorithms:
            algorithms[filename.replace("./results_", "")] = {}
        algorithms[filename.replace("./results_", "")][
            function.replace("xkem_", "").replace("gkem_", "")
        ] = round(statistics.mean(functions[function]))


if __name__ == "__main__":
    get_system_info()

    for filename in glob.iglob("./results_*"):
        functions = parse_file(filename)
        print(filename)
        analyse(filename, functions)

    with open("test_speed_results.json", "w") as write_file:
        json.dump(algorithms, write_file, indent=2)
