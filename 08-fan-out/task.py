import tower

def main():
    params = {
        "friend": "Brad",
        "foe": "Serhii"
    }

    run = tower.run_app("hello-world", parameters=params)
    tower.wait_for_run(run)

if __name__ == "__main__":
    main()
