"""Running the simulation in the cinema environment."""
import statistics
import logging
import simpy
import random

logging.basicConfig(level=logging.DEBUG)


class Theater:
    def __init__(self, env,
                 num_cashiers: int, num_servers: int, num_ushers: int):
        self.env = env
        self.cashier = simpy.Resource(self.env, capacity=num_cashiers)
        self.server = simpy.Resource(self.env, capacity=num_servers)
        self.usher = simpy.Resource(self.env, capacity=num_ushers)

    def purchase_ticket(self, moviegoer):
        logging.debug(f"purchasing ticket")
        rand_time = random.randint(1, 3)
        yield self.env.timeout(rand_time)

    def check_ticket(self, moviegoer):
        logging.debug(f"checking ticket")
        seconds = float(1) / 60
        rand_time = random.randint(2, 8) * seconds
        yield self.env.timeout(rand_time)

    def sell_food(self, moviegoer):
        logging.debug(f"selling food")
        rand_time = random.randint(1, 5)
        yield self.env.timeout(rand_time)


def go_to_movies(env, moviegoer, theater, wait_times):
    # Moviegoer arrives at the theater
    arrival_time = env.now
    logging.info(f"Simulation ({moviegoer}) starting {arrival_time=}")

    with theater.cashier.request() as request:
        logging.debug(f"requesting cashier - ticket purchase")
        yield request
        logging.debug(f"purchasing ticket")
        logging.debug(f"{env.now=}")
        yield env.process(theater.purchase_ticket(moviegoer))

    with theater.usher.request() as request:
        logging.debug(f"requesting usher - check ticket")
        yield request
        logging.debug(f"checking ticket")
        yield env.process(theater.check_ticket(moviegoer))

    logging.debug(f"making choice - buy food or not")
    if random.choice([True, False]):
        with theater.server.request() as request:
            logging.debug(f"requesting server - buy food")
            yield request
            logging.debug(f"buying food")
            yield env.process(theater.sell_food(moviegoer))

    # Moviegoer heads into the theater
    complete_time = env.now
    wait_time = complete_time - arrival_time
    wait_times.append(wait_time)

    logging.debug(f"{complete_time=}")
    logging.info(f"{wait_time=}")


def run_theater(env, num_cashiers, num_servers, num_ushers, wait_times):
    logging.info("Running movie theater simulation")
    theater = Theater(env, num_cashiers, num_servers, num_ushers)

    # Create a process for each moviegoer
    for moviegoer in range(3):
        env.process(go_to_movies(env, moviegoer, theater, wait_times))

    while True:
        logging.debug("Waiting for next moviegoer")
        yield env.timeout(0.20)

        moviegoer += 1
        env.process(go_to_movies(env, moviegoer, theater, wait_times))


# Helper functions
def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    return average_wait


def calculate_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    # Pretty print the results
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)


def get_user_input():
    num_cashiers = input("Input # of cashiers working: ")
    num_servers = input("Input # of servers working: ")
    num_ushers = input("Input # of ushers working: ")
    params = [num_cashiers, num_servers, num_ushers]
    if all(str(i).isdigit() for i in params):  # Check input is valid
        params = [int(x) for x in params]
    else:
        print(
            "Could not parse input. The simulation will use default values:",
            "\n1 cashier, 1 server, 1 usher.",
        )
        params = [1, 1, 1]
    return params


def main():
    # Setup
    wait_times = []
    random.seed(42)
    num_cashiers, num_servers, num_ushers = get_user_input()

    logging.info(f"{num_cashiers=}")
    logging.info(f"{num_servers=}")
    logging.info(f"{num_ushers=}")

    # Run the simulation
    env = simpy.Environment()
    env.process(run_theater(env, num_cashiers, num_servers, num_ushers, wait_times))
    env.run(until=10)

    logging.info(f"{wait_times=}")

    # View the results
    mean_wait_time = get_average_wait_time(wait_times)
    print(
        "Running simulation...",
        f"\nThe average wait time is {mean_wait_time}.",
    )


if __name__ == '__main__':
    main()
