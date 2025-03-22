import subprocess
import requests
import csv


def run_database_builder():
    try:

        result = subprocess.run(["python", "database_builder.py"], check=True, capture_output=True, text=True)
        print("Sortie standard :")
        print(result.stdout)
        print("Sortie d'erreur (le cas échéant) :")
        print(result.stderr)
    except subprocess.CalledProcessError as e:
        print("Une erreur est survenue lors de l'exécution de database_builder.py")
        print(e)

def run_bot_script():
    try:

        result = subprocess.run(["python", "bot_script.py"],
                                check=True,
                                capture_output=True,
                                text=True)
        print("Sortie standard :")
        print(result.stdout)
        print("Sortie d'erreur :")
        print(result.stderr)
    except subprocess.CalledProcessError as e:
        print("Une erreur est survenue lors de l'exécution de bot_script.py")
        print(e)


if __name__ == "__main__":

    if(run_bot_script()):
        run_database_builder()

