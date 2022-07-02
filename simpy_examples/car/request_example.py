import simpy


def car(env, name, bcs, driving_time, charge_duration):
    # Simulate driving to the BCS
    yield env.timeout(driving_time)

    # Request one of its charging spots
    print('%s arriving at %d' % (name, env.now))
    with bcs.request() as req:
        yield req

        # Charge the battery
        print('%s starting to charge at %s' % (name, env.now))
        yield env.timeout(charge_duration)
        print('%s leaving the bcs at %s' % (name, env.now))


def main():
    env = simpy.Environment()
    bcs = simpy.Resource(env, capacity=2)

    for i in range(4):
        env.process(car(env,
                        name=f'Car {i}',
                        bcs=bcs,
                        driving_time=i * 2,
                        charge_duration=5
                        ))

    env.run()


if __name__ == "__main__":
    main()
