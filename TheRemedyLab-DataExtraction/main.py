import os
import subprocess

def main():
    # Change directory
    target_dir = r"D:\TheRemedyLab\TheRemedyLab-DataExtraction\DataCollectionAndStructuring"
    os.chdir(target_dir)

    # Run Streamlit app
    try:
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")

if __name__ == "__main__":
    main()
