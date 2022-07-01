"""Running the simulation in the cinema environment."""
import statistics

import simpy
import random


class Theater:
    def __init__(self, env,
                 num_cashiers: int, num_servers: int, num_ushers: int):
        self.env = env
        self.cashier = simpy.Resource(self.env, num_cashiers)
        self.server = simpy.Resource(self.env, num_servers)
        self.usher = simpy.Resource(self.env, num_ushers)

    def purchase_ticket(self, moviegoer):
        rand_time = random.randint(1, 3)
        yield self.env.timeout(rand_time)

    def check_ticket(self, moviegoer):
        seconds = float(1) / 60
        rand_time = random.randint(2, 8) * seconds
        yield self.env.timeout(rand_time)

    def sell_food(self, moviegoer):
        rand_time = random.randint(1, 5)
        yield self.env.timeout(rand_time)


def go_to_movies(env, moviegoer, theater, wait_times):
    # Moviegoer arrives at the theater
    arrival_time = env.now

    with theater.cashier.request() as request:
        yield request
        yield env.process(theater.purchase_ticket(moviegoer))

    with theater.usher.request() as request:
        yield request
        yield env.process(theater.check_ticket(moviegoer))

    if random.choice([True, False]):
        with theater.server.request() as request:
            yield request
            yield env.process(theater.sell_food(moviegoer))

    # Moviegoer heads into the theater
    wait_times.append(env.now - arrival_time)


def run_theater(env, num_cashiers, num_servers, num_ushers, wait_times):
    theater = Theater(env, num_cashiers, num_servers, num_ushers)

    for moviegoer in range(3):
        env.process(go_to_movies(env, moviegoer, theater, wait_times))

    while True:
        yield env.timeout(0.20)  # Wait a bit before generating a new person

        moviegoer += 1
        env.process(go_to_movies(env, moviegoer, theater, wait_times))


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

    # Run the simulation
    env = simpy.Environment()
    env.process(run_theater(env, num_cashiers, num_servers, num_ushers, wait_times))
    env.run(until=90)

    # View the results
    mean_wait_time = get_average_wait_time(wait_times)
    print(
        "Running simulation...",
        f"\nThe average wait time is {mean_wait_time}.",
    )


if __name__ == '__main__':
    main()
