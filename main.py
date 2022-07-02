"""
Cinema visit simulation models customer waiting times

Scenario:
    customers ;
    - randomly arrive at the cinema
    - request a ticket desk vendors to buy a ticket
    - request a concession stand servers to buy food and/or drink
    - request an usher to check their ticket and enter the film
    - complete their front of house visit
"""

# TODO: Add parameters to module docstring

import itertools
import numpy as np
from pprint import pprint
import logging
import simpy

RANDOM_SEED = 42
TIME_INTERVAL = 165  # Average time interval between customer arrivals (seconds)
SIM_TIME = 60 * 60 * 12  # Simulation time in seconds


def customer(counter, env, ticket_desk, concession_stand, ushers):
    """
    Simulate a customer process from arrival to entering the movie screen.
    """

    global customer_records

    process_record = {}
    process_start = env.now
    customer_name = f'customer {counter}'
    logging.info(f'{customer_name} arriving at cinema at {process_start:.1f}')

    # TODO: Factory for DRY
    # BUY A TICKET
    with ticket_desk.request() as req:
        req_name = 'ticket_desk'
        process_record[req_name] = {}
        req_start = env.now

        # Request one of the ticket desks
        yield req

        # The purchase process takes some time
        req_duration = max(1, np.random.normal(loc=90, scale=45))
        yield env.timeout(req_duration)

        req_end = env.now
        req_duration = req_end - req_start
        logging.info(f'{customer_name} finished {req_name} in {req_duration: .1f} seconds.')

        for variable in ['req_start', 'req_end', 'req_duration']:
            process_record[req_name][variable] = eval(variable)

    # Choose to buy confectionery
    if np.random.choice([True, False]):
        with concession_stand.request() as req:
            req_name = 'concession'
            process_record[req_name] = {}
            req_start = env.now

            # Request one of the ticket desks
            yield req

            # The purchase process takes some time
            req_duration = max(1, np.random.gamma(shape=3, scale=60))
            yield env.timeout(req_duration)

            req_end = env.now
            req_duration = req_end - req_start
            logging.info(f'{customer_name} finished {req_name} in {req_duration: .1f} seconds.')

            for variable in ['req_start', 'req_end', 'req_duration']:
                process_record[req_name][variable] = eval(variable)

    # CHECK TICKETS
    with ushers.request() as req:
        req_name = 'ushers'
        process_record[req_name] = {}
        req_start = env.now

        # Request one of the ticket desks
        yield req

        # The purchase process takes some time
        req_duration = 5
        yield env.timeout(req_duration)

        req_end = env.now
        req_duration = req_end - req_start
        logging.info(f'{customer_name} finished {req_name} in {req_duration: .1f} seconds.')

        for variable in ['req_start', 'req_end', 'req_duration']:
            process_record[req_name][variable] = eval(variable)

    process_end = env.now
    process_duration = process_end - process_start

    # Record process data
    process_record = dict(
        **process_record,
        **dict(
            id=counter,
            start_time=process_start,
            end_time=process_end,
            duration=process_duration,
        ))
    customer_records.append(process_record)


def customer_generator(env, **resources):
    """Generate new customers who arrive at the cinema."""
    for i in itertools.count():
        counter = i + 1
        # Time before another customer arrives
        arrival = np.random.exponential(TIME_INTERVAL)
        yield env.timeout(arrival)

        # Start new process
        env.process(customer(counter, env=env, **resources))


def run_simulation(capacities):
    """Setup and start the simulation."""

    global customer_records

    np.random.seed(RANDOM_SEED)

    # Holds all data about simulation
    customer_records = []

    # Create environment and start processes
    env = simpy.Environment()
    logging.info(f'Cinema sim starting at {env.now}')
    resources = dict(
        ticket_desk=simpy.Resource(env, capacity=capacities['ticket_desk']),
        concession_stand=simpy.Resource(env, capacity=capacities['concession_stand']),
        ushers=simpy.Resource(env, capacity=capacities['ushers']),
    )

    env.process(customer_generator(env, **resources))

    # Execute!
    env.run(until=SIM_TIME)

    return customer_records


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('numexpr').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    run_stats = {}  # Simulation info (totals etc.)
    customer_records = []  # Customer level simulation info

    resource_capacities = dict(
        ticket_desk=1,
        concession_stand=2,
        ushers=1,
    )
    sim_data = run_simulation(resource_capacities)
    pprint(sim_data)

    # Process simulation data
    num_customers = len(sim_data)
    wait_times = [i['duration'] for i in sim_data]
    mean = np.mean(wait_times)
    sigma = np.std(wait_times)
    print(f'{num_customers=}')
    print(f'{mean=}')

    import seaborn as sns
    import matplotlib.pyplot as plt

    sns.displot(x=wait_times, )
    plt.show()

    import scipy.stats as stats

    # Probability customers will wait longer than threshold
    x = 10 * 60  # 10 minutes
    p_value = 1 - stats.norm.cdf(x, mean, sigma)
    print(f'{p_value=}')
