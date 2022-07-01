import simpy


class Car(object):
    def __init__(self, env):
        self.env = env
        # Start the run process everytime an instance is created.
        self.action = env.process(self.run())

    def run(self):
        while True:  # Loop until env.run(until)
            print('Start parking and charging at %d' % self.env.now)
            charge_duration = 5
            # We yield the process that process() returns to wait for it to finish
            try:
                yield self.env.process(self.charge(charge_duration))
            except simpy.Interrupt:
                print("Charging was interrupted, I hope the battery is full enough!")

            # The charge process has finished, and we can start driving again.
            print('Start driving at %d' % self.env.now)
            trip_duration = 2
            yield self.env.timeout(trip_duration)

    def charge(self, duration):
        yield self.env.timeout(duration)


def driver(env, car):
    """A driver who might interrupt the charging process."""
    yield env.timeout(3)
    car.action.interrupt()


def main():
    env = simpy.Environment()
    car = Car(env)
    env.process(driver(env, car))
    env.run(until=15)


if __name__ == "__main__":
    main()
